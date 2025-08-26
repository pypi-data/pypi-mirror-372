from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import random
import time
from typing import Dict, Any

import requests
from flask import Blueprint, request, jsonify
from cryptography.fernet import Fernet
from loguru import logger

omni_bp = Blueprint('omni', __name__)

# Encryption key derived from the password
ENCRYPTION_PASSWORD = "media-agent-mcp!@123"

# Fault-tolerance settings
DEFAULT_TIMEOUT = 20  # seconds per HTTP request
RETRY_STATUS_CODES = {500, 502, 503, 504}
MAX_HTTP_RETRIES = 3
BACKOFF_FACTOR = 1.8
MAX_JITTER = 0.3  # seconds jitter added to backoff


def _get_encryption_key() -> bytes:
    """
    Generate encryption key from password.
    
    Returns:
        bytes: Fernet encryption key
    """
    # Use SHA256 to create a consistent 32-byte key from password
    key_hash = hashlib.sha256(ENCRYPTION_PASSWORD.encode()).digest()
    # Fernet requires base64-encoded 32-byte key
    return base64.urlsafe_b64encode(key_hash)


def decrypt_credentials(encrypted_ak: str, encrypted_sk: str) -> tuple[str, str]:
    """
    Decrypt AK and SK using the encryption password.
    
    Args:
        encrypted_ak: Base64 encoded encrypted access key
        encrypted_sk: Base64 encoded encrypted secret key
    
    Returns:
        tuple: Decrypted (ak, sk) pair
    """
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        
        # Decode and decrypt
        ak = fernet.decrypt(encrypted_ak.encode()).decode()
        sk = fernet.decrypt(encrypted_sk.encode()).decode()
        
        return ak, sk
    except Exception as e:
        logger.error(f"Failed to decrypt credentials: {e}")
        raise ValueError("Invalid encrypted credentials")


def _sleep_with_backoff(attempt: int) -> None:
    """
    Sleep with exponential backoff and jitter.
    
    Args:
        attempt: Current attempt number (0-based)
    """
    backoff_time = BACKOFF_FACTOR ** attempt
    jitter = random.uniform(0, MAX_JITTER)
    time.sleep(backoff_time + jitter)


def _post_json_with_retry(url: str, *, params: Dict[str, Any], headers: Dict[str, str], json_body: Dict[str, Any],
                          timeout: int = DEFAULT_TIMEOUT, max_retries: int = MAX_HTTP_RETRIES) -> Dict[str, Any]:
    """
    Args:
        url: Target request URL
        params: Query parameters appended to URL
        headers: HTTP headers
        json_body: JSON body payload
        timeout: Per-request timeout in seconds
        max_retries: Max number of retries on transient errors
    
    Returns:
        result: Parsed JSON dictionary from the response
    """
    last_err = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, params=params, headers=headers, json=json_body, timeout=timeout)
            # Retry on 5xx
            if resp.status_code in RETRY_STATUS_CODES and attempt < max_retries:
                _sleep_with_backoff(attempt)
                continue
            resp.raise_for_status()
            try:
                return resp.json()
            except ValueError as ve:
                # Non-JSON response
                last_err = ve
                if attempt < max_retries:
                    _sleep_with_backoff(attempt)
                    continue
                raise
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as e:
            last_err = e
            if attempt < max_retries:
                _sleep_with_backoff(attempt)
                continue
            raise
    
    # Should not reach here, but just in case
    if last_err:
        raise last_err
    raise Exception("Unexpected error in retry logic")


def _generate_signature(nonce: int, timestamp: int, security_key: str) -> str:
    """
    Generates a signature for the API request.
    
    Args:
        nonce: Random nonce value
        timestamp: Unix timestamp
        security_key: Security key for signing
    
    Returns:
        result: Generated signature
    """
    keys = [str(nonce), str(security_key), str(timestamp)]
    keys.sort()
    key_str = "".join(keys).encode("utf-8")
    signature = hashlib.sha1(key_str).hexdigest()
    return signature.lower()


def _submit_task(image_url: str, audio_url: str, api_key: str, security_key: str) -> str:
    """
    Submits a video generation task.
    
    Args:
        image_url: URL of the input image
        audio_url: URL of the input audio
        api_key: API access key
        security_key: Security key for signing
    
    Returns:
        result: Task ID for the submitted task
    """
    submit_task_url = "https://cv-api.bytedance.com/api/common/v2/submit_task"
    timestamp = int(time.time())
    nonce = random.randint(0, (1 << 31) - 1)
    signature = _generate_signature(nonce, timestamp, security_key)

    params = {
        "api_key": api_key,
        "timestamp": str(timestamp),
        "nonce": str(nonce),
        "sign": signature,
    }
    headers = {"Content-Type": "application/json"}
    body = {
        "req_key": "realman_avatar_picture_omni_v2",
        "image_url": image_url,
        "audio_url": audio_url,
    }

    data = _post_json_with_retry(
        submit_task_url,
        params=params,
        headers=headers,
        json_body=body,
    )
    if data.get("code") != 10000:
        raise Exception(f"Failed to submit task: {data.get('message', 'unknown error')} (code={data.get('code')})")
    return data["data"]["task_id"]


