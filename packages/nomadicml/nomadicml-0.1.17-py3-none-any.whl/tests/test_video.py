"""
Tests for the NomadicML video client.
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
from nomadicml import NomadicML
from nomadicml.types import VideoSource
from nomadicml.exceptions import ValidationError
import time

class TestVideoClient:
    """Test cases for the NomadicML video client."""

    @pytest.fixture
    def client(self):
        """Create a NomadicML client for testing."""
        return NomadicML(api_key="test_api_key")

    def test_upload_video_with_missing_path(self, client):
        """Test upload_video with missing file_path."""
        with pytest.raises(ValidationError):
            client.video._upload_video("")

    # Override the actual validate_file_path in the module namespace
    @patch("nomadicml.video.validate_file_path")
    @patch("nomadicml.video.VideoClient.get_user_id")
    @patch("nomadicml.utils.get_filename_from_path")
    @patch("nomadicml.utils.get_file_mime_type")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake video data")
    @patch("nomadicml.client.NomadicML._make_request")
    def test_upload_video_file_success(self, mock_make_request, mock_open_file,
                                   mock_get_mime_type, mock_get_filename,
                                   mock_get_user_id, mock_validate_path, client):
        """Test successful video file upload."""
        # Setup mocks
        mock_validate_path.return_value = None  # Just ensure it doesn't raise an exception
        mock_get_filename.return_value = "test_video.mp4"
        mock_get_mime_type.return_value = "video/mp4"
        mock_get_user_id.return_value = "test_user"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "video_id": "test_video_id"}
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = client.video._upload_video(file_path="/path/to/test_video.mp4")
        
        # Assertions
        assert result == {"status": "success", "video_id": "test_video_id"}
        mock_validate_path.assert_called_once_with("/path/to/test_video.mp4")
        mock_make_request.assert_called_once()
        
        # Verify SDK headers were included
        call_args = mock_make_request.call_args
        # Headers should be passed through kwargs or in the actual request call

    @patch("nomadicml.client.requests.request")
    def test_sdk_headers_included(self, mock_request, client):
        """Test that SDK identification headers are included in requests."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_request.return_value = mock_response
        
        # Make a request
        client._make_request("GET", "/test")
        
        # Verify headers were included
        call_args = mock_request.call_args
        headers = call_args[1]["headers"]
        assert headers["X-Client-Type"] == "SDK"
        assert "X-Client-Version" in headers
        assert "NomadicML-Python-SDK" in headers["User-Agent"]

    @patch("nomadicml.client.NomadicML._make_request")
    def test_analyze_video_success(self, mock_make_request, client):
        """Test successful video analysis."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "analysis_id": "test_analysis_id"}
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = client.video.analyze_video("test_video_id")
        
        # Assertions
        assert result == {"status": "success", "analysis_id": "test_analysis_id"}
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="/api/analyze-video/test_video_id",
            data={
                "firebase_collection_name": client.collection_name,
                "model_id": "Nomadic-VL-XLarge",
            },
        )

    @patch("nomadicml.client.NomadicML._make_request")
    def test_get_video_status_success(self, mock_make_request, client):
        """Test successful video status retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "completed", "progress": 100}
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = client.video.get_video_status("test_video_id")
        
        # Assertions
        assert result == {"status": "completed", "progress": 100}
        mock_make_request.assert_called_once_with(
            "GET",
            "/api/video/test_video_id/status",
            params={"firebase_collection_name": client.collection_name}
        )

    @patch("nomadicml.client.NomadicML._make_request")
    def test_get_video_analysis_success(self, mock_make_request, client):
        """Test successful video analysis retrieval.""" 
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"events": [], "summary": "No events detected"}
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = client.video.get_video_analysis("test_video_id")
        
        # Assertions
        assert result == {"events": [], "summary": "No events detected"}
        mock_make_request.assert_called_once_with(
            "GET",
            "/api/video/test_video_id/analysis",
            params={"firebase_collection_name": client.collection_name}
        )

    @patch("nomadicml.client.NomadicML._make_request")
    def test_delete_video_success(self, mock_make_request, client):
        """Test successful video deletion."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "deleted"}
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = client.video.delete_video("test_video_id")
        
        # Assertions
        assert result == {"status": "deleted"}
        mock_make_request.assert_called_once_with(
            "DELETE",
            "/api/video/test_video_id",
            params={"firebase_collection_name": client.collection_name}
        )

    @patch("nomadicml.client.NomadicML._make_request")
    def test_my_videos_success(self, mock_make_request, client):
        """Test successful video list retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"video_id": "test_video_1"}, {"video_id": "test_video_2"}]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = client.video.my_videos()
        
        # Assertions
        assert result == [{"video_id": "test_video_1"}, {"video_id": "test_video_2"}]
        mock_make_request.assert_called_once_with(
            "GET",
            "/api/videos",
            params={"firebase_collection_name": client.collection_name}
        )

    def test_wait_for_analysis_timeout(self, client):
        """Test that wait_for_analysis raises TimeoutError when analysis doesn't complete."""
        with patch.object(client.video, 'get_video_status') as mock_get_status:
            mock_get_status.return_value = {"status": "processing"}
            
            with pytest.raises(TimeoutError):
                client.video.wait_for_analysis("test_video_id", timeout=1, poll_interval=0.1)

    @patch("nomadicml.video.VideoClient.get_video_status")
    def test_wait_for_analysis_success(self, mock_get_status, client):
        """Test successful wait_for_analysis."""
        # First call returns processing, second call returns completed
        mock_get_status.side_effect = [
            {"status": "processing"},
            {"status": "completed", "analysis": {"events": []}}
        ]
        
        result = client.video.wait_for_analysis("test_video_id", timeout=10, poll_interval=0.1)
        
        assert result["status"] == "completed"
        assert mock_get_status.call_count == 2
