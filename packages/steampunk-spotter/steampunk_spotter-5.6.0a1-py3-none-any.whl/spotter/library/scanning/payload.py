"""Provide scan payload model."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from pydantic_core import to_jsonable_python

from spotter.library.environment import Environment, EnvironmentV3, Statistics
from spotter.library.parsing.parsing import ParsingResult


class Payload(BaseModel):
    tasks: List[Dict[str, Any]]
    playbooks: List[Dict[str, Any]]

    def to_json_file(self, export_path: Path) -> None:
        """
        Export scan payload to JSON file.

        :param export_path: File path to export to (will be overwritten if exists)
        """
        try:
            with export_path.open("w", encoding="utf-8") as export_file:
                json.dump(to_jsonable_python(self), export_file, indent=2)
        except TypeError as e:
            print(f"Error: {e!s}", file=sys.stderr)
            sys.exit(2)


class PayloadV3(Payload):
    """A container for information about the scan payload/input."""

    environment: EnvironmentV3


class PayloadV4(Payload):
    environment: Environment
    dynamic_inventories: Optional[List[Dict[str, Any]]] = None
    roles: Optional[List[Dict[str, Any]]] = None
    blocks: Optional[List[Dict[str, Any]]] = None
    plugins: Optional[List[Dict[str, Any]]] = None
    variables: Optional[List[Dict[str, Any]]] = None
    statistics: Optional[Statistics] = None

    @staticmethod
    def task_as_payload_v3(task: Dict[str, Any]) -> Dict[str, Any]:
        task_cloned = dict(task)
        task_cloned.pop("block_id", None)
        return task_cloned

    def as_payload_v3(self) -> PayloadV3:
        environment_v3 = EnvironmentV3(
            python_version=self.environment.python_version,
            ansible_version=self.environment.ansible_version,
            installed_collections=self.environment.installed_collections,
            ansible_config=self.environment.ansible_config,
            galaxy_yml=self.environment.galaxy_yml,
            collection_requirements=self.environment.collection_requirements,
            cli_scan_args=self.environment.cli_scan_args,
        )
        tasks = [self.task_as_payload_v3(x) for x in self.tasks]
        return PayloadV3(environment=environment_v3, tasks=tasks, playbooks=self.playbooks)

    @classmethod
    def from_args(
        cls,
        parsing_result: ParsingResult,
        environment: Environment,
        include_metadata: bool,
        exclude_environment: bool,
        import_payload: Optional[Path],
    ) -> "PayloadV4":
        """
        Convert CLI arguments to ScanPayload object.

        :param parsing_result: ParsingResult object
        :param environment: Environment object
        :param include_metadata: Upload metadata (i.e., file names, line and column numbers)
        :param exclude_environment: Omit uploading environment data
        (i.e., installed collections and roles, installed pip packages, ansible config)
        :param import_payload: Path to file where ScanPayload can be imported from
        :return: ScanPayload object
        """
        if import_payload:
            return cls.from_json_file(import_payload)

        tasks = (
            parsing_result.tasks_with_relative_path_to_cwd()
            if include_metadata
            else parsing_result.tasks_without_metadata()
        )
        playbooks = (
            parsing_result.playbooks_with_relative_path_to_cwd()
            if include_metadata
            else parsing_result.playbooks_without_metadata()
        )

        blocks = parsing_result.clean_blocks(include_metadata)
        dynamic_inventories = parsing_result.clean_inventory(include_metadata)
        roles = parsing_result.clean_roles(include_metadata)
        plugins = parsing_result.clean_plugins(include_metadata)
        variables = parsing_result.clean_variables(include_metadata)
        statistics = parsing_result.clean_statistics(include_metadata)

        if exclude_environment:
            environment.ansible_config = {}
            environment.installed_collections = []
            environment.installed_roles = []
            environment.installed_pip_packages = []
        return PayloadV4(
            environment=environment.clean(include_metadata),
            tasks=tasks,
            playbooks=playbooks,
            blocks=blocks,
            dynamic_inventories=dynamic_inventories,
            roles=roles,
            plugins=plugins,
            variables=variables,
            statistics=statistics,
        )

    @classmethod
    def from_json_file(cls, import_path: Path) -> "PayloadV4":
        """
        Load ScanPayload object from JSON file.

        :param import_path: File path with JSON to import from
        :return: ScanPayload object holding input tuple (environment, tasks, playbooks)
        """
        try:
            if not import_path.exists():
                print(f"Error: import file at {import_path} does not exist.", file=sys.stderr)
                sys.exit(2)

            with import_path.open("r", encoding="utf-8") as import_file:
                scan_payload = json.load(import_file)
                environment_dict = scan_payload.get("environment", None)
                environment = Environment(**environment_dict) if environment_dict is not None else Environment()

                statistics_dict = scan_payload.get("statistics", None)
                statistics = Statistics(**statistics_dict) if statistics_dict is not None else None
                return cls(
                    environment=environment,
                    tasks=scan_payload.get("tasks", []),
                    playbooks=scan_payload.get("playbooks", []),
                    dynamic_inventories=scan_payload.get("dynamic_inventories", []),
                    roles=scan_payload.get("roles", []),
                    plugins=scan_payload.get("plugins", []),
                    variables=scan_payload.get("variables", []),
                    statistics=statistics,
                )
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error: {e!s}", file=sys.stderr)
            sys.exit(2)
