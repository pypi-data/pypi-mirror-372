"""Exceptions for the NomadicML SDK."""


class NomadicMLError(Exception):
    """Base exception for all NomadicML SDK errors."""
    
    pass


class AuthenticationError(NomadicMLError):
    """Raised when there is an authentication error with the API."""
    
    pass


class APIError(NomadicMLError):
    """Raised when the API returns an error."""
    
    def __init__(self, status_code: int, message: str, details: dict = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"API Error ({status_code}): {message}")


class VideoUploadError(NomadicMLError):
    """Raised when there is an error uploading a video."""
    
    pass


class AnalysisError(NomadicMLError):
    """Raised when there is an error analyzing a video."""
    
    pass


class ValidationError(NomadicMLError):
    """Raised when input validation fails."""
    
    pass