def _get_task_result(task_id: str, api_key: str, security_key: str) -> Dict[str, Any]:
    """
    Gets the result of a video generation task.
    
    Args:
        task_id: ID of the task to check
        api_key: API access key
        security_key: Security key for signing
    
    Returns:
        result: Task result data
    """
    get_result_url = "https://cv-api.bytedance.com/api/common/v2/get_result"
    timestamp = int(time.time())
    nonce = random.randint(0, (1 << 31) - 1)
    signature = _generate_signature(nonce, timestamp, security_key)

    params = {
        "api_key": api_key,
        "timestamp": str(timestamp),
        "nonce": str(nonce),
        "sign": signature,
    }
    headers = {"Content-Type": "application/json"}
    body = {
        "req_key": "realman_avatar_picture_omni_v2",
        "task_id": task_id,
    }

    return _post_json_with_retry(
        get_result_url,
        params=params,
        headers=headers,
        json_body=body,
    )


def generate_video_from_omni_human(image_url: str, audio_url: str, api_key: str, security_key: str) -> str:
    """
    Generates a video from an image and audio using the Omni Human API.

    Args:
        image_url: The URL of the portrait image
        audio_url: The URL of the audio
        api_key: API access key
        security_key: Security key for signing

    Returns:
        result: The URL of the generated video
    """
    # Submit task with retry already handled inside _submit_task
    logger.info(f'Received request to generate video from Omni Human API {image_url}, {audio_url}')
    task_id = _submit_task(image_url, audio_url, api_key, security_key)
    logger.info(f"Submitted Omni Human task, task_id={task_id}")

    # Poll for result with an overall timeout
    poll_interval = 5  # seconds
    max_wait_seconds = 20 * 60  # 20 minutes
    start_ts = time.time()
    last_message = None

    while True:
        # If overall timeout exceeded, abort
        if time.time() - start_ts > max_wait_seconds:
            raise TimeoutError(
                f"Timed out after {max_wait_seconds}s waiting for Omni Human task to complete. "
                f"Last status: {last_message}"
            )

        try:
            result = _get_task_result(task_id, api_key, security_key)
            logger.info(f"Polled Omni Human task result: {json.dumps(result)}")
        except Exception as e:
            # Transient errors from _post_json_with_retry are already retried; if still failing, wait and continue
            last_message = str(e)
            time.sleep(poll_interval)
            continue

        code = result.get("code")
        if code == 10000:
            # Success
            data = result.get("data", {})
            video_url = data.get("video_url")
            if video_url:
                return video_url
            else:
                raise Exception(f"No video URL in successful response, {data}")
        elif code == 10001:
            # Still processing
            last_message = result.get("message", "Processing...")
            time.sleep(poll_interval)
        else:
            # Error
            error_msg = result.get("message", "Unknown error")
            raise Exception(f"Omni Human API error: {error_msg} (code={code})")


@omni_bp.route('/omni/generate', methods=['POST'])
def omni_generate():
    """
    Generate video using Omni Human API with encrypted credentials.
    
    Expected JSON body:
    {
        "encrypted_ak": "base64_encoded_encrypted_access_key",
        "encrypted_sk": "base64_encoded_encrypted_secret_key",
        "image_url": "https://example.com/image.jpg",
        "audio_url": "https://example.com/audio.mp3"
    }
    
    Returns:
        JSON response with video generation result
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "data": None,
                "message": "No JSON data provided"
            }), 400
        
        # Extract required fields
        encrypted_ak = data.get('encrypted_ak')
        encrypted_sk = data.get('encrypted_sk')
        image_url = data.get('image_url')
        audio_url = data.get('audio_url')
        
        if not all([encrypted_ak, encrypted_sk, image_url, audio_url]):
            return jsonify({
                "status": "error",
                "data": None,
                "message": "Missing required fields: encrypted_ak, encrypted_sk, image_url, audio_url"
            }), 400
        
        # Decrypt credentials
        try:
            api_key, security_key = decrypt_credentials(encrypted_ak, encrypted_sk)
            logger.info(f'Decrypted credentials successfully')
        except ValueError as e:
            return jsonify({
                "status": "error",
                "data": None,
                "message": str(e)
            }), 400
        
        # Generate video
        video_url = generate_video_from_omni_human(image_url, audio_url, api_key, security_key)
        
        return jsonify({
            "status": "success",
            "data": {"video_url": video_url},
            "message": "Video generated successfully"
        })
        
    except Exception as e:
        logger.error(f"Error in omni_generate: {str(e)}")
        return jsonify({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        }), 500