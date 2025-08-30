
from typing import Optional, Any, Dict
import io, mimetypes, requests, base64
from .auth import OCRSpaceAuth
from .errors import OCRSpaceError, AuthError, RequestError, ProcessingError
from .models import OCRSpaceResult
from .utils import guess_mime, base64_to_bytes

DEFAULT_ENDPOINT = "https://api.ocr.space/parse/image"

class OCRSpaceClient:
    def __init__(self, api_key: str, base_url: str = DEFAULT_ENDPOINT, timeout: int = 60):
        self.auth = OCRSpaceAuth(api_key)
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

    def _handle_response(self, resp: requests.Response) -> OCRSpaceResult:
        if resp.status_code == 401:
            raise AuthError("Unauthorized - invalid API key or access denied")
        if resp.status_code >= 400:
            raise RequestError(f"HTTP {resp.status_code}: {resp.text[:300]}")
        try:
            j = resp.json()
        except ValueError:
            raise RequestError("Non-JSON response from OCR.Space: " + resp.text[:300])
        if j.get("IsErroredOnProcessing"):
            msg = j.get("ErrorMessage") or j.get("ErrorDetails") or "Unknown processing error"
            if isinstance(msg, list):
                msg = "; ".join([str(m) for m in msg])
            raise ProcessingError(msg)
        return OCRSpaceResult.from_dict(j)

    def _post(self, data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None):
        payload = dict(self.auth.as_param())
        if data:
            payload.update({k: v for k, v in data.items() if v is not None})
        try:
            resp = self.session.post(self.base_url, data=payload, files=files, timeout=self.timeout)
        except requests.RequestException as e:
            raise RequestError(str(e)) from e
        return self._handle_response(resp)

    # Public APIs ------------------------------------------------
    def from_file(self, path: str, filename: Optional[str] = None, **kwargs) -> OCRSpaceResult:
        filename = filename or path.split("/")[-1]
        mime, _ = guess_mime(filename)
        with open(path, "rb") as f:
            files = {"file": (filename, f, mime)}
            return self._post(data=kwargs, files=files)

    def from_url(self, url: str, language="eng", filetype="jpg"):
        data = {
            "apikey": self.api_key,
            "url": url,
            "language": language,
            "filetype": filetype
        }
        return self._post(data=data, files=None)

    def from_bytes(self, content: bytes, filename: str = "upload.jpg", **kwargs) -> OCRSpaceResult:
        mime, _ = guess_mime(filename)
        fileobj = io.BytesIO(content)
        files = {"file": (filename, fileobj, mime)}
        return self._post(data=kwargs, files=files)

    def from_base64(self, b64_string: str, filename: str = "upload.jpg", **kwargs) -> OCRSpaceResult:
        content = base64_to_bytes(b64_string)
        return self.from_bytes(content, filename=filename, **kwargs)
