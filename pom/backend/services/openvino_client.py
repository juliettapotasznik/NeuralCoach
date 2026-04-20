"""
Client for communicating with the OpenVINO pose extraction service.
"""
import httpx
from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)


OPENVINO_SERVICE_URL = os.getenv("OPENVINO_SERVICE_URL", "http://localhost:8001")


async def process_video(video_file: bytes, filename: str, exercise_name: str) -> Dict[str, Any]:
    """
    Send video to OpenVINO service for pose extraction.

    Args:
        video_file: Video file content as bytes
        filename: Original filename
        exercise_name: Name of the exercise (e.g., "biceps", "squats")

    Returns:
        Dictionary containing exercise_name and csv_base64

    Raises:
        httpx.TimeoutException: If request times out
        httpx.RequestError: If request fails
    """
    try:
        logger.info(f"Sending video '{filename}' to OpenVINO service for exercise '{exercise_name}'")

        # Increase timeout to 5 minutes for video processing (can take long for large videos)
        async with httpx.AsyncClient(timeout=300.0) as client:
            files = {"file": (filename, video_file, "video/mp4")}
            data = {"exercise_name": exercise_name}

            response = await client.post(
                f"{OPENVINO_SERVICE_URL}/process_video",
                files=files,
                data=data
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"OpenVINO service processed video successfully")
            return result

    except httpx.TimeoutException as e:
        logger.error(f"OpenVINO service timeout: {str(e)}")
        raise
    except httpx.RequestError as e:
        logger.error(f"OpenVINO service request error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OpenVINO client: {str(e)}")
        raise
