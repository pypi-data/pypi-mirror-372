
import base64, io, mimetypes
from typing import Tuple

def guess_mime(filename: str) -> Tuple[str, str]:
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream", filename

def base64_to_bytes(b64: str) -> bytes:
    # accept data URI too
    if b64.startswith("data:"):
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64)
