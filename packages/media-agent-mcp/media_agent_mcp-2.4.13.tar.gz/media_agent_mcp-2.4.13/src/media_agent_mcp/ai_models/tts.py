import base64
import json
import os
import requests
import datetime
import uuid
import tos
from media_agent_mcp.storage.tos_client import get_tos_client

def tts(text: str, speaker_id: str):
    app_id = os.environ.get("TTS_APP_KEY")
    access_key = os.environ.get("TTS_ACCESS_KEY")
    resource_id = os.environ.get("RESOURCE_ID", "volc.service_type.1000009")
    speaker = speaker_id

    if not app_id or not access_key or not resource_id:
        return None

    url = "https://voice.ap-southeast-1.bytepluses.com/api/v3/tts/unidirectional"

    headers = {
        "X-Api-App-Id": app_id,
        "X-Api-Access-Key": access_key,
        "X-Api-Resource-Id": resource_id,
        "X-Api-App-Key": "aGjiRDfUWi",
        "Content-Type": "application/json",
        "Connection": "keep-alive"
    }

    additions = {
        "disable_markdown_filter": True,
        "enable_language_detector": True,
        "enable_latex_tn": True,
        "disable_default_bit_rate": True,
        "max_length_to_filter_parenthesis": 0,
        "cache_config": {
            "text_type": 1,
            "use_cache": True
        }
    }

    additions_json = json.dumps(additions)

    payload = {
        "user": {"uid": "12345"},
        "req_params": {
            "text": text,
            "speaker": speaker,
            "additions": additions_json,
            "audio_params": {
                "format": "mp3",
                "sample_rate": 24000
            }
        }
    }
    session = requests.Session()
    response = None
    try:
        response = session.post(url, headers=headers, json=payload, stream=True)

        audio_data = bytearray()
        for chunk in response.iter_lines(decode_unicode=True):
            if not chunk:
                continue
            data = json.loads(chunk)
            if data.get("code", 0) == 0 and "data" in data and data["data"]:
                chunk_audio = base64.b64decode(data["data"])
                audio_data.extend(chunk_audio)
            if data.get("code", 0) == 20000000:
                break
            if data.get("code", 0) > 0:
                print(f"error response:{data}")
                break

        # Directly upload bytes to TOS
        try:
            client = get_tos_client()
            bucket_name = os.getenv('TOS_BUCKET_NAME')

            if not bucket_name:
                print("TOS_BUCKET_NAME environment variable must be set")
                return None

            # Generate a unique object key
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            object_key = f"media_agent/{date_str}/{uuid.uuid4().hex}.mp3"

            client.put_object(bucket_name, object_key, content=bytes(audio_data))

            # Construct the URL
            endpoint = os.getenv('TOS_ENDPOINT', "tos-ap-southeast-1.bytepluses.com")
            file_url = f"https://{bucket_name}.{endpoint}/{object_key}"
            return file_url
        except Exception as e:
            print(f"Error uploading audio to TOS: {e}")
            return None

    except Exception as e:
        print(f"request error: {e}")
        return None
    finally:
        if response:
            response.close()
        session.close()


if __name__ == '__main__':
    text = "欢迎使用字节跳动语音合成服务。"
    speaker_id = "zh_female_shaoergushi_mars_bigtts"
    result = tts(text, speaker_id)
    print(result)