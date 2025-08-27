"""Provide methods for parsing Ansible artifacts."""

import re
import sys
import uuid
from enum import Enum
from multiprocessing import Pool
from pathlib import Path
from typing import Any, ClassVar, Dict, Iterable, List, Optional, Set, Tuple, Union, cast

import ruamel.yaml as ruamel
from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.settings import default_settings
from pydantic import BaseModel
from pydantic_core import to_jsonable_python
from ruamel.yaml.comments import TaggedScalar
from ruamel.yaml.scalarint import BinaryInt, HexCapsInt, HexInt, OctalInt
from ruamel.yaml.scanner import MarkedYAMLError

from spotter.library.environment import Statistics
from spotter.library.parsing.noqa_comments import match_comments_with_task
from spotter.library.scanning.parser_error import YamlErrorDetails
from spotter.library.utils import get_relative_path_to_cwd


class SpotterObfuscated(BaseModel):
    """Class where we save metadata about which fields were obfuscated."""

    type: str
    path: List[Union[int, str]]

    def to_parent(self, path_item: Union[int, str]) -> "SpotterObfuscated":
        """
        Create new object which contains also parent path.

        :param path_item: Path that needs to be inserted at the beginning
        :return: SpotterObfuscated with added parent path
        """
        temp = cast(List[Union[int, str]], [path_item])
        return SpotterObfuscated(type=self.type, path=temp + self.path)


ObfuscatedInput = List[SpotterObfuscated]

# TODO: Rethink if we need to allow parsing and scanning files with other suffixes
YAML_SUFFIXES = (".yml", ".yaml")


class ParsingResult(BaseModel):
    """A container for information about the parsed Ansible artifacts."""

    tasks: List[Dict[str, Any]]
    playbooks: List[Dict[str, Any]]
    blocks: List[Dict[str, Any]]
    dynamic_inventories: List[Dict[str, Any]]
    roles: List[Dict[str, Any]]
    plugins: List[Dict[str, Any]]
    variables: List[Dict[str, Any]]
    errors: List[YamlErrorDetails]
    included_files_count: int
    excluded_paths_count: int
    path_loops_detected: int

    def tasks_with_relative_path_to_cwd(self) -> List[Dict[str, Any]]:
        """
        Use relative file paths in input tasks.

        :return: Updated tasks with relative paths to cwd
        """
        tasks = self.tasks.copy()
        for t in tasks:
            relative_path = get_relative_path_to_cwd(t["spotter_metadata"]["file"])
            if relative_path:
                t["spotter_metadata"]["file"] = relative_path

        return tasks

    def playbooks_with_relative_path_to_cwd(self) -> List[Dict[str, Any]]:
        """
        Use relative file paths in input playbooks.

        :return: Updated playbooks with relative paths to cwd
        """
        playbooks = self.playbooks.copy()
        for playbook in playbooks:
            for play in playbook["plays"]:
                relative_path = get_relative_path_to_cwd(play["spotter_metadata"]["file"])
                if relative_path:
                    play["spotter_metadata"]["file"] = relative_path

        return playbooks

    def tasks_without_metadata(self) -> List[Dict[str, Any]]:
        """
        Remove sensitive data from input tasks.

        :return: Cleaned list of input tasks
        """
        return [
            {
                "task_id": t["task_id"],
                "play_id": t["play_id"],
                "task_args": t["task_args"],
                "spotter_noqa": t["spotter_noqa"],
            }
            for t in self.tasks
        ]

    def playbooks_without_metadata(self) -> List[Dict[str, Union[str, List[Dict[str, Any]]]]]:
        """
        Remove sensitive data from input playbooks.

        :return: Cleaned list of input playbooks
        """
        return [
            {
                "playbook_id": t["playbook_id"],
                "plays": [{"play_id": x.get("play_id", None), "play_args": x["play_args"]} for x in t["plays"]],
            }
            for t in self.playbooks
        ]

    @staticmethod
    def copy_fields(source: Dict[str, Any], use_fields: List[str]) -> Dict[str, Any]:
        result = {x: source[x] for x in use_fields}
        return result

    def clean_items(
        self, use_fields: List[str], items: List[Dict[str, Any]], include_metadata: bool
    ) -> List[Dict[str, Any]]:
        if not include_metadata:
            return [self.copy_fields(i, use_fields) for i in items]
        for i in items:
            relative_path = get_relative_path_to_cwd(i["spotter_metadata"]["file"])
            if relative_path:
                i["spotter_metadata"]["file"] = relative_path
        return items

    def clean_blocks(self, include_metadata: bool) -> List[Dict[str, Union[str, List[Dict[str, Any]]]]]:
        fields = ["block_id", "block_parent_id"]
        return self.clean_items(fields, self.blocks, include_metadata)

    def clean_inventory(self, include_metadata: bool) -> List[Dict[str, Union[str, List[Dict[str, Any]]]]]:
        fields = ["dynamic_inventory_id", "dynamic_inventory_args"]
        return self.clean_items(fields, self.dynamic_inventories, include_metadata)

    def clean_roles(self, include_metadata: bool) -> List[Dict[str, Optional[str]]]:
        fields = ["role_id", "role_name", "role_argument_specification"]
        return self.clean_items(fields, self.roles, include_metadata)

    def clean_plugins(self, include_metadata: bool) -> List[Dict[str, Optional[str]]]:
        fields = ["plugin_id", "plugin_name", "plugin_type", "plugin_specification"]
        return self.clean_items(fields, self.plugins, include_metadata)

    def clean_variables(self, include_metadata: bool) -> List[Dict[str, Optional[str]]]:
        fields = ["variable_id", "variable_args"]
        return self.clean_items(fields, self.variables, include_metadata)

    def clean_statistics(self, include_metadata: bool) -> Optional[Statistics]:
        if not include_metadata:
            return None
        return Statistics(
            included_files_count=self.included_files_count,
            excluded_paths_count=self.excluded_paths_count,
            path_loops_detected=self.path_loops_detected,
        )


