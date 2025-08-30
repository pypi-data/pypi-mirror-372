
"""OCR.Space Python SDK - upgraded version
Exports main client and models.
"""
from .client import OCRSpaceClient
from .errors import OCRSpaceError, AuthError, RequestError, ProcessingError
from .models import OCRSpaceResult, ParsedResult

__all__ = [
    "OCRSpaceClient",
    "OCRSpaceError", "AuthError", "RequestError", "ProcessingError",
    "OCRSpaceResult", "ParsedResult",
]
