"""Provide item metadata model."""

from typing import Any, Dict

from pydantic import BaseModel

from spotter.library.utils import get_relative_path_to_cwd


class ItemMetadata(BaseModel):
    """A container for item metadata originating from the original task or play."""

    file_name: str
    line: int
    column: int

    @classmethod
    def from_item_meta(cls, item_meta: Dict[str, Any]) -> "ItemMetadata":
        """
        Convert task metadata to ItemMetadata object for storing metadata for Ansible task or play.

        :param item_meta: Ansible task spotter_metadata content.
        :return: TaskMetadata object
        """
        file_name = get_relative_path_to_cwd(item_meta.get("file", ""))
        line = item_meta.get("line", "")
        column = item_meta.get("column", "")

        return cls(file_name=file_name, line=line, column=column)
