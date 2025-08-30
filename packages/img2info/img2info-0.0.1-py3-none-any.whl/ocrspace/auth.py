
class OCRSpaceAuth:
    """Simple auth wrapper storing API key."""
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required for OCR.Space API")
        self.api_key = api_key

    def as_param(self):
        return {"apikey": self.api_key}
