"""
Tests for the NomadicML client.
"""

import pytest
from unittest.mock import patch, MagicMock, ANY

from nomadicml import NomadicML
from nomadicml.exceptions import ValidationError, AuthenticationError, APIError


class TestNomadicMLClient:
    """Test cases for the NomadicML client."""
    
    def test_init_with_valid_api_key(self):
        """Test initialization with a valid API key."""
        client = NomadicML(api_key="valid_api_key")
        assert client.api_key == "valid_api_key"
        assert client.base_url == "https://fdixgrmuam.us-west-2.awsapprunner.com"
        assert client.timeout == 900
        assert client.collection_name == "videos"
        assert hasattr(client, "video")
    
    def test_init_with_invalid_api_key(self):
        """Test initialization with an invalid API key."""
        with pytest.raises(ValidationError):
            NomadicML(api_key="")
    
    def test_init_with_custom_base_url(self):
        """Test initialization with a custom base URL."""
        client = NomadicML(api_key="valid_api_key", base_url="http://localhost:8099")
        assert client.base_url == "http://localhost:8099"
    
    def test_init_with_custom_timeout(self):
        """Test initialization with a custom timeout."""
        client = NomadicML(api_key="valid_api_key", timeout=60)
        assert client.timeout == 60
    
    def test_init_with_custom_collection_name(self):
        """Test initialization with a custom collection name."""
        client = NomadicML(api_key="valid_api_key", collection_name="custom_videos")
        assert client.collection_name == "custom_videos"
    
    @patch("requests.Session.request")
    def test_make_request_success(self, mock_request):
        """Test _make_request with a successful response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "success"}
        mock_request.return_value = mock_response
        
        client = NomadicML(api_key="valid_api_key")
        response = client._make_request("GET", "/test")
        
        assert response == mock_response
        mock_request.assert_called_once_with(
            method="GET",
            url="https://fdixgrmuam.us-west-2.awsapprunner.com/test",
            headers={'X-Request-ID': ANY},
            params=None,
            data=None,
            json=None,
            files=None,
            timeout=900,
        )
    
    @patch("requests.Session.request")
    def test_make_request_auth_error(self, mock_request):
        """Test _make_request with an authentication error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        client = NomadicML(api_key="invalid_api_key")
        with pytest.raises(AuthenticationError):
            client._make_request("GET", "/test")
    
    @patch("requests.Session.request")
    def test_make_request_api_error(self, mock_request):
        """Test _make_request with an API error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"detail": "Internal server error"}
        mock_request.return_value = mock_response
        
        client = NomadicML(api_key="valid_api_key")
        with pytest.raises(APIError) as exc_info:
            client._make_request("GET", "/test")
        
        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value)
    
    @patch("nomadicml.client.NomadicML._make_request")
    def test_verify_auth(self, mock_make_request):
        """Test verify_auth method."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"valid": True, "user_id": "test_user"}
        mock_make_request.return_value = mock_response
        
        client = NomadicML(api_key="valid_api_key")
        result = client.verify_auth()
        
        assert result == {"valid": True, "user_id": "test_user"}
        mock_make_request.assert_called_once_with("POST", "/api/keys/verify")
