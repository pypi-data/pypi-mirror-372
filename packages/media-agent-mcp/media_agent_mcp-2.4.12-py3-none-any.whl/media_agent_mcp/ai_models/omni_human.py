import hashlib
import os
import random
import time
from typing import Dict, Any
import requests


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

    response = requests.post(submit_task_url, params=params, headers=headers, json=body)
    response.raise_for_status()
    data = response.json()
    if data["code"] != 10000:
        raise Exception(f"Failed to submit task: {data['message']}")
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

    response = requests.post(get_result_url, params=params, headers=headers, json=body)
    response.raise_for_status()
    return response.json()


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

    task_id = _submit_task(image_url, audio_url, api_key, security_key)
    while True:
        result = _get_task_result(task_id, api_key, security_key)
        if result["code"] != 10000:
            raise Exception(f"Failed to get task result: {result['message']}")

        status = result.get("data", {}).get("status")
        if status == "done":
            return result["data"]["video_url"]
        elif status in ["failed", "error"]:
            raise Exception(f"Video generation failed: {result}")

        time.sleep(5)


if __name__ == '__main__':
    print(generate_video_from_omni_human(
        image_url='https://carey.tos-ap-southeast-1.bytepluses.com/media_agent/2025-07-28/e6c6751b65a846d1928356ac4c60dd13.jpg',
        audio_url='https://carey.tos-ap-southeast-1.bytepluses.com/media_agent/2025-08-26/eeeb1cd0f5034200981219ee0a0a8ece.mp3'
    ))