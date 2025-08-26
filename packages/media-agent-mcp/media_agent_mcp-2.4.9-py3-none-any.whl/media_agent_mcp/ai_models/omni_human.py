import hashlib
import os
import random
import time
from typing import Dict, Any, Optional
import requests

# Fault-tolerance settings
DEFAULT_TIMEOUT = 20  # seconds per HTTP request
RETRY_STATUS_CODES = {500, 502, 503, 504}
MAX_HTTP_RETRIES = 3
BACKOFF_FACTOR = 1.8
MAX_JITTER = 0.3  # seconds jitter added to backoff


def _sleep_with_backoff(attempt: int) -> None:
    """
    Args:
        attempt: Zero-based retry attempt index
    
    Returns:
        result: None. Sleeps for an exponential-backoff duration with jitter
    """
    delay = (BACKOFF_FACTOR ** attempt) + random.random() * MAX_JITTER
    time.sleep(delay)


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
    last_err: Optional[Exception] = None
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
            if isinstance(e, requests.HTTPError) and (getattr(e.response, 'status_code', 0) not in RETRY_STATUS_CODES):
                # Do not retry non-transient HTTP errors
                raise
            if attempt < max_retries:
                _sleep_with_backoff(attempt)
                continue
            raise
    # Should never reach here, but raise the last error for safety
    if last_err is not None:
        raise last_err
    raise RuntimeError("Unknown error in _post_json_with_retry")


def _generate_signature(nonce: int, timestamp: int, security_key: str) -> str:
    """
    Generates a signature for the API request.
    """
    keys = [str(nonce), str(security_key), str(timestamp)]
    keys.sort()
    key_str = "".join(keys).encode("utf-8")
    signature = hashlib.sha1(key_str).hexdigest()
    return signature.lower()


def _submit_task(image_url: str, audio_url: str, api_key: str, security_key: str) -> str:
    """
    Submits a video generation task.
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


def generate_video_from_omni_human(image_url: str, audio_url: str) -> str:
    """
    Generates a video from an image and audio using the Omni Human API.

    Args:
        image_url: The URL of the portrait image.
        audio_url: The URL of the audio.

    Returns:
        The URL of the generated video.
    """
    api_key = os.environ.get("OMNI_HUMAN_AK")
    security_key = os.environ.get("OMNI_HUMAN_SK")

    if not api_key or not security_key:
        raise ValueError("OMNI_HUMAN_AK and OMNI_HUMAN_SK environment variables must be set")

    # Submit task with retry already handled inside _submit_task
    task_id = _submit_task(image_url, audio_url, api_key, security_key)

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
        except Exception as e:
            # Transient errors from _post_json_with_retry are already retried; if still failing, wait and continue
            last_message = str(e)
            time.sleep(poll_interval)
            continue

        if result.get("code") != 10000:
            # Non-success code from API; treat as transient unless explicit failure status
            last_message = result.get("message", "unknown error")
            status = result.get("data", {}).get("status")
            if status in ["failed", "error"]:
                raise Exception(f"Video generation failed: {result}")
            time.sleep(poll_interval)
            continue

        data = result.get("data", {})
        status = data.get("status")
        last_message = data.get("message") or status

        if status == "done":
            video_url = data.get("video_url")
            if not video_url:
                raise Exception("API returned done status without video_url")
            return video_url
        elif status in ["failed", "error"]:
            raise Exception(f"Video generation failed: {result}")

        time.sleep(poll_interval)


if __name__ == '__main__':
    print(generate_video_from_omni_human(
        image_url='https://carey.tos-ap-southeast-1.bytepluses.com/media_agent/2025-07-28/e6c6751b65a846d1928356ac4c60dd13.jpg',
        audio_url='https://carey.tos-ap-southeast-1.bytepluses.com/media_agent/2025-08-26/eeeb1cd0f5034200981219ee0a0a8ece.mp3'
    ))