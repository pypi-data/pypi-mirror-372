"""Provide scan progress model."""

from typing import Any, Dict

from pydantic import BaseModel

from spotter.library.scanning.progress_status import ProgressStatus


class Progress(BaseModel):
    """A container for scan progress originating from the backend."""

    progress_status: ProgressStatus
    current: int
    total: int

    @classmethod
    def from_api_response_element(cls, response_json: Dict[str, Any]) -> "Progress":
        """
        Convert scan API response element to Progress object.

        :param response_json: The backend API response in JSON format
        :return: Progress object
        """
        return cls(
            progress_status=ProgressStatus.from_string(response_json.get("progress_status", "")),
            current=response_json.get("current", 0),
            total=response_json.get("total", 0),
        )
