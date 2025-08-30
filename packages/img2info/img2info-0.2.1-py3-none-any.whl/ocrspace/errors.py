
class OCRSpaceError(Exception):
    """Base exception for OCRSpace SDK."""
class AuthError(OCRSpaceError):
    """Raised when authentication fails (bad key)."""
class RequestError(OCRSpaceError):
    """Raised on network or HTTP errors."""
class ProcessingError(OCRSpaceError):
    """Raised when OCR.Space reports processing errors."""
