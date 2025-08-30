from __future__ import annotations

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any

from flask import Blueprint, jsonify, request, send_file, after_this_request

from media_agent_mcp.be.utils import (
    download_video_from_url,
    _probe_duration,
    _probe_has_audio,
)

logger = logging.getLogger(__name__)

media_bp = Blueprint("media", __name__)


@media_bp.post("/combine-audio-video")
def combine_audio_video():
    """
    Combines audio and video from URLs.
    """
    try:
        data = request.get_json(silent=True) or {}
        video_url = data.get("video_url")
        audio_url = data.get("audio_url")
        audio_start_time = float(data.get("audio_start_time", 0.0))

        if not video_url or not audio_url:
            return jsonify({
                "status": "error",
                "data": None,
                "message": "Fields video_url and audio_url are required"
            }), 400

        temp_files: List[Path] = []

        @after_this_request
        def cleanup(response):
            for f in temp_files:
                try:
                    f.unlink(missing_ok=True)
                except Exception:
                    pass
            return response

        # Download video
        video_dl = download_video_from_url(video_url)
        if video_dl.get("status") == "error":
            return jsonify(video_dl), 400
        video_path = Path(video_dl["data"]["file_path"])  # type: ignore[index]
        temp_files.append(video_path)

        # Download audio
        audio_dl = download_video_from_url(audio_url)
        if audio_dl.get("status") == "error":
            return jsonify(audio_dl), 400
        audio_path = Path(audio_dl["data"]["file_path"])  # type: ignore[index]
        temp_files.append(audio_path)

        video_duration = _probe_duration(video_path)
        has_audio = _probe_has_audio(video_path)

        # FFmpeg command - always video as input 0, audio as input 1
        output_path = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name)
        temp_files.append(output_path)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(audio_path),
        ]

        delay_ms = int(audio_start_time)

        if has_audio:
            # Video has audio, mix them with delay on new audio
            filter_complex = f"[1:a]adelay={delay_ms}|{delay_ms}[del];[0:a][del]amix=inputs=2:duration=first[a]"
            cmd.extend([
                "-filter_complex", filter_complex,
                "-map", "0:v",
                "-map", "[a]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-t", str(video_duration),  # Keep video duration unchanged
            ])
        else:
            # Video has no audio, add the new audio with delay and pad to video duration
            if delay_ms > 0:
                filter_complex = f"[1:a]adelay={delay_ms}|{delay_ms},apad[a]"
                cmd.extend([
                    "-filter_complex", filter_complex,
                    "-map", "0:v",
                    "-map", "[a]",
                ])
            else:
                cmd.extend([
                    "-map", "0:v",
                    "-map", "1:a",
                ])
            cmd.extend([
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",  # Use with apad to match video duration
            ])

        cmd.append(str(output_path))

        logger.info("FFmpeg cmd: %s", " ".join(cmd))
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        if proc.returncode != 0:
            logger.error("FFmpeg error: %s", proc.stdout)
            return jsonify({"status": "error", "data": None, "message": "FFmpeg failed -> " + proc.stdout}), 500

        logger.info("FFmpeg output: %s", proc.stdout)
        return send_file(str(output_path), mimetype="video/mp4")

    except Exception as e:
        logger.exception("Audio-video combination service error: %s", e)
        return jsonify({"status": "error", "data": None, "message": str(e)}), 500


