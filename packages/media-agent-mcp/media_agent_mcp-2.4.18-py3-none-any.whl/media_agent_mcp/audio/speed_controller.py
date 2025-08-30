import io
import math
import os
import tempfile
import requests
from pydub import AudioSegment
from media_agent_mcp.storage.tos_client import get_tos_client
import datetime
import uuid
from loguru import logger


def speed_up_audio_if_needed(audio_url: str, target_duration: int = 12) -> dict:
    """
    Speed up audio if it exceeds target duration to fit within the limit.
    
    Args:
        audio_url: URL of the audio file to process
        target_duration: Maximum duration in seconds (default: 12)
    
    Returns:
        result: Dictionary containing processed audio_url and duration_seconds
    """
    try:
        # Download audio from URL
        logger.info(f'Speed up audio to 12s, {audio_url}')
        response = requests.get(audio_url)
        response.raise_for_status()
        
        # Load audio using pydub
        audio = AudioSegment.from_file(io.BytesIO(response.content))
        
        # Get current duration in seconds
        current_duration = len(audio) / 1000.0
        
        # If audio is within target duration, return original
        if current_duration <= target_duration:
            return {
                "audio_url": audio_url,
                "duration_seconds": math.ceil(current_duration)
            }
        
        # Calculate speed factor to fit within target duration
        speed_factor = current_duration / target_duration
        
        # Speed up audio
        speeded_audio = audio.speedup(playback_speed=speed_factor)
        
        # Export to bytes
        output_buffer = io.BytesIO()
        speeded_audio.export(output_buffer, format="mp3")
        audio_data = output_buffer.getvalue()
        
        # Upload processed audio to TOS
        client = get_tos_client()
        bucket_name = os.getenv('TOS_BUCKET_NAME')
        
        if not bucket_name:
            raise Exception("TOS_BUCKET_NAME environment variable must be set")
        
        # Generate unique object key
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        object_key = f"media_agent/{date_str}/{uuid.uuid4().hex}_speeded.mp3"
        
        # Upload to TOS
        client.put_object(bucket_name, object_key, content=audio_data)
        
        # Construct URL
        endpoint = os.getenv('TOS_ENDPOINT', "tos-ap-southeast-1.bytepluses.com")
        processed_url = f"https://{bucket_name}.{endpoint}/{object_key}"
        
        return {
            "audio_url": processed_url,
            "duration_seconds": target_duration
        }
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        # Return original URL if processing fails
        return {
            "audio_url": audio_url,
            "duration_seconds": math.ceil(current_duration) if 'current_duration' in locals() else 12
        }


def process_tts_result(tts_result: dict, target_duration: int = 12) -> dict:
    """
    Process TTS result and apply speed control if needed.
    
    Args:
        tts_result: Result from TTS function containing audio_url and duration_seconds
        target_duration: Maximum duration in seconds (default: 12)
    
    Returns:
        result: Dictionary containing processed audio_url and duration_seconds
    """
    if not isinstance(tts_result, dict) or 'audio_url' not in tts_result:
        return tts_result
    
    audio_url = tts_result['audio_url']
    duration = tts_result.get('duration_seconds', 0)
    
    # If duration is within limit, return as is
    if duration <= target_duration:
        return tts_result
    
    # Apply speed control
    return speed_up_audio_if_needed(audio_url, target_duration)