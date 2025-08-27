from abc import ABC, abstractmethod

from pydantic import BaseModel

from spotter.library.parsing.parsing import ParsingResult
from spotter.library.scanning.result import ScanResult


class OutputFormatOptions(BaseModel):
    show_docs_url: bool
    show_scan_url: bool
    show_colors: bool
    rewriting_enabled: bool

    @classmethod
    def enable_all(cls) -> "OutputFormatOptions":
        return cls(
            show_docs_url=True,
            show_scan_url=True,
            show_colors=True,
            rewriting_enabled=True,
        )


class OutputFormatter(ABC):
    @abstractmethod
    def format(self, scan_result: ScanResult, parsing_result: ParsingResult, options: OutputFormatOptions) -> str:
        """Format a scan result into a user-facing format."""
