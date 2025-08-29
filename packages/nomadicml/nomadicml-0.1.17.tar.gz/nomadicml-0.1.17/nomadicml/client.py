"""
NomadicML API client for interacting with the DriveMonitor backend.
"""
from functools import cached_property    
import json
import logging
from typing import Dict, Any, Optional
import requests
import uuid 
import backoff

from .exceptions import NomadicMLError, AuthenticationError, APIError
from .utils import validate_api_key, format_error_message

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("nomadicml")

DEFAULT_BASE_URL = "https://api-prod.nomadicml.com/"
DEFAULT_COLLECTION_NAME = "videos"
DEFAULT_FOLDER_COLLECTION_NAME = "videoFolders"
DEFAULT_TIMEOUT = 900  # seconds

def _summarise_files(files):
    return {k: (v[0], v[2]) for k, v in (files or {}).items()}

class NomadicML:
    """
    NomadicML client for interacting with the DriveMonitor API.
    
    This is the base client that handles authentication and HTTP requests.
    
    Args:
        api_key: Your API key for authentication.
        base_url: The base URL of the API. Defaults to the production API.
        timeout: The default timeout for API requests in seconds.
        collection_name: The Firestore collection name to use for videos.
        folder_collection_name: The Firestore collection name to use for folders.
    """

    def __init__(
        self, 
        api_key: str, 
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        folder_collection_name: str = DEFAULT_FOLDER_COLLECTION_NAME,
    ):
        from . import __version__
        validate_api_key(api_key)
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.collection_name = collection_name
        self.folder_collection_name = folder_collection_name
        
        # Set up a session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "User-Agent": f"NomadicML-Python-SDK/{__version__}",
        })

        # ─────────── increase host & total pool size (and add light retries) ───────────
        retry = Retry(
            total=None,                 # don't multiply with other buckets
            connect=0, read=0,          # let backoff handle exceptions
            status=3,                   # only status retries here
            backoff_factor=0.5,
            status_forcelist=[408, 429, 500, 502, 503, 504] + list(range(520, 528)),
            allowed_methods=frozenset({"HEAD","GET","POST","PUT","PATCH","DELETE","OPTIONS","TRACE"}),
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(
            pool_connections=100,   # total socket pool size
            pool_maxsize=100,       # per-host pool size
            max_retries=retry,
        )
     # - 500: Internal Server Error                                                                                                                      │
     # - 502: Bad Gateway                                                                                                                                │
     # - 503: Service Unavailable                                                                                                                        │
     # - 504: Gateway Timeout                                                                                                                            │
     # - 520-527: Cloudflare errors (Web Server Unknown, Connection Timed Out, Origin Is Unreachable, etc.)
        # apply to both HTTP and HTTPS
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.debug(f"Initialized NomadicML client with base URL: {self.base_url}")
    
    
    # ───────────────────────── video helper (lazy) ─────────────────────────
    @cached_property
    def video(self) -> "VideoClient":
        """
        A lazily-instantiated high-level helper for video workflows.

        The first time you access `client.video` (or call one of the flat
        proxy methods below) we create a single `VideoClient` bound to this
        REST client and cache it for reuse.
        """
        from .video import VideoClient          # local import avoids cycles
        return VideoClient(self)

    # ───────────────────────── flat convenience proxies ────────────────────
    def upload(self, *args, **kwargs):
        """Proxy to `client.video.upload()` so you can just call `client.upload(...)`."""
        return self.video.upload(*args, **kwargs)

    def analyze(self, *args, **kwargs):
        """Proxy to `client.video.video.analyze()`."""
        return self.video.analyze(*args, **kwargs)

    def my_videos(self, *args, **kwargs):
        """Proxy to `client.video.my_videos()`."""
        return self.video.my_videos(*args, **kwargs)

    def delete_video(self, video_id: str) -> dict:
        """Proxy to `client.video.delete_video()`."""
        return self.video.delete_video(video_id)
    
    def search_videos(self, *args, **kwargs):
        """Proxy to `client.video.search_videos()`."""
        return self.video.search_videos(*args, **kwargs)
    
    def get_visuals(self, *args, **kwargs):
        """Proxy to `client.video.get_visuals()`."""
        return self.video.get_visuals(*args, **kwargs)
    
    def get_visual(self, *args, **kwargs):
        """Proxy to `client.video.get_visual()`."""
        return self.video.get_visual(*args, **kwargs)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """
        Make an HTTP request to the NomadicML API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Form data
            json_data: JSON data
            files: Files to upload
            timeout: Request timeout in seconds
            
        Returns:
            The HTTP response.
            
        Raises:
            AuthenticationError: If authentication fails.
            APIError: If the API returns an error.
            NomadicMLError: For any other errors.
        """
        if timeout is None:
            timeout = self.timeout
            
        from . import __version__
        url = f"{self.base_url}{endpoint}"
        req_id = str(uuid.uuid4())

        #logger.debug(">>> %s %s [%s]", method, url, req_id)
        logger.debug("    params=%s json=%s data=%s files=%s",
                     params, json_data, str(data)[:500],
                     _summarise_files(files))
        
        # Add SDK identification headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Client-Type": "SDK",
            "X-Client-Version": __version__,
            "User-Agent": f"NomadicML-Python-SDK/{__version__}",
            "X-Request-ID": req_id,
        }
        
        # Optional idempotency for mutating methods
        if method.upper() in {"POST","PUT","PATCH","DELETE"}:
            headers.setdefault("Idempotency-Key", req_id)
        
        @backoff.on_exception(
            backoff.expo,
            (
                requests.exceptions.SSLError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ReadTimeout,
            ),
            max_tries=4,
            max_time=300,
            jitter=backoff.random_jitter,
            on_backoff=lambda d: logger.warning(
                f"[{req_id}] {method} {url} attempt {d['tries']} failed: "
                f"{type(d['exception']).__name__}; retrying in {d['wait']:.1f}s"
            ),
            on_giveup=lambda d: logger.error(
                f"[{req_id}] {method} {url} failed after {d['tries']} attempts: "
                f"{type(d['exception']).__name__}"
            ),
        )
        def _send():
            return self.session.request(
                method=method, url=url, headers=headers,
                params=params, data=data, json=json_data, files=files,
                timeout=timeout or self.timeout,
            )
        
        try:
            response = _send()

            logger.debug("<<< %s %s – %s", method, url, response.status_code)
            
            # Check for error responses
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed. Check your API key.")

            if response.status_code >= 400:
                logger.error("Request-ID %s failed: %s", req_id, response.status_code)
                try:
                    error_data = response.json()
                except (ValueError, json.JSONDecodeError):
                    error_data = {"message": response.text}
                
                error_message = format_error_message(error_data)
                raise APIError(response.status_code, error_message, error_data)
            
            return response
            
        except requests.RequestException as e:
            # Handle network errors
            raise NomadicMLError(f"Request failed: {e.__class__.__name__}: {e}") from e
    
    def verify_auth(self) -> Dict[str, Any]:
        """
        Verify that the API key is valid.
        
        Returns:
            A dictionary with authentication information.
            
        Raises:
            AuthenticationError: If authentication fails.
        """
        response = self._make_request("POST", "/api/keys/verify")
        return response.json()
