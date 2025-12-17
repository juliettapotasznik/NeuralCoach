import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from services.openvino_client import process_video
from services.autoencoder_client import analyze_csv

@pytest.mark.asyncio
async def test_process_video_success():
    # Mock response data
    mock_response_data = {
        "exercise_name": "biceps",
        "csv_base64": "base64encodedcsvdata"
    }
    
    # Mock httpx response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status = MagicMock()

    # Mock httpx client
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await process_video(b"fakevideobytes", "test.mp4", "biceps")
    
    assert result == mock_response_data
    mock_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_process_video_timeout():
    # Mock httpx client to raise TimeoutException
    mock_client = AsyncMock()
    mock_client.post.side_effect = httpx.TimeoutException("Timeout")
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(httpx.TimeoutException):
            await process_video(b"fakevideobytes", "test.mp4", "biceps")

@pytest.mark.asyncio
async def test_analyze_csv_success():
    # Mock response data
    mock_response_data = {
        "feedback": "Good form",
        "frame_ids": [1, 2, 3]
    }
    
    # Mock httpx response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status = MagicMock()

    # Mock httpx client
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await analyze_csv("base64csv", "biceps")
    
    assert result == mock_response_data
    mock_client.post.assert_called_once()
