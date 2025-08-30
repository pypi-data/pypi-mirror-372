
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

@dataclass
class ParsedResult:
    file_parse_exit_code: int = 0
    parsed_text: str = ""
    error_message: Optional[Any] = None
    error_details: Optional[Any] = None
    text_overlay: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ParsedResult":
        return ParsedResult(
            file_parse_exit_code=d.get("FileParseExitCode", 0),
            parsed_text=d.get("ParsedText", "") or "",
            error_message=d.get("ErrorMessage"),
            error_details=d.get("ErrorDetails"),
            text_overlay=d.get("TextOverlay"),
        )

@dataclass
class OCRSpaceResult:
    parsed_results: List[ParsedResult] = field(default_factory=list)
    is_errored_on_processing: bool = False
    processing_time_in_ms: Optional[str] = None
    searchable_pdf_url: Optional[str] = None
    ocr_exit_code: Optional[int] = None

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "OCRSpaceResult":
        prs = [ParsedResult.from_dict(x) for x in d.get("ParsedResults", [])]
        return OCRSpaceResult(
            parsed_results=prs,
            is_errored_on_processing=d.get("IsErroredOnProcessing", False),
            processing_time_in_ms=d.get("ProcessingTimeInMilliseconds"),
            searchable_pdf_url=d.get("SearchablePDFURL"),
            ocr_exit_code=d.get("OCRExitCode"),
        )

    @property
    def text(self) -> str:
        return "\n".join([p.parsed_text for p in self.parsed_results if p.parsed_text])