@media_bp.post("/concat-videos")
def concat_videos():
    """
    Concatenates multiple videos from a list of URLs.
    """
    try:
        data = request.get_json(silent=True) or {}
        video_urls = data.get("video_urls")

        if not video_urls or not isinstance(video_urls, list):
            return jsonify({
                "status": "error",
                "data": None,
                "message": "Field video_urls is required and must be a list"
            }), 400

        temp_files: List[Path] = []

        @after_this_request
        def cleanup(response):
            for f in temp_files:
                try:
                    f.unlink(missing_ok=True)
                except Exception:
                    pass
            return response

        video_paths = []
        for url in video_urls:
            dl = download_video_from_url(url)
            if dl.get("status") == "error":
                return jsonify(dl), 400
            path = Path(dl["data"]["file_path"])  # type: ignore[index]
            temp_files.append(path)
            video_paths.append(path)

        # Create a file list for ffmpeg
        list_path = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".txt").name)
        temp_files.append(list_path)
        with open(list_path, "w") as f:
            for path in video_paths:
                f.write(f"file '{path.resolve()}'\n")

        # FFmpeg command
        output_path = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name)
        temp_files.append(output_path)

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_path),
            "-c", "copy",
            str(output_path),
        ]

        logger.debug("FFmpeg cmd: %s", " ".join(cmd))
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        if proc.returncode != 0:
            logger.error("FFmpeg error: %s", proc.stdout)
            return jsonify({"status": "error", "data": None, "message": "FFmpeg failed -> " + proc.stdout}), 500

        return send_file(str(output_path), mimetype="video/mp4")

    except Exception as e:
        logger.exception("Video concatenation service error: %s", e)
        return jsonify({"status": "error", "data": None, "message": str(e)}), 500


@media_bp.post("/stack-videos")
def stack_videos():
    """
    Stacks two videos vertically (secondary on top of main).
    """
    try:
        data = request.get_json(silent=True) or {}
        main_video_url = data.get("main_video_url")
        secondary_video_url = data.get("secondary_video_url")

        if not main_video_url or not secondary_video_url:
            return jsonify({
                "status": "error",
                "data": None,
                "message": "Fields main_video_url and secondary_video_url are required"
            }), 400

        temp_files: List[Path] = []

        @after_this_request
        def cleanup(response):
            for f in temp_files:
                try:
                    f.unlink(missing_ok=True)
                except Exception:
                    pass
            return response

        # Download main video
        main_dl = download_video_from_url(main_video_url)
        if main_dl.get("status") == "error":
            return jsonify(main_dl), 400
        main_path = Path(main_dl["data"]["file_path"])  # type: ignore[index]
        temp_files.append(main_path)

        # Download secondary video
        secondary_dl = download_video_from_url(secondary_video_url)
        if secondary_dl.get("status") == "error":
            return jsonify(secondary_dl), 400
        secondary_path = Path(secondary_dl["data"]["file_path"])  # type: ignore[index]
        temp_files.append(secondary_path)

        main_duration = _probe_duration(main_path)
        output_path = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name)
        temp_files.append(output_path)

        cmd = [
            "ffmpeg", "-y",
            "-i", str(main_path),           # input 0: main video
            "-stream_loop", "-1",
            "-i", str(secondary_path),      # input 1: secondary video (looped)
            "-filter_complex", (
                # Scale secondary video to main video's width, maintaining aspect ratio
                "[1:v]scale=w=iw:h=-2[sec_scaled];"
                # Stack scaled secondary video on top of main video
                "[sec_scaled][0:v]vstack=inputs=2[v]"
            ),
            "-map", "[v]",                  # Map the combined video stream
            "-map", "0:a?",                 # Map audio from the main video, if it exists
            "-c:a", "copy",                 # Copy the audio stream without re-encoding
            "-t", str(main_duration),       # Set the output duration to the main video's duration
            str(output_path),
        ]

        logger.info("FFmpeg cmd: %s", " ".join(cmd))
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        if proc.returncode != 0:
            logger.error("FFmpeg error: %s", proc.stdout)
            return jsonify({"status": "error", "data": None, "message": "FFmpeg failed -> " + proc.stdout}), 500

        logger.info("FFmpeg output: %s", proc.stdout)
        return send_file(str(output_path), mimetype="video/mp4")

    except Exception as e:
        logger.exception("Video stacking service error: %s", e)
        return jsonify({"status": "error", "data": None, "message": str(e)}), 500