"""Provide model for starting a new scan."""

from typing import Any, Dict

from pydantic import BaseModel

from spotter.library.scanning.progress import Progress


class StartAsync(BaseModel):
    """A container for scan start originating from the backend."""

    uuid: str
    project_id: str
    organization_id: str
    scan_progress: Progress

    @classmethod
    def from_api_response(cls, response_json: Dict[str, Any]) -> "StartAsync":
        """
        Convert scan API response to Start object.

        :param response_json: The backend API response in JSON format
        :return: Start object
        """
        return cls(
            uuid=response_json.get("id", ""),
            project_id=response_json.get("project_id", ""),
            organization_id=response_json.get("organization_id", ""),
            scan_progress=Progress.from_api_response_element(response_json.get("scan_progress", {})),
        )
