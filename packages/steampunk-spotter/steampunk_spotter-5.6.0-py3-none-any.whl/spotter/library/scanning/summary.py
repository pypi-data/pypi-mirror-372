"""Provide scan summary model."""

from typing import Optional

from pydantic import BaseModel

from spotter.library.scanning.check_result import CheckResult
from spotter.library.scanning.display_level import DisplayLevel


class Summary(BaseModel):
    """A container for scan result summary."""

    scan_time: float
    num_errors: int
    num_warnings: int
    num_hints: int
    status: str

    def update(self, check_result: Optional[CheckResult]) -> None:
        """
        Update summary information.

        If check_result is not set the summary does not change, otherwise
        summary update respects CheckResult.level field.
        """
        if not check_result:
            return

        if check_result.level == DisplayLevel.ERROR:
            self.num_errors += 1
        elif check_result.level == DisplayLevel.WARNING:
            self.num_warnings += 1
        else:
            self.num_hints += 1
