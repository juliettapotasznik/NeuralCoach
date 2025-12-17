"""
Client for communicating with the LSTM Autoencoder analysis service.
"""
import httpx
from typing import Dict, Any
import logging
import os

logger = logging.getLogger(__name__)


AUTOENCODER_SERVICE_URL = os.getenv("AUTOENCODER_SERVICE_URL", "http://localhost:8003")


async def analyze_csv(csv_base64: str, exercise_name: str, video_path: str = None) -> Dict[str, Any]:
    """
    Send CSV data to LSTM Autoencoder service for analysis.

    Args:
        csv_base64: Base64-encoded CSV data from pose extraction
        exercise_name: Name of the exercise (e.g., "biceps", "squats")
        video_path: Path to the video file (optional, for overlay generation)

    Returns:
        Dictionary containing feedback text and optional frame_ids

    Raises:
        httpx.TimeoutException: If request times out
        httpx.RequestError: If request fails
    """
    try:
        logger.info(f"Sending CSV data to Autoencoder service for exercise '{exercise_name}'")

        # Increase timeout to 5 minutes for AI analysis (can take long for complex processing)
        async with httpx.AsyncClient(timeout=300.0) as client:
            data = {
                "csv_base64": csv_base64,
                "exercise_name": exercise_name
            }
            if video_path:
                data["video_path"] = video_path

            logger.info(f"Sending to Autoencoder - exercise: {exercise_name}, csv_len: {len(csv_base64)}, video_path: {video_path}")

            response = await client.post(
                f"{AUTOENCODER_SERVICE_URL}/analyze_csv",
                data=data
            )

            # Log response details for debugging
            if response.status_code != 200:
                logger.error(f"Autoencoder service returned {response.status_code}")
                logger.error(f"Response body: {response.text}")

            response.raise_for_status()

            result = response.json()
            logger.info(f"Autoencoder service analyzed CSV successfully")
            return result

    except httpx.TimeoutException as e:
        logger.error(f"Autoencoder service timeout: {str(e)}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Autoencoder HTTP error {e.response.status_code}: {e.response.text}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Autoencoder service request error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Autoencoder client: {str(e)}")
        raise