class ScalarBool:
    def __init__(self, bool_value: bool, original_value: str) -> None:
        self.bool_value = bool_value
        self.original_value = original_value

    def __str__(self) -> str:
        return str(self.bool_value)


class ScalarBoolYes(ScalarBool):
    pass


class ScalarBoolNo(ScalarBool):
    pass


class ScalarBoolfactory:
    @staticmethod
    def from_string(value: Any, parsed_value: bool) -> Union[ScalarBool, bool]:
        if value in ["True", "yes", "y", "On", "on"]:
            return ScalarBoolYes(parsed_value, value)
        if value in ["False", "no", "n", "Off", "off"]:
            return ScalarBoolNo(parsed_value, value)
        return parsed_value


class ScalarTimestamp:
    def __init__(self, str_value: str) -> None:
        self.str_value = str_value


class SafeLineConstructor(ruamel.RoundTripConstructor):  # type: ignore
    """YAML loader that adds line numbers."""

    def __init__(self, preserve_quotes: Optional[bool] = None, loader: Any = None) -> None:
        super().__init__(preserve_quotes, loader)

        # add constructors for !vault and !unsafe tags, throw away their values because they are sensitive
        def construct_unsafe_or_vault(loader: ruamel.SafeLoader, node: ruamel.Node) -> Any:  # noqa: ARG001  # mandatory
            ## TODO: All data that is thrown away here should be included in spotter_obfuscated part.
            ## Implemenatition that I se at the moment is that we skip processing here, and just extend code inside
            ## _remove_secret_parameter_values method. Since we handle ints and bools there, we should be able to
            ## handle this as well.
            return None

        self.add_constructor("!unsafe", construct_unsafe_or_vault)
        self.add_constructor("!vault", construct_unsafe_or_vault)
        self.add_constructor("tag:yaml.org,2002:bool", self.construct_yaml_sbool)
        self.add_constructor("tag:ruamel.org,2002:timestamp", ruamel.SafeLoader.construct_yaml_str)

    def construct_yaml_sbool(self, tmp: Any, node: Any = None) -> Any:  # noqa: ARG002  # mandatory signature
        value = super().construct_yaml_sbool(node)
        return ScalarBoolfactory.from_string(node.value, value)

    # TODO: Method is not called even if timestamp tag is rewired to us
    def construct_yaml_timestamp(self, node: Any, values: Any = None) -> Any:  # noqa: ARG002
        value = super().construct_yaml_str(node)
        return ScalarTimestamp(value)

    def construct_mapping(self, node: ruamel.MappingNode, maptyp: Any, deep: bool = False) -> Dict[Any, Any]:
        """
        Overridden the original construct_mapping method.

        :param node: YAML node object
        :param maptyp: YAML map type
        :param deep: Build objects recursively
        :return: A dict with loaded YAML
        """
        try:
            super().construct_mapping(node, maptyp, deep=deep)
        except TypeError as ex:
            raise MarkedYAMLError(
                problem='Cannot parse YAML element. Frequent reason for this error is missing quotes around Jinja reference, e.g., {{ var_name }} that should be "{{ var_name }}".',
                problem_mark=node.start_mark,
            ) from ex

        meta = {}
        meta["__line__"] = node.start_mark.line + 1
        meta["__column__"] = node.start_mark.column + 1
        meta["__start_mark_index__"] = node.start_mark.index
        meta["__end_mark_index__"] = node.end_mark.index
        for key in list(maptyp.keys()):
            if isinstance(key, ScalarBool):
                value = maptyp[key]
                del maptyp[key]
                maptyp[key.original_value] = value

        maptyp["__meta__"] = meta
        return maptyp  # type: ignore


class AnsibleArtifact(Enum):
    """Enum that can distinct between different Ansible artifacts (i.e., types of Ansible files)."""

    TASK = 1
    PLAYBOOK = 2
    ROLE = 3
    COLLECTION = 4


class _PlaybookKeywords:
    """
    Enum that stores significant keywords for playbooks that help us automatically discover Ansible file types.

    Keywords were gathered from: https://docs.ansible.com/ansible/latest/reference_appendices/playbooks_keywords.html.
    """

    PLAY: ClassVar[Set[str]] = {
        "any_errors_fatal",
        "become",
        "become_exe",
        "become_flags",
        "become_method",
        "become_user",
        "check_mode",
        "collections",
        "connection",
        "debugger",
        "diff",
        "environment",
        "fact_path",
        "force_handlers",
        "gather_facts",
        "gather_subset",
        "gather_timeout",
        "handlers",
        "hosts",
        "ignore_errors",
        "ignore_unreachable",
        "max_fail_percentage",
        "module_defaults",
        "name",
        "no_log",
        "order",
        "port",
        "post_tasks",
        "pre_tasks",
        "remote_user",
        "roles",
        "run_once",
        "serial",
        "strategy",
        "tags",
        "tasks",
        "throttle",
        "timeout",
        "vars",
        "vars_files",
        "vars_prompt",
    }
    ROLE: ClassVar[Set[str]] = {
        "any_errors_fatal",
        "become",
        "become_exe",
        "become_flags",
        "become_method",
        "become_user",
        "check_mode",
        "collections",
        "connection",
        "debugger",
        "delegate_facts",
        "delegate_to",
        "diff",
        "environment",
        "ignore_errors",
        "ignore_unreachable",
        "module_defaults",
        "name",
        "no_log",
        "port",
        "remote_user",
        "run_once",
        "tags",
        "throttle",
        "timeout",
        "vars",
        "when",
    }
    BLOCK: ClassVar[Set[str]] = {
        "always",
        "any_errors_fatal",
        "become",
        "become_exe",
        "become_flags",
        "become_method",
        "become_user",
        "block",
        "check_mode",
        "collections",
        "connection",
        "debugger",
        "delegate_facts",
        "delegate_to",
        "diff",
        "environment",
        "ignore_errors",
        "ignore_unreachable",
        "module_defaults",
        "name",
        "no_log",
        "notify",
        "port",
        "remote_user",
        "rescue",
        "run_once",
        "tags",
        "throttle",
        "timeout",
        "vars",
        "when",
    }
    TASK: ClassVar[Set[str]] = {
        "action",
        "any_errors_fatal",
        "args",
        "async",
        "become",
        "become_exe",
        "become_flags",
        "become_method",
        "become_user",
        "changed_when",
        "check_mode",
        "collections",
        "connection",
        "debugger",
        "delay",
        "delegate_facts",
        "delegate_to",
        "diff",
        "environment",
        "failed_when",
        "ignore_errors",
        "ignore_unreachable",
        "local_action",
        "loop",
        "loop_control",
        "module_defaults",
        "name",
        "no_log",
        "notify",
        "poll",
        "port",
        "register",
        "remote_user",
        "retries",
        "run_once",
        "tags",
        "throttle",
        "timeout",
        "until",
        "vars",
        "when",
    }


