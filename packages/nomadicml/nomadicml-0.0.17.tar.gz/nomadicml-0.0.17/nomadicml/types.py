"""Type definitions for the NomadicML SDK."""

from enum import Enum
from typing import TypedDict, Optional
class VideoSource(str, Enum):
    """Video source types."""
    
    FILE = "file"
    SAVED = "saved"  # Note: Upload from saved videos is not supported. Use analyze() for existing videos.
    VIDEO_URL = "video_url"


class ProcessingStatus(str, Enum):
    """Video processing status types."""
    
    UPLOADING = "uploading"
    UPLOADING_FAILED = "uploading_failed"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class RapidReviewEvent(TypedDict):
    """Structure of a rapid review event returned by the SDK."""
    t_start: str  # Time in "MM:SS" or "HH:MM:SS" format
    t_end: str    # Time in "MM:SS" or "HH:MM:SS" format
    category: str
    label: str
    severity: str
    aiAnalysis: str
    confidence: float
    annotated_thumbnail_url: Optional[str]


class UIEvent(TypedDict):
    """Structure of a UI event as stored in Firebase."""
    type: str           # Maps to category
    time: str           # "t=X.XX" format
    end_time: str       # "t=X.XX" format
    severity: str
    description: str    # Maps to label
    dmvRule: str
    aiAnalysis: str
    data: dict          # Original event data
    approval: str




