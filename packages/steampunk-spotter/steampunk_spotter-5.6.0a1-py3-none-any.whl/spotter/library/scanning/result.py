"""Provide scan result model."""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel

from spotter.library.rewriting.models import CheckType, RewriteSuggestion
from spotter.library.rewriting.processor import update_files
from spotter.library.scanning.check_catalog_info import CheckCatalogInfo
from spotter.library.scanning.check_result import CheckResult
from spotter.library.scanning.display_level import DisplayLevel
from spotter.library.scanning.item_metadata import ItemMetadata
from spotter.library.scanning.progress import Progress
from spotter.library.scanning.summary import Summary


class ScanResult(BaseModel):
    """A container for scan result originating from the backend."""

    # TODO: Add more fields from scan response if we need them

    uuid: Optional[str] = None
    user: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None
    project: Optional[str] = None
    organization: Optional[str] = None
    environment: Optional[Dict[str, Any]] = None
    scan_date: Optional[str] = None
    subscription: Optional[str] = None
    is_paid: Optional[bool] = None
    web_urls: Optional[Dict[str, str]] = None
    summary: Summary
    scan_progress: Progress
    check_results: List[CheckResult]
    fixed_check_results: List[CheckResult]

    @classmethod
    def from_api_response(
        cls,
        response_json: Dict[str, Any],
        input_tasks: List[Dict[str, Any]],
        input_playbooks: List[Dict[str, Any]],
        input_inventories: List[Dict[str, Any]],
        input_variables: List[Dict[str, Any]],
        scan_time: float,
    ) -> "ScanResult":
        """
        Convert scan API response to Result object.

        :param response_json: The backend API response in JSON format
        :param input_tasks: The scanned tasks with no information removed
        :param input_playbooks: The scanned playbooks with plays that have no information removed
        :param scan_time: Time taken to do a scan
        :return: Result object
        """
        scan_result = cls(
            uuid=response_json.get("id", ""),
            user=response_json.get("user", ""),
            user_info=response_json.get("user_info", {}),
            project=response_json.get("project", ""),
            organization=response_json.get("organization", ""),
            environment=response_json.get("environment", {}),
            scan_date=response_json.get("scan_date", ""),
            subscription=response_json.get("subscription", ""),
            is_paid=response_json.get("is_paid", False),
            web_urls=response_json.get("web_urls", {}),
            summary=Summary(
                scan_time=scan_time, num_errors=0, num_warnings=0, num_hints=0, status=response_json.get("status", "")
            ),
            scan_progress=Progress.from_api_response_element(response_json.get("scan_progress", {})),
            check_results=[],
            fixed_check_results=[],
        )
        scan_result.parse_check_results(response_json, input_tasks, input_playbooks, input_inventories, input_variables)
        return scan_result

    @staticmethod
    def _parse_known_check_result(
        element: Dict[str, Any], input_items: Dict[str, Dict[str, Any]]
    ) -> Optional[CheckResult]:
        check_type: CheckType = CheckType.from_string(element.get("check_type", ""))
        good_check_types = [CheckType.TASK, CheckType.PLAY, CheckType.INVENTORY, CheckType.VARIABLE]
        if check_type not in good_check_types:
            print(
                f"Error: incorrect check type '{check_type}'. Should be one of {good_check_types}.",
                file=sys.stderr,
            )
            sys.exit(2)

        correlation_id = element.get("correlation_id")
        if not correlation_id:
            print(
                "Error: correlation id for result was not set. This should not happen for a task or play.",
                file=sys.stderr,
            )
            sys.exit(2)

        # guard against incomplete results where we don't match a task or play
        original_item = input_items.get(correlation_id)
        if not original_item:
            print("Could not map task ID to its original task.")
            return None

        # guard against missing task or play args and metadata
        item_meta = original_item.get("spotter_metadata", None)
        if not item_meta:
            print("Meta data is missing.")
            return None

        suggestion = element.get("suggestion", "")
        item_metadata_object = ItemMetadata.from_item_meta(item_meta)
        display_level = DisplayLevel.from_string(element.get("level", ""))

        suggestion_object: Optional[RewriteSuggestion] = RewriteSuggestion.from_item(
            check_type, original_item, suggestion, display_level
        )

        result = CheckResult(
            correlation_id=correlation_id,
            original_item=original_item,
            metadata=item_metadata_object,
            catalog_info=CheckCatalogInfo.from_api_response_element(element),
            level=display_level,
            message=element.get("message", ""),
            suggestion=suggestion_object,
            doc_url=element.get("doc_url", ""),
            check_type=check_type,
        )
        return result

    @staticmethod
    def _parse_unknown_check_result(element: Dict[str, Any]) -> CheckResult:
        check_type = CheckType.from_string(element.get("check_type", ""))
        display_level = DisplayLevel.from_string(element.get("level", ""))
        check_catalog_info = CheckCatalogInfo.from_api_response_element(element)

        result = CheckResult(
            correlation_id="",
            original_item={},
            metadata=None,
            catalog_info=check_catalog_info,
            level=display_level,
            message=element.get("message", ""),
            suggestion=None,
            doc_url=element.get("doc_url", ""),
            check_type=check_type,
        )
        return result

    def parse_check_results(
        self,
        response_json: Dict[str, Any],
        input_tasks: List[Dict[str, Any]],
        input_playbooks: List[Dict[str, Any]],
        input_inventories: List[Dict[str, Any]],
        input_variables: List[Dict[str, Any]],
    ) -> None:
        """
        Parse result objects and map tasks with complete information.

        :param response_json: The backend API response in JSON format
        :param input_tasks: The scanned tasks with no information removed
        :param input_playbooks: The scanned playbooks with plays that have no information removed
        """
        tasks_as_dict = {x["task_id"]: x for x in input_tasks if "task_id" in x}
        plays_as_dict = {}
        inventories_as_dict = {x["dynamic_inventory_id"]: x for x in input_inventories if "dynamic_inventory_id" in x}
        variables_as_dict = {x["variable_id"]: x for x in input_variables if "variable_id" in x}
        for playbook in input_playbooks:
            plays_as_dict.update({x["play_id"]: x for x in playbook["plays"] if "play_id" in x})

        result: List[CheckResult] = []
        for element in response_json.get("elements", []):
            check_type = CheckType.from_string(element.get("check_type", ""))
            item: Optional[CheckResult] = None

            if check_type == CheckType.TASK:
                item = self._parse_known_check_result(element, tasks_as_dict)
            elif check_type == CheckType.PLAY:
                item = self._parse_known_check_result(element, plays_as_dict)
            elif check_type == CheckType.INVENTORY:
                item = self._parse_known_check_result(element, inventories_as_dict)
            elif check_type == CheckType.VARIABLE:
                item = self._parse_known_check_result(element, variables_as_dict)
            else:
                item = self._parse_unknown_check_result(element)

            if item:
                self.summary.update(item)
                result.append(item)
        self.check_results = result

    def filter_check_results(self, threshold: DisplayLevel) -> None:
        """
        Filter a list of check results by only keeping tasks over a specified severity level.

        :param threshold: The DisplayLevel object as threshold (inclusive) of what level messages (and above) to keep
        """
        self.check_results = [cr for cr in self.check_results if cr.level.value >= threshold.value]

    @staticmethod
    def _get_sort_key(check_result: CheckResult) -> Tuple[str, int, int, int]:
        """
        Extract a tuple of file name, line number, column number and negative display level from check result.

        This is a key function for sorting check results.

        :param check_result: CheckResult object
        :return: A tuple of file name, line number, column number, and negative display level
        """
        if not check_result.metadata:
            return "", 0, 0, 0
        return (
            check_result.metadata.file_name,
            int(check_result.metadata.line),
            int(check_result.metadata.column),
            -check_result.level.value,
        )

    def sort_check_results(self) -> None:
        """Sort a list of check results by file names (alphabetically) and also YAML line and column numbers."""
        self.check_results.sort(key=self._get_sort_key)

    def apply_check_result_suggestions(self, display_level: DisplayLevel, scan_paths: List[Path]) -> None:
        """
        Automatically apply suggestions.

        :param display_level: DisplayLevel object
        """
        all_suggestions = [cr.suggestion for cr in self.check_results if cr.suggestion is not None]
        applied_suggestions = set(update_files(all_suggestions, display_level, scan_paths))
        self.fixed_check_results = [
            cr for cr in self.check_results if cr.suggestion is not None and cr.suggestion in applied_suggestions
        ]
        fixed_set = set(self.fixed_check_results)
        self.check_results = [cr for cr in self.check_results if cr not in fixed_set]