def _safe_remove_dashes(yaml_text: str) -> str:
    lines = yaml_text.splitlines(True)
    for i, line in enumerate(lines):
        trimmed = line.lstrip()
        if trimmed.startswith("#"):
            continue
        if trimmed.startswith("---"):
            before = "".join(lines[0:i])
            actual_line = re.sub(r"^(\s*?)---", r"\1   ", line, count=1)
            after = "".join(lines[i + 1 :])
            result = before + actual_line + after
            return result
        break
    return yaml_text


def _load_yaml_file(path: Path) -> Tuple[Any, List[YamlErrorDetails]]:
    """
    Load YAML file and return corresponding Python object if parsing has been successful.

    :param path: Path to YAML file
    :return: Parsed YAML file as a Python object
    """
    try:
        yaml_text = path.read_text(encoding="utf-8")

        # remove document start to prevent ruamel changing the YAML version to 1.2
        yaml_text = _safe_remove_dashes(yaml_text)
        yaml = ruamel.YAML(typ="rt")
        yaml.Constructor = SafeLineConstructor
        yaml.version = (1, 1)
        return yaml.load(yaml_text), []
    except MarkedYAMLError as e:
        if e.problem_mark:
            mark = e.problem_mark
            description = e.problem
        elif e.context_mark:
            mark = e.context_mark
            description = e.context
        if not mark:
            print(f"Something went wrong when parsing:\n{path.name}: {e}", file=sys.stderr)
            return None, []
        return None, [
            YamlErrorDetails(
                column=mark.column,
                index=mark.index,
                line=mark.line + 1,
                description=description,
                file_path=path,
            )
        ]
    except ruamel.YAMLError as e:
        print(f"{path.name}: {e}", file=sys.stderr)
        return None, []
    except UnicodeDecodeError as e:
        print(f"{path.name}: {e}", file=sys.stderr)
        return None, []
    except Exception as e:  # noqa: BLE001  # safety catchall since we're handling unknown inputs
        print(f"{path.name}: {e}", file=sys.stderr)
        return None, []


def _is_playbook(loaded_yaml: Any) -> bool:
    """
    Check if file is a playbook = a YAML file containing one or more plays in a list.

    :param loaded_yaml: Parsed YAML file as a Python object
    :return: True or False
    """
    # use only keywords that are unique for play and do not intersect with other keywords
    playbook_keywords = _PlaybookKeywords.PLAY.difference(
        _PlaybookKeywords.TASK.union(_PlaybookKeywords.BLOCK).union(_PlaybookKeywords.ROLE)
    )

    return isinstance(loaded_yaml, list) and any(
        len(playbook_keywords.intersection(e.keys())) > 0 for e in loaded_yaml if isinstance(e, dict)
    )


def _is_requirements(loaded_yaml: Any) -> bool:
    """
    Check if file is a requirements file (which is sometimes structurally similar to a playbook).

    https://docs.ansible.com/ansible/latest/galaxy/user_guide.html#installing-multiple-roles-from-a-file

    :param loaded_yaml: Parsed YAML file as a Python object
    :return: True or False
    """
    if not loaded_yaml:
        return False

    allowed_keys = ["roles", "collections"]
    if isinstance(loaded_yaml, dict):
        if any(x not in allowed_keys for x in loaded_yaml):
            return False
    elif not isinstance(loaded_yaml, list):
        return False

    allowed_role_keys = ["name", "scm", "src", "version"]
    return all(
        not any(x not in allowed_role_keys and not x.startswith("_") for x in item or []) for item in loaded_yaml
    )


def _is_dynamic_inventory(loaded_yaml: Any) -> bool:
    """
    Check if file is a dynamic inventory definition.

    :param loaded_yaml: Parsed YAML file as a Python object
    :return: True or False
    """
    if not isinstance(loaded_yaml, dict):
        return False
    return "plugin" in loaded_yaml


def is_var_file(loaded_yaml: Any) -> bool:
    """
    Check if file is vars file.

    :param loaded_yaml: Parsed YAML file as a Python object
    :return: True or False
    """
    return isinstance(loaded_yaml, dict)


def _is_role(directory: Path) -> bool:
    """
    Check if directory is a role = a directory with at least one of eight main standard directories.

    :param directory: Path to directory
    :return: True or False
    """
    standard_role_directories = ["tasks", "handlers", "library", "defaults", "vars", "files", "templates", "meta"]

    return any((directory / d).exists() for d in standard_role_directories)


def _is_collection(directory: Path) -> bool:
    """
    Check if directory is a collection = a directory with galaxy.yml or roles or plugins.

    :param directory: Path to directory
    :return: True or False
    """
    return (directory / "galaxy.yml").exists() or (directory / "roles").exists() or (directory / "plugins").exists()


