"""Provide check result model."""

from typing import Any, Dict, Optional

from pydantic import BaseModel

from spotter.library.rewriting.models import CheckType, RewriteSuggestion
from spotter.library.scanning.check_catalog_info import CheckCatalogInfo
from spotter.library.scanning.display_level import DisplayLevel
from spotter.library.scanning.item_metadata import ItemMetadata


class CheckResult(BaseModel):
    """A container for parsed check results originating from the backend."""

    correlation_id: str
    original_item: Dict[str, Any]
    metadata: Optional[ItemMetadata] = None
    catalog_info: CheckCatalogInfo
    level: DisplayLevel
    message: str
    suggestion: Optional[RewriteSuggestion] = None
    doc_url: Optional[str] = None
    check_type: CheckType

    # used so classes are compared by reference
    def __hash__(self) -> int:
        return id(self)
