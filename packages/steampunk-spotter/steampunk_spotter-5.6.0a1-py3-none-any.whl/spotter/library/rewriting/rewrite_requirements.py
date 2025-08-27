"""Logic for requirements rewriting."""

from pathlib import Path
from typing import Dict, List, Tuple

import ruamel.yaml as ruamel

from spotter.library.environment import Environment
from spotter.library.rewriting.models import INodeSuggestion
from spotter.library.scanning.display_level import DisplayLevel


def update_requirements(inodes: List[INodeSuggestion], display_level: DisplayLevel, scan_paths: List[Path]) -> None:
    """
    Update requirements.yml file.

    :param inodes: List of INodeSuggestion objects
    :param display_level: DisplayLevel object
    """
    requirements_yml_path = Environment.get_candidate_requirements_path(scan_paths[0] if scan_paths else Path.cwd())
    if not requirements_yml_path:
        # TODO: there should always be at least one path, so this shound not appen
        return

    requirements_update_suggestions: Dict[Path, set[Tuple[str, str]]] = {}
    for inode in inodes:
        for suggestion in inode.suggestions:
            if not suggestion.is_fix_requirements:
                continue
            if display_level.value > suggestion.display_level.value:
                continue

            suggestion_dict = suggestion.suggestion_spec
            collection_name = suggestion_dict["data"]["collection_name"]
            collection_version = suggestion_dict["data"]["version"]
            # TODO: update path when we are able to get it from scan input or scan result
            bucket = requirements_update_suggestions.get(requirements_yml_path, set())
            bucket.add((collection_name, collection_version))
            requirements_update_suggestions[requirements_yml_path] = bucket

    # TODO: consider updating this when we will be updating detection and rewriting of collection requirements
    for requirements_yml_path, collections in requirements_update_suggestions.items():
        with requirements_yml_path.open("a+", encoding="utf-8") as requirements_file:
            # TODO: what should be done if same collection is listed with different versions
            try:
                requirements_file.seek(0)
                yaml = ruamel.YAML(typ="safe", pure=True)
                data = yaml.load(requirements_file)
            except ruamel.YAMLError:
                # overwrite erroneous requirement file
                data = None
            if not data:
                data = {}
            if not isinstance(data, dict):
                # should we overwrite in this case as well?
                continue
            if "collections" not in data or ("collections" in data and data["collections"] is None):
                data["collections"] = []

            for collection_name, collection_version in sorted(collections):
                data["collections"].append({"name": collection_name, "version": collection_version})

            requirements_file.seek(0)
            requirements_file.truncate()

            yaml = ruamel.YAML(typ="rt")
            yaml.indent(mapping=2, sequence=4, offset=2)
            yaml.dump(data, requirements_file)