def _clean_action_and_local_action(task: Dict[str, Any], parse_values: bool = False) -> None:
    """
    Handle parsing Ansible task that include action or local_action keys.

    This is needed because tasks from action or local_action have different syntax and need to be cleaned to look the
    same as other tasks.

    :param task: Ansible task
    :param parse_values: True if also read values (apart from parameter names) from task parameters, False if not
    :return: Cleaned Ansible task
    """
    # TODO: Remove this spaghetti when API will be able to parse action plugins
    if parse_values:
        # server handles that case already
        return

    if not isinstance(task, dict):
        # probably inlined - we do not cover that case without parsed values
        return

    if not ("action" in task or "local_action" in task):
        # nothing to do
        return

    # replace action or local_action with the name of the module they contain and set delegate_to for local_action
    verb = "action" if "action" in task else "local_action"
    dict_with_module = next((d for d in list(task.values()) if isinstance(d, dict) and "module" in d), None)
    if dict_with_module is not None:
        module_name = dict_with_module.pop("module", None)
        action = task.pop(verb, None)
        task[module_name] = action
        if verb == "local_action":
            task["delegate_to"] = None


def _remove_deep_metadata(task: Any) -> Any:
    """
    Remove nested metadata.

    :param task: Ansible task
    :return: Updated Ansible task
    """
    if not task:
        return task

    if isinstance(task, dict):
        return {k: _remove_deep_metadata(v) for k, v in task.items() if k != "__meta__"}

    if isinstance(task, list):
        return [_remove_deep_metadata(x) for x in task]

    return task


def _remove_parameter_values(task: Dict[str, Any], params_to_keep: Optional[List[str]] = None) -> None:
    """
    Remove parameter values from Ansible tasks.

    :param task: Ansible task
    :param params_to_keep: List of parameters that should not be removed
    """
    for task_key in task:
        if isinstance(task[task_key], dict):
            for key in list(task[task_key]):
                if task_key in ["action", "local_action"] and key == "module":
                    continue
                if key != "__meta__":
                    task[task_key][key] = None
        elif not params_to_keep or task_key not in params_to_keep:
            task[task_key] = None


def detect_secrets_in_file(file_name: str, skip_detect_secrets: bool) -> List[str]:
    """
    Detect secret parameter values (e.g., passwords, SSH keys, API tokens, cloud credentials, etc.) in the file.

    :param file_name: Name of the original file with tasks
    :return: List of secrets as strings
    """
    if skip_detect_secrets:
        return []

    secrets_collection = SecretsCollection()
    with default_settings():
        secrets_collection.scan_file(file_name)
        return [
            secret.secret_value
            for secret_set in secrets_collection.data.values()
            for secret in secret_set
            if secret.secret_value
        ]


def _remove_secret_parameter_from_dict(yaml_key: Dict[str, Any], secrets: List[str]) -> Tuple[Any, ObfuscatedInput]:
    obfuscated: ObfuscatedInput = []
    result = {}
    for key, value in yaml_key.items():
        cleaned, items = _remove_secret_parameter_values(value, secrets)
        result[key] = cleaned
        obfuscated.extend(item.to_parent(key) for item in items)
    return result, obfuscated


def _remove_secret_parameter_from_list(yaml_key: List[Any], secrets: List[str]) -> Tuple[Any, ObfuscatedInput]:
    obfuscated: ObfuscatedInput = []
    result = []
    for key, value in enumerate(yaml_key):
        cleaned, items = _remove_secret_parameter_values(value, secrets)
        result.append(cleaned)
        obfuscated.extend(item.to_parent(key) for item in items)
    return result, obfuscated


def _remove_secret_parameter_values(  # noqa: PLR0911
    yaml_key: Any, secret_values: List[str]
) -> Tuple[Any, ObfuscatedInput]:
    """
    Remove secret parameter values from YAML.

    :param yaml_key: YAML key
    :param secret_values: List of detected secret values
    :return: Updated YAML key
    """
    if isinstance(yaml_key, dict):
        return _remove_secret_parameter_from_dict(yaml_key, secret_values)

    if isinstance(yaml_key, list):
        return _remove_secret_parameter_from_list(yaml_key, secret_values)

    if isinstance(yaml_key, str) and any(secret_value in yaml_key for secret_value in secret_values):
        return None, [SpotterObfuscated(type="str", path=[])]

    if isinstance(yaml_key, BinaryInt):
        return yaml_key, [SpotterObfuscated(type="BinaryInt", path=[])]
    if isinstance(yaml_key, OctalInt):
        return yaml_key, [SpotterObfuscated(type="OctalInt", path=[])]
    if isinstance(yaml_key, HexInt):
        return yaml_key, [SpotterObfuscated(type="HexInt", path=[])]
    if isinstance(yaml_key, HexCapsInt):
        return yaml_key, [SpotterObfuscated(type="HexCapsInt", path=[])]

    if isinstance(yaml_key, ScalarTimestamp):
        return yaml_key.str_value, [SpotterObfuscated(type="Timestamp", path=[])]

    if isinstance(yaml_key, ScalarBool):
        return yaml_key.bool_value, [SpotterObfuscated(type=yaml_key.__class__.__name__, path=[])]

    if isinstance(yaml_key, TaggedScalar):  # key: !!str '{sdgsgfdhfd}'
        return yaml_key.value, []

    if isinstance(yaml_key, bytes):  # key: !!binary | Base64....
        return None, [SpotterObfuscated(type="bytes", path=[])]

    if isinstance(yaml_key, str) and "\x00" in yaml_key:
        return yaml_key.replace("\x00", "\\u0000"), [SpotterObfuscated(type="EOF", path=[])]

    return yaml_key, []


