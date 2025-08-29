"""
NomadicML Python SDK for the DriveMonitor API.

This SDK provides a simple interface to interact with the 
DriveMonitor backend for analyzing driving videos.
"""

__version__ = "0.0.17"  # This will be the clean version for PyPI (Overwritten by CI)
__build__ = "cf337f7"      # This will hold the commit hash or full build string, populated by CI

from .client import NomadicML, DEFAULT_BASE_URL, DEFAULT_COLLECTION_NAME
from .video import VideoClient, AnalysisType
from .exceptions import NomadicMLError, AuthenticationError, APIError, VideoUploadError, AnalysisError
from .types import VideoSource, ProcessingStatus

# Add video client to NomadicML
def _add_video_client(client):
    client.video = VideoClient(client)
    return client

# Patch the NomadicML class
_original_init = NomadicML.__init__

def _patched_init(self, *args, **kwargs):
    _original_init(self, *args, **kwargs)
    _add_video_client(self)

NomadicML.__init__ = _patched_init

__all__ = [
    "NomadicML",
    "VideoClient",
    "AnalysisType",
    "NomadicMLError",
    "AuthenticationError",
    "APIError",
    "VideoUploadError",
    "AnalysisError",
    "VideoSource",
    "ProcessingStatus",
    "DEFAULT_BASE_URL",
    "DEFAULT_COLLECTION_NAME"
]
