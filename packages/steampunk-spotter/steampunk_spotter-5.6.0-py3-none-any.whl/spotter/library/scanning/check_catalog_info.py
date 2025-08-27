"""Provide check catalog info model."""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class CheckCatalogInfo(BaseModel):
    """A container for information about the specific check in check catalog from the backend."""

    event_code: str
    event_value: str
    event_message: str
    check_class: str
    event_subcode: Optional[str] = None
    event_submessage: Optional[str] = None

    @classmethod
    def from_api_response_element(cls, element: Dict[str, Any]) -> "CheckCatalogInfo":
        """
        Convert element entry from scan API response to CheckCatalogInfo object.

        :param element: An 'element' JSON entry from scan API response
        :return: CheckCatalogInfo object
        """
        return cls(
            event_code=element.get("event_code", ""),
            event_value=element.get("event_value", ""),
            event_message=element.get("event_message", ""),
            check_class=element.get("check_class", ""),
            event_subcode=element.get("event_subcode", ""),
            event_submessage=element.get("event_submessage", ""),
        )