def _parse_tasks(  # noqa: PLR0912  # TODO: oh dear
    tasks: List[Dict[str, Any]],
    file_name: str,
    parse_values: bool,
    play_id: Optional[str],
    block_id: Optional[str],
    skip_detect_secrets: bool,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Parse Ansible tasks and prepare them for scanning.

    :param tasks: List of Ansible task dicts
    :param file_name: Name of the original file with tasks
    :param parse_values: True if also read values (apart from parameter names) from task parameters, False if not
    :param play_id: Unique identifier for play that tasks belong to
    :param block_id: Unique identifier for block that tasks belong to
    :return: List of parsed Ansible tasks and blocks
    """
    try:
        parsed_tasks = []
        parsed_blocks = []
        secrets = detect_secrets_in_file(file_name, skip_detect_secrets)

        for task in [t for t in tasks if t is not None]:
            contains_block_section = False
            task_block_id = str(uuid.uuid4())
            for block_section in ("block", "rescue", "always"):
                if block_section in task:
                    contains_block_section = True
                    if isinstance(task[block_section], list):
                        block_tasks, block_blocks = _parse_tasks(
                            task[block_section], file_name, parse_values, play_id, task_block_id, skip_detect_secrets
                        )
                        parsed_tasks += block_tasks
                        parsed_blocks += block_blocks
            if contains_block_section:
                block_copy: Dict[str, Any] = dict(task)
                block_meta_raw = block_copy.pop("__meta__", None)
                block_noqa = block_copy.pop("__noqa__", [])
                block_copy.pop("block", [])
                block_copy.pop("rescue", [])
                block_copy.pop("always", [])
                block_obfuscated: ObfuscatedInput = []

                if not parse_values:
                    _remove_parameter_values(block_copy)
                else:
                    for block_key in block_copy:
                        block_copy[block_key], hidden = _remove_secret_parameter_values(block_copy[block_key], secrets)
                        block_obfuscated.extend(item.to_parent(block_key) for item in hidden)

                block_meta = {
                    "file": file_name,
                    "line": block_meta_raw["__line__"],
                    "column": block_meta_raw["__column__"],
                    "start_mark_index": block_meta_raw["__start_mark_index__"],
                    "end_mark_index": block_meta_raw["__end_mark_index__"],
                }
                block_dict = {
                    "block_id": task_block_id,
                    "block_args": _remove_deep_metadata(block_copy),
                    "parent_block_id": block_id,
                    "spotter_metadata": block_meta,
                    "spotter_obfuscated": [to_jsonable_python(x) for x in block_obfuscated],
                    "spotter_noqa": [to_jsonable_python(x) for x in block_noqa],
                }
                parsed_blocks.insert(0, block_dict)
                continue

            if isinstance(task, ruamel.CommentedMap):
                match_comments_with_task(task)

            task_copy: Dict[str, Any] = dict(task)
            task_meta = task_copy.pop("__meta__", None)
            task_noqa = task_copy.pop("__noqa__", [])
            obfuscated: ObfuscatedInput = []

            if not parse_values:
                _remove_parameter_values(task_copy)
            else:
                for task_key in task_copy:
                    task_copy[task_key], hidden = _remove_secret_parameter_values(task_copy[task_key], secrets)
                    obfuscated.extend(item.to_parent(task_key) for item in hidden)

            meta = {
                "file": file_name,
                "line": task_meta["__line__"],
                "column": task_meta["__column__"],
                "start_mark_index": task_meta["__start_mark_index__"],
                "end_mark_index": task_meta["__end_mark_index__"],
            }

            task_dict = {
                "task_id": str(uuid.uuid4()),
                "play_id": play_id,
                "block_id": block_id,
                "task_args": _remove_deep_metadata(task_copy),
                "spotter_metadata": meta,
                "spotter_obfuscated": [to_jsonable_python(x) for x in obfuscated],
                "spotter_noqa": [to_jsonable_python(x) for x in task_noqa],
            }
            parsed_tasks.append(task_dict)

        return parsed_tasks, parsed_blocks
    except Exception as e:  # noqa: BLE001  # safety catchall
        print(f"Error: parsing tasks from {file_name} failed: {e}", file=sys.stderr)
        return [], []


def _parse_dynamic_inventory(
    dynamic_inventory: Dict[str, Any], file_name: str, parse_values: bool, skip_detect_secrets: bool
) -> Dict[str, Any]:
    secrets = detect_secrets_in_file(file_name, skip_detect_secrets)

    if isinstance(dynamic_inventory, ruamel.CommentedMap):
        match_comments_with_task(dynamic_inventory)

    dynamic_inventory_copy: Dict[str, Any] = dict(dynamic_inventory)
    dynamic_inventory_meta = dynamic_inventory_copy.pop("__meta__", None)
    dynamic_inventory_noqa = dynamic_inventory_copy.pop("__noqa__", [])
    obfuscated: ObfuscatedInput = []

    if not parse_values:
        _remove_parameter_values(dynamic_inventory_copy, ["plugin", "plugin_type"])
    else:
        for key in dynamic_inventory_copy:
            dynamic_inventory_copy[key], hidden = _remove_secret_parameter_values(dynamic_inventory_copy[key], secrets)
            obfuscated.extend(item.to_parent(key) for item in hidden)

    meta = {
        "file": file_name,
        "line": dynamic_inventory_meta["__line__"],
        "column": dynamic_inventory_meta["__column__"],
        "start_mark_index": dynamic_inventory_meta["__start_mark_index__"],
        "end_mark_index": dynamic_inventory_meta["__end_mark_index__"],
    }
    parsed_dynamic_inventory = {
        "dynamic_inventory_id": str(uuid.uuid4()),
        "dynamic_inventory_args": _remove_deep_metadata(dynamic_inventory_copy),
        "spotter_metadata": meta,
        "spotter_obfuscated": [to_jsonable_python(x) for x in obfuscated],
        "spotter_noqa": [to_jsonable_python(x) for x in dynamic_inventory_noqa],
    }
    return parsed_dynamic_inventory


def _parse_vars(
    variables: Dict[str, Any], file_name: str, parse_values: bool, parse_vars: bool, skip_detect_secrets: bool
) -> List[Dict[str, Any]]:
    """
    Parse Ansible vars file prepare it for scanning.

    :param vars: Ansible vars dict
    :param file_name: Name of the original file with vars
    :return: Dict with parsed Ansible vars
    """
    secrets = detect_secrets_in_file(file_name, skip_detect_secrets)

    if isinstance(variables, ruamel.CommentedMap):
        match_comments_with_task(variables)

    variables_copy: Dict[str, Any] = dict(variables)
    variables_meta = variables_copy.pop("__meta__", None)
    variables_noqa = variables_copy.pop("__noqa__", [])
    obfuscated: ObfuscatedInput = []

    if not parse_values:
        _remove_parameter_values(variables_copy, ["plugin", "plugin_type"])
    else:
        for key in variables_copy:
            variables_copy[key], hidden = _remove_secret_parameter_values(variables_copy[key], secrets)
            obfuscated.extend(item.to_parent(key) for item in hidden)

    meta = {
        "file": file_name,
        "line": variables_meta["__line__"],
        "column": variables_meta["__column__"],
        "start_mark_index": variables_meta["__start_mark_index__"],
        "end_mark_index": variables_meta["__end_mark_index__"],
    }

    vars_dict = {
        "variable_id": str(uuid.uuid4()),
        "variable_args": _remove_deep_metadata(variables_copy) if parse_vars else None,
        "spotter_metadata": meta,
        "spotter_obfuscated": [to_jsonable_python(x) for x in obfuscated],
        "spotter_noqa": [to_jsonable_python(x) for x in variables_noqa],
    }
    return [vars_dict]


def _parse_play(
    play: Dict[str, Any], file_name: str, parse_values: bool, play_id: Optional[str], skip_detect_secrets: bool
) -> Dict[str, Any]:
    """
    Parse Ansible play and prepare it for scanning.

    :param play: Ansible play dict
    :param file_name: Name of the original file with play
    :param parse_values: True if also read values (apart from parameter names) from play parameters, False if not
    :param play_id: Unique identifier for this play
    :return: Dict with parsed Ansible play
    """
    try:
        play_meta = play.pop("__meta__", None)

        obfuscated: ObfuscatedInput = []
        if not parse_values:
            _remove_parameter_values(play, ["collections"])
        else:
            secrets = detect_secrets_in_file(file_name, skip_detect_secrets)
            for play_key in play:
                play[play_key], hidden = _remove_secret_parameter_values(play[play_key], secrets)
                obfuscated.extend(item.to_parent(play_key) for item in hidden)

        meta = {
            "file": file_name,
            "line": play_meta["__line__"],
            "column": play_meta["__column__"],
            "start_mark_index": play_meta["__start_mark_index__"],
            "end_mark_index": play_meta["__end_mark_index__"],
        }

        play_dict = {
            "play_id": play_id,
            "play_args": _remove_deep_metadata(play),
            "spotter_metadata": meta,
            "spotter_obfuscated": [to_jsonable_python(x) for x in obfuscated],
        }

        return play_dict
    except Exception as e:  # noqa: BLE001  # safety catchall
        print(f"Error: parsing play from {file_name} failed: {e}", file=sys.stderr)
        return {}


def _parse_playbook(
    playbook: List[Dict[str, Any]], file_name: str, parse_values: bool, skip_detect_secrets: bool
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Parse Ansible playbook and prepare it for scanning.

    :param playbook: Ansible playbook as dict
    :param file_name: Name of the original file with playbook
    :param parse_values: True if also read values (apart from parameter names) from task parameters, False if not
    :return: Tuple containing list of parsed Ansible tasks and parsed playbook as dict
    """
    parsed_tasks = []
    parsed_plays = []
    parsed_blocks = []
    for play in [p for p in playbook if p is not None]:
        tasks = play.pop("tasks", [])
        pre_tasks = play.pop("pre_tasks", [])
        post_tasks = play.pop("post_tasks", [])
        handlers = play.pop("handlers", [])

        all_tasks = ruamel.CommentedSeq()
        if isinstance(tasks, list):
            all_tasks.extend(tasks)
        if isinstance(pre_tasks, list):
            all_tasks.extend(pre_tasks)
        if isinstance(post_tasks, list):
            all_tasks.extend(post_tasks)
        if isinstance(handlers, list):
            all_tasks.extend(handlers)

        play_id = str(uuid.uuid4())
        item_tasks, item_blocks = _parse_tasks(all_tasks, file_name, parse_values, play_id, None, skip_detect_secrets)
        parsed_tasks += item_tasks
        parsed_blocks += item_blocks
        parsed_plays.append(_parse_play(play, file_name, parse_values, play_id, skip_detect_secrets))

    parsed_playbook = {"playbook_id": str(uuid.uuid4()), "plays": parsed_plays}
    return parsed_tasks, parsed_blocks, [parsed_playbook]


def _parse_role(
    directory: Path,
    parse_values: bool = False,  # noqa: ARG001  # TODO: there is a test for parse_values here but the param isn't used?
) -> Tuple[Dict[str, Any], List[YamlErrorDetails]]:
    """
    Parse Ansible role.

    :param directory: Role directory
    :param parse_values: True if also read values (apart from parameter names) from task parameters, False if not
    :return: Tuple containing list of parsed Ansible tasks and parsed playbook as dict
    """
    parsed_errors = []

    # read role specification
    arg_spec_file = directory / "meta" / "argument_specs.yml"
    if arg_spec_file.exists():
        parsed_role_args_spec, role_spec_errors = _load_yaml_file(arg_spec_file)
        parsed_errors += role_spec_errors
    else:
        parsed_role_args_spec = None

    parsed_role = {
        "role_id": str(uuid.uuid4()),
        "role_name": directory.stem,
        "role_argument_specification": _remove_deep_metadata(parsed_role_args_spec) if parsed_role_args_spec else None,
        "spotter_metadata": {
            "column": 0,
            "end_mark_index": 0,
            "file": str(directory),
            "line": 0,
            "start_mark_index": 0,
        },
    }
    return parsed_role, parsed_errors


def _parse_py(file: Path) -> List[Dict[str, Any]]:
    if not file.parent:
        return []
    plugin_type_dict = {
        "library": "module",
        "action_plugins": "action",
        "lookup_plugins": "lookup",
    }

    plugin_type = plugin_type_dict.get(file.parent.name, None)
    if not plugin_type:
        return []

    return [
        {
            "plugin_id": str(uuid.uuid4()),
            "plugin_name": file.stem,
            "plugin_type": plugin_type,
            "plugin_specification": None,
            "spotter_metadata": {
                "column": 0,
                "end_mark_index": 0,
                "file": str(file),
                "line": 0,
                "start_mark_index": 0,
            },
        }
    ]


class UnknownAnsibleArtifactInput(BaseModel):
    path: Path
    exclude_paths: Set[str]
    parse_values: bool
    parse_vars: bool
    skip_detect_secrets: bool
    known_inodes: Set[int]

    # runtime field used for correct multi-process scan execution
    is_daemon: bool = False


class UnknownAnsibleArtifactStatistcsResult(BaseModel):
    parsed_included_files_count: int
    parsed_excluded_paths_count: int
    path_loops_detected: int


class UnknownAnsibleArtifactResult(BaseModel):
    parsed_tasks: List[Dict[str, Any]]
    parsed_playbooks: List[Dict[str, Any]]
    parsed_blocks: List[Dict[str, Any]]
    parsed_dynamic_inventories: List[Dict[str, Any]]
    parsed_roles: List[Dict[str, Any]]
    parsed_plugins: List[Dict[str, Any]]
    parsed_vars: List[Dict[str, Any]]
    yaml_error: List[YamlErrorDetails]
    statistics: UnknownAnsibleArtifactStatistcsResult


def parse_unknown_ansible_artifact_core(  # noqa: PLR0915, PLR0912
    data: UnknownAnsibleArtifactInput,
) -> UnknownAnsibleArtifactResult:
    """
    Parse Ansible artifact (unknown by type) by applying automatic Ansible file type detection.

    We are able to can discover task files, playbooks, roles and collections at any level recursively.

    :param path: Path to file or directory
    :param parse_values: True if also read values (apart from parameter names) from task parameters, False if not
    :return: Tuple containing list of parsed Ansible tasks and parsed playbook as dict
    """
    parsed_ansible_artifacts_tasks = []
    parsed_ansible_artifacts_playbooks = []
    parsed_ansible_artifacts_blocks = []
    parsed_ansible_artifacts_dynamic_inventories = []
    parsed_ansible_artifacts_roles = []
    parsed_ansible_artifacts_plugins = []
    parsed_ansible_artifacts_vars = []
    parsed_errors = []
    parsed_ansible_included_files_count = 0
    parsed_ansible_excluded_paths_count = 0
    path_loops_detected = 0

    if str(data.path.absolute()) in data.exclude_paths:
        parsed_ansible_excluded_paths_count += 1
    elif data.path.is_file() and data.path.suffix in YAML_SUFFIXES:
        parsed_ansible_included_files_count += 1
        loaded_yaml, yaml_error = _load_yaml_file(data.path)
        parsed_errors += yaml_error

        if _is_playbook(loaded_yaml):
            parsed_tasks, parsed_blocks, parsed_playbooks = _parse_playbook(
                loaded_yaml, str(data.path), data.parse_values, data.skip_detect_secrets
            )
            parsed_ansible_artifacts_tasks += parsed_tasks
            parsed_ansible_artifacts_blocks += parsed_blocks
            parsed_ansible_artifacts_playbooks += parsed_playbooks
        elif _is_dynamic_inventory(loaded_yaml):
            parsed_ansible_artifacts_dynamic_inventories += [
                _parse_dynamic_inventory(loaded_yaml, str(data.path), data.parse_values, data.skip_detect_secrets)
            ]
        elif _is_requirements(loaded_yaml):
            pass
        elif is_var_file(loaded_yaml):
            parsed_vars = _parse_vars(
                loaded_yaml, str(data.path), data.parse_values, data.parse_vars, data.skip_detect_secrets
            )
            parsed_ansible_artifacts_vars += parsed_vars
        elif isinstance(loaded_yaml, list):
            parsed_tasks, parsed_blocks = _parse_tasks(
                loaded_yaml, str(data.path), data.parse_values, None, None, data.skip_detect_secrets
            )
            parsed_ansible_artifacts_tasks += parsed_tasks
            parsed_ansible_artifacts_blocks += parsed_blocks
    elif data.path.is_file() and data.path.suffix == ".py":
        parsed_ansible_artifacts_plugins += _parse_py(data.path)
        parsed_ansible_included_files_count += 1
    elif data.path.is_dir():
        data.known_inodes.add(data.path.stat().st_ino)
        if _is_role(data.path):
            parsed_role, yaml_error = _parse_role(data.path)
            parsed_ansible_artifacts_roles += [parsed_role]
            parsed_errors += yaml_error

        inputs = [
            UnknownAnsibleArtifactInput(
                path=path,
                exclude_paths=data.exclude_paths,
                parse_values=data.parse_values,
                parse_vars=data.parse_vars,
                skip_detect_secrets=data.skip_detect_secrets,
                known_inodes=data.known_inodes,
                is_daemon=True,
            )
            for path in sorted(data.path.iterdir())
            if path.stat().st_ino not in data.known_inodes
        ]
        path_loops_detected += len(list(data.path.iterdir())) - len(inputs)

        if not data.is_daemon:
            with Pool() as pool:
                collected: Iterable[UnknownAnsibleArtifactResult] = pool.map(parse_unknown_ansible_artifact, inputs)
        else:
            collected = map(parse_unknown_ansible_artifact, inputs)
        for subresult in collected:
            parsed_ansible_artifacts_tasks += subresult.parsed_tasks
            parsed_ansible_artifacts_playbooks += subresult.parsed_playbooks
            parsed_ansible_artifacts_blocks += subresult.parsed_blocks
            parsed_ansible_artifacts_dynamic_inventories += subresult.parsed_dynamic_inventories
            parsed_ansible_artifacts_roles += subresult.parsed_roles
            parsed_ansible_artifacts_plugins += subresult.parsed_plugins
            parsed_ansible_artifacts_vars += subresult.parsed_vars
            parsed_errors += subresult.yaml_error
            parsed_ansible_included_files_count += subresult.statistics.parsed_included_files_count
            parsed_ansible_excluded_paths_count += subresult.statistics.parsed_excluded_paths_count
            path_loops_detected += subresult.statistics.path_loops_detected

    return UnknownAnsibleArtifactResult(
        parsed_tasks=parsed_ansible_artifacts_tasks,
        parsed_playbooks=parsed_ansible_artifacts_playbooks,
        parsed_blocks=parsed_ansible_artifacts_blocks,
        parsed_dynamic_inventories=parsed_ansible_artifacts_dynamic_inventories,
        parsed_roles=parsed_ansible_artifacts_roles,
        parsed_plugins=parsed_ansible_artifacts_plugins,
        parsed_vars=parsed_ansible_artifacts_vars,
        yaml_error=parsed_errors,
        statistics=UnknownAnsibleArtifactStatistcsResult(
            parsed_included_files_count=parsed_ansible_included_files_count,
            parsed_excluded_paths_count=parsed_ansible_excluded_paths_count,
            path_loops_detected=path_loops_detected,
        ),
    )


def parse_unknown_ansible_artifact(
    data: UnknownAnsibleArtifactInput,
) -> UnknownAnsibleArtifactResult:
    try:
        return parse_unknown_ansible_artifact_core(data)
    except OSError as ex:
        return UnknownAnsibleArtifactResult(
            parsed_tasks=[],
            parsed_playbooks=[],
            parsed_blocks=[],
            parsed_dynamic_inventories=[],
            parsed_roles=[],
            parsed_plugins=[],
            parsed_vars=[],
            yaml_error=[YamlErrorDetails(column=0, index=0, line=0, description=ex.strerror, file_path=data.path)],
            statistics=UnknownAnsibleArtifactStatistcsResult(
                parsed_included_files_count=0,
                parsed_excluded_paths_count=0,
                path_loops_detected=0,
            ),
        )


def parse_ansible_artifacts(
    paths: List[Path],
    exclude_paths: Optional[List[Path]],
    parse_values: bool,
    parse_vars: bool,
    skip_detect_secrets: bool,
) -> ParsingResult:
    """
    Parse multiple Ansible artifacts.

    :param paths: List of paths to Ansible artifacts
    :param parse_values: True if also read values (apart from parameter names) from task parameters, False if not
    :return: ParsingResult object with list of parsed Ansible tasks and playbooks that are prepared for scanning
    """
    paths_to_exclude = {str(x.absolute()) for x in exclude_paths} if exclude_paths else set()
    parsed_ansible_artifacts_tasks = []
    parsed_ansible_artifacts_playbooks = []
    parsed_ansible_artifacts_blocks = []
    parsed_ansible_artifacts_dynamic_inventories = []
    parsed_ansible_artifacts_roles = []
    parsed_ansible_artifacts_plugins = []
    parsed_ansible_artifacts_vars = []
    parsed_errors = []
    parsed_ansible_artifacts_included_files_count = 0
    parsed_ansible_artifacts_excluded_paths_count = 0
    path_loops_detected = 0

    for path in paths:
        data = UnknownAnsibleArtifactInput(
            path=path,
            exclude_paths=paths_to_exclude,
            parse_values=parse_values,
            parse_vars=parse_vars,
            skip_detect_secrets=skip_detect_secrets,
            known_inodes=set(),
            is_daemon=False,
        )
        parsed = parse_unknown_ansible_artifact(data)
        parsed_ansible_artifacts_tasks += parsed.parsed_tasks
        parsed_ansible_artifacts_playbooks += parsed.parsed_playbooks
        parsed_ansible_artifacts_blocks += parsed.parsed_blocks
        parsed_ansible_artifacts_dynamic_inventories += parsed.parsed_dynamic_inventories
        parsed_ansible_artifacts_roles += parsed.parsed_roles
        parsed_ansible_artifacts_plugins += parsed.parsed_plugins
        parsed_ansible_artifacts_vars += parsed.parsed_vars
        parsed_errors += parsed.yaml_error
        parsed_ansible_artifacts_included_files_count += parsed.statistics.parsed_included_files_count
        parsed_ansible_artifacts_excluded_paths_count += parsed.statistics.parsed_excluded_paths_count
        path_loops_detected = parsed.statistics.path_loops_detected
    return ParsingResult(
        tasks=parsed_ansible_artifacts_tasks,
        playbooks=parsed_ansible_artifacts_playbooks,
        blocks=parsed_ansible_artifacts_blocks,
        dynamic_inventories=parsed_ansible_artifacts_dynamic_inventories,
        roles=parsed_ansible_artifacts_roles,
        plugins=parsed_ansible_artifacts_plugins,
        variables=parsed_ansible_artifacts_vars,
        errors=parsed_errors,
        included_files_count=parsed_ansible_artifacts_included_files_count,
        excluded_paths_count=parsed_ansible_artifacts_excluded_paths_count,
        path_loops_detected=path_loops_detected,
    )
