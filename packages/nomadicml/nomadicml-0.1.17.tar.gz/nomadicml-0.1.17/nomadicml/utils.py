"""Utility functions for the NomadicML SDK."""

import os
import logging
from typing import Dict, Any, Union
from urllib.parse import urlparse
from pathlib import Path

from .exceptions import ValidationError
from .types import VideoSource

logger = logging.getLogger("nomadicml")


def validate_api_key(api_key: str) -> None:
    """
    Validate the format of an API key.
    
    Args:
        api_key: The API key to validate.
        
    Raises:
        ValidationError: If the API key format is invalid.
    """
    if not isinstance(api_key, str):
        raise ValidationError("API key must be a string")
    
    if not api_key.strip():
        raise ValidationError("API key cannot be empty")


REMOTE_SCHEMES = {"http", "https"}

VIDEO_EXTS = {".mp4", ".webm", ".mov", ".avi"}


def looks_like_video(path_str: str) -> bool:
    """Return True if ``path_str`` has a known video extension."""
    return Path(path_str).suffix.lower() in VIDEO_EXTS


def infer_source(src: Union[str, Path]) -> VideoSource:
    """Infer the :class:`~nomadicml.types.VideoSource` for ``src``.

    The heuristic is:
    1. If the string has a scheme matching ``REMOTE_SCHEMES`` ⇒ ``VIDEO_URL``.
       The URL must end with one of :data:`VIDEO_EXTS`.
    2. Else, if the path exists locally or has a video suffix ⇒ ``FILE``.
       Local files are validated to ensure the extension is supported.
    3. If none of the above match, raise ValidationError since we don't support
       uploading from saved video IDs.
    """
    s = str(src).strip()

    # 1) Remote URL
    scheme = urlparse(s).scheme.lower()
    if scheme in REMOTE_SCHEMES:
        if not any(s.lower().endswith(ext) for ext in VIDEO_EXTS):
            supported_exts = ", ".join(sorted(VIDEO_EXTS))
            raise ValidationError(f"Remote URI must point to a video file with supported extension ({supported_exts})")
        return VideoSource.VIDEO_URL

    # 2) Local file (exists or looks like a file path)
    p = Path(s).expanduser()
    if p.exists():
        if not looks_like_video(p):
            supported_exts = ", ".join(sorted(VIDEO_EXTS))
            raise ValidationError(f"Local file must be a supported video type ({supported_exts})")
        return VideoSource.FILE
    if p.suffix and looks_like_video(p):
        return VideoSource.FILE

    # 3) If we can't determine it's a file or URL, it might be a video ID
    # but we don't support uploading from video IDs
    supported_exts = ", ".join(sorted(VIDEO_EXTS))
    supported_schemes = ", ".join(sorted(REMOTE_SCHEMES))
    raise ValidationError(
        f"Cannot determine source type for '{s}'. "
        f"Must be a local file path with supported extension ({supported_exts}) "
        f"or remote URL with supported scheme ({supported_schemes}). "
        "To analyze existing videos, use analyze() with the video ID directly."
    )

def format_error_message(response_data: Dict[str, Any]) -> str:
    """
    Format an error message from the API response.
    
    Args:
        response_data: The response data from the API.
        
    Returns:
        A formatted error message.
    """
    if isinstance(response_data, dict):
        # Try to extract error message from common patterns
        if "detail" in response_data:
            detail = response_data["detail"]
            if isinstance(detail, list):
                # Handle validation errors which are often lists
                return "; ".join(f"{err.get('loc', [''])[0]}: {err.get('msg', '')}" 
                                for err in detail)
            return str(detail)
        elif "message" in response_data:
            return str(response_data["message"])
        elif "error" in response_data:
            return str(response_data["error"])
    
    # Fallback to returning the entire response as a string
    return str(response_data)


def get_file_mime_type(file_path: str) -> str:
    """
    Get the MIME type of a file based on its extension.
    
    Args:
        file_path: The path to the file.
        
    Returns:
        The MIME type of the file.
    """
    _, ext = os.path.splitext(file_path)
    
    # Simple mapping of common file extensions to MIME types
    mime_types = {
        ".mp4": "video/mp4",
        ".avi": "video/x-msvideo",
        ".mov": "video/quicktime",
        ".wmv": "video/x-ms-wmv",
        ".flv": "video/x-flv",
        ".mkv": "video/x-matroska",
    }
    
    return mime_types.get(ext.lower(), "application/octet-stream")


def get_filename_from_path(file_path: str) -> str:
    """
    Extract the filename from a file path.
    
    Args:
        file_path: The file path.
        
    Returns:
        The filename.
    """
    return os.path.basename(file_path)
