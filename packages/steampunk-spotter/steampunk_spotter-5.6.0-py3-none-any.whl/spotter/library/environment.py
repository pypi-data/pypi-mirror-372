"""Provide discovery of user's environment."""

import json
import os
import platform
import subprocess
import sys
from copy import deepcopy
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import ruamel.yaml as ruamel
from pydantic import BaseModel, ConfigDict
from pydantic_core import to_jsonable_python

from spotter.library.parsing.noqa_comments import SpotterNoqa
from spotter.library.utils import get_package_version


def path_func(args: Tuple[Optional[Path], Any]) -> Any:
    arg, func = args
    result = func(arg)
    return result


class EnvironmentAnsibleVersion(BaseModel):
    """Discovered Ansible versions (per edition, i.e. full, base, core)."""

    model_config = ConfigDict(extra="ignore")

    ansible_core: Optional[str] = None
    ansible_base: Optional[str] = None
    ansible: Optional[str] = None


class EnvironmentAapData(BaseModel):
    job_id: str
    inventory_id: Optional[str]
    project_revision: Optional[str]


class Environment(BaseModel):
    """User environment/workspace state discovery (retrieves system info and versions of installed packages)."""

    model_config = ConfigDict(extra="ignore")

    python_version: Optional[str] = None
    ansible_version: Optional[EnvironmentAnsibleVersion] = None
    installed_collections: Optional[List[Dict[str, Optional[str]]]] = None
    installed_roles: Optional[List[Dict[str, Optional[str]]]] = None
    installed_pip_packages: Optional[List[Dict[str, Optional[str]]]] = None
    ansible_config: Optional[Dict[str, Any]] = None
    galaxy_yml: Optional[Dict[str, Any]] = None
    collection_requirements: Optional[Dict[str, Any]] = None
    cli_scan_args: Optional[Dict[str, Any]] = None
    aap_data: Optional[EnvironmentAapData] = None

    @staticmethod
    def remove_installed_location(data: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        if not data:
            return data
        result = [
            {
                "fqcn": x["fqcn"],
                "version": x["version"],
                "location": None,
            }
            for x in data
        ]
        return result

    def clean(self, include_metadata: bool) -> "Environment":
        if include_metadata:
            return self

        result = Environment(
            python_version=self.python_version,
            ansible_version=self.ansible_version,
            installed_collections=self.remove_installed_location(self.installed_collections),
            installed_roles=self.remove_installed_location(self.installed_roles),
            installed_pip_packages=self.installed_pip_packages,
            ansible_config=self.ansible_config,
            galaxy_yml=self.galaxy_yml,
            collection_requirements=self.collection_requirements,
            cli_scan_args=self.cli_scan_args,
            aap_data=self.aap_data,
        )
        return result

    @staticmethod
    def _get_python_version() -> str:
        """
        Get python version.

        :return: Version string
        """
        return platform.python_version()

    @staticmethod
    def _get_ansible_core_python_version() -> Optional[str]:
        """
        Get ansible-core python package version.

        :return: Version string
        """
        return get_package_version("ansible-core", False)

    @staticmethod
    def _get_ansible_base_python_version() -> Optional[str]:
        """
        Get ansible-base python package version.

        :return: Version string
        """
        return get_package_version("ansible-base", False)

    @staticmethod
    def _get_ansible_version() -> Optional[str]:
        """
        Get ansible python package version.

        :return: Version string
        """
        return get_package_version("ansible", False)

    @staticmethod
    def _get_installed_ansible_collections() -> List[Dict[str, Optional[str]]]:
        """
        Get installed Ansible collections.

        :return: Dict with Ansible collection names and their versions
        """
        installed_collections = []
        try:
            output = subprocess.check_output(
                ["ansible-galaxy", "collection", "list", "--format", "json"], stderr=subprocess.DEVNULL
            ).decode("utf-8")
            for value in json.loads(output).values():
                for fqcn, version in value.items():
                    installed_collections.append(
                        {
                            "fqcn": fqcn,
                            "version": version.get("version", None),
                        }
                    )
            return installed_collections
        except (subprocess.CalledProcessError, FileNotFoundError):
            return installed_collections

    @staticmethod
    def _get_installed_ansible_roles() -> List[Dict[str, Optional[str]]]:
        """
        Get installed Ansible roles.

        :return: Dict with Ansible role names and their versions
        """
        installed_roles = []
        try:
            output = subprocess.check_output(["ansible-galaxy", "role", "list"], stderr=subprocess.DEVNULL).decode(
                "utf-8"
            )
            location = None
            for line in output.splitlines():
                if line.startswith("#"):
                    location = line[2:].strip()
                if not line.startswith("-"):
                    continue
                content = line[2:]
                name, version = content.split(",", 1)
                installed_roles.append({"fqcn": name.strip(), "version": version.strip(), "location": location})
            return installed_roles
        except (subprocess.CalledProcessError, FileNotFoundError):
            return installed_roles

    @staticmethod
    def _get_installed_pip_packages() -> List[Dict[str, Optional[str]]]:
        """
        Get installed pip collections.

        :return: Dict with pip package names and their versions
        """
        installed_pip_packages = []
        try:
            output = subprocess.check_output(["pip", "list", "--format", "json"], stderr=subprocess.DEVNULL).decode(
                "utf-8"
            )
            decoded = json.loads(output)
            installed_pip_packages = cast(List[Dict[str, Optional[str]]], decoded)
            return installed_pip_packages
        except (subprocess.CalledProcessError, FileNotFoundError):
            return installed_pip_packages

    @staticmethod
    def _get_aap_data() -> Optional[EnvironmentAapData]:
        """
        Get related AAP data - like JOB_ID.

        :return: EnvironmentAapData with aap specific data
        """
        job_id = os.environ.get("JOB_ID")
        if not job_id:
            return None
        return EnvironmentAapData(
            job_id=job_id,
            inventory_id=os.environ.get("INVENTORY_ID"),
            project_revision=os.environ.get("PROJECT_REVISION"),
        )

    @staticmethod
    def _get_ansible_config(path: Path) -> Dict[str, Any]:
        """
        Get Ansible config current settings.

        :return: Dict with Ansible config current settings specified as key-value pairs
        """
        ansible_config = {}
        try:
            str_path = str(path) if path.is_dir() else str(path.parent)
            env = dict(os.environ, ANSIBLE_FORCE_COLOR="0")
            output = subprocess.check_output(
                ["ansible-config", "dump", "--only-changed"], stderr=subprocess.DEVNULL, cwd=str_path, env=env
            ).decode("utf-8")
            for line in output.splitlines():
                if line and "=" in line:
                    key, value = line.split("=", maxsplit=1)
                    ansible_config[key.strip()] = value.strip()
            return ansible_config
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            return ansible_config

    @staticmethod
    def _get_galaxy_yml(path: Path) -> Dict[str, Any]:
        """
        Get galaxy.yml contents.

        :param path: Path to directory where collection requirements reside
        :return: Contents of galaxy.yml file
        """
        try:
            with (path / "galaxy.yml").open("r", encoding="utf-8") as stream:
                try:
                    yaml = ruamel.YAML(typ="safe", pure=True)
                    parsed = yaml.load(stream)
                    if not (isinstance(parsed, dict) and all(isinstance(k, str) for k in parsed)):
                        print("Failed basic format checking for the collection galaxy.yml file. Ignoring.")
                        return {}
                    return parsed
                except ruamel.YAMLError:
                    return {}
        except OSError:
            return {}

    @staticmethod
    def _validate_collection_requirements(  # noqa: PLR0911
        parsed_collections: List[Any], requirements_path: Path
    ) -> List[Dict[str, Any]]:
        """
        Validate Ansible collection requirements from requirements.yml.

        The rules applied here have been taken from: https://docs.ansible.com/ansible/latest/galaxy/user_guide.html.

        :param requirements_path: Path to requirements file
        :return: List of Ansible collection requirements
        """
        requirements_yml_collections_keys = {"name", "version", "signatures", "source", "type"}
        type_key_allowed_values = {"file", "galaxy", "git", "url", "dir", "subdirs"}
        collection_requirements: List[Dict[str, Any]] = []
        for entry in parsed_collections:
            if isinstance(entry, str):
                collection_requirements.append({"name": entry})
            elif isinstance(entry, dict):
                extra_keys = entry.keys() - requirements_yml_collections_keys
                if extra_keys:
                    print(
                        f"Invalid keys '{extra_keys}' in entry '{entry}' under 'collections' in the requirements "
                        f"file '{requirements_path}'. Supported keys are '{requirements_yml_collections_keys}'. "
                        f"Ignoring."
                    )
                    return []

                if "name" not in entry:
                    print(
                        f"Missing required 'name' key in entry '{entry}' under 'collections' in the requirements "
                        f"file '{requirements_path}'. Ignoring."
                    )
                    return []

                for key in entry:
                    if key == "signatures" and not isinstance(entry["signatures"], list):
                        print(
                            f"The 'signatures' key in entry '{entry}' under 'collections' in the requirements file "
                            f"'{requirements_path}' should be of type list but is '{type(entry)}'. Ignoring."
                        )
                        return []
                    if key != "signatures" and not isinstance(entry[key], str):
                        print(
                            f"The '{key}' key in entry '{entry}' under 'collections' in the requirements file "
                            f"'{requirements_path}' should be of type string but is '{type(entry[key])}'. Ignoring."
                        )
                        return []
                    if key == "type":
                        extra_keys_type = {entry[key]} - type_key_allowed_values
                        if extra_keys_type:
                            print(
                                f"Invalid values '{extra_keys_type}' in for 'type' key in entry '{entry}' under "
                                f"'collections' in the requirements file '{requirements_path}'. Supported keys are "
                                f"'{type_key_allowed_values}'. Ignoring."
                            )
                            return []

                collection_requirements.append(entry)
            else:
                print(
                    f"The entry '{entry}' under 'collections' key in the requirements file '{requirements_path}' "
                    f"should be of type string or dict but is '{type(entry)}'. Ignoring."
                )
                return []

        return collection_requirements

    @staticmethod
    def _validate_role_requirements(parsed_roles: List[Any], requirements_path: Path) -> List[Dict[str, Any]]:
        """
        Validate Ansible role requirements from requirements.yml.

        The rules applied here have been taken from: https://galaxy.ansible.com/docs/using/installing.html.

        :param requirements_path: Path to requirements file
        :return: List of Ansible role requirements
        """
        requirements_yml_roles_keys = {"src", "scm", "version", "name"}
        scm_key_allowed_values = {"git", "hg"}
        role_requirements: List[Dict[str, Any]] = []
        for entry in parsed_roles:
            if isinstance(entry, str):
                role_requirements.append({"src": entry})
            elif isinstance(entry, dict):
                extra_keys = entry.keys() - requirements_yml_roles_keys
                if extra_keys:
                    print(
                        f"Invalid keys '{extra_keys}' in entry '{entry}' under 'roles' in the requirements file "
                        f"'{requirements_path}'. Supported keys are '{requirements_yml_roles_keys}'. Ignoring."
                    )
                    return []

                if "src" not in entry and "name" not in entry:
                    print(
                        f"Missing required 'src' or 'name key in entry '{entry}' under 'roles' in the requirements "
                        f"file '{requirements_path}'. Ignoring."
                    )
                    return []

                for key in entry:
                    if not isinstance(entry[key], str):
                        print(
                            f"The '{key}' key in entry '{entry}' under 'roles' in the requirements file "
                            f"'{requirements_path}' should be of type string but is '{type(entry[key])}'. Ignoring."
                        )
                        return []
                    if key == "scm":
                        extra_keys_scm = {entry[key]} - scm_key_allowed_values
                        if extra_keys_scm:
                            print(
                                f"Invalid values '{extra_keys}' in for 'scm' key in entry '{entry}' under 'roles' in "
                                f"the requirements file {requirements_path}'. Supported keys are "
                                f"'{scm_key_allowed_values}'. Ignoring."
                            )
                            return []

                role_requirements.append(entry)
            else:
                print(
                    f"The entry '{entry}' under 'roles' key in the requirements file '{requirements_path}' should be "
                    f"of type string or dict but is '{type(entry)}'. Ignoring."
                )
                return []

        return role_requirements

    @staticmethod
    def get_candidate_requirements_path(path: Path) -> Path:
        """
        Get candidate for requirements.yml file.

        :param path: Path to directory where requirements reside
        :return: Path requirements.yml file
        """
        search_path = path
        if path.is_file():
            search_path = path.parent

        # TODO: Update discovery as requirements.yml files can be anywhere
        default = search_path / "requirements.yml"
        possible_requirements_yml_paths = (
            default,
            search_path / "requirements.yaml",
            search_path / "collections" / "requirements.yml",
            search_path / "collections" / "requirements.yaml",
            search_path / "roles" / "requirements.yml",
            search_path / "roles" / "requirements.yaml",
        )

        requirements_yml_path = next((path for path in possible_requirements_yml_paths if path.exists()), default)
        return requirements_yml_path

    @staticmethod
    def _get_requirements(path: Path) -> Dict[str, List[Dict[str, Any]]]:  # noqa: PLR0911
        """
        Get Ansible requirements from requirements.yml.

        :param path: Path to directory where requirements reside
        :return: Contents of requirements.yml file
        """
        try:
            requirements_yml_path = Environment.get_candidate_requirements_path(path)
            if not requirements_yml_path:
                return {}

            with requirements_yml_path.open("r", encoding="utf-8") as stream:
                try:
                    yaml = ruamel.YAML(typ="safe", pure=True)
                    parsed = yaml.load(stream)
                    if isinstance(parsed, dict) and all(isinstance(k, str) for k in parsed):
                        if not ("collections" in parsed or "roles" in parsed):
                            print(
                                f"Missing 'collections' or 'roles' key in the requirements file "
                                f"'{requirements_yml_path}'. Ignoring."
                            )
                            return {}

                        if "collections" in parsed:
                            if not isinstance(parsed["collections"], list):
                                print(
                                    f"The 'collections' key in the requirements file '{requirements_yml_path}' "
                                    f"is not of list type. Ignoring."
                                )
                                return {}

                            parsed["collections"] = Environment._validate_collection_requirements(
                                parsed["collections"], requirements_yml_path
                            )

                        if "roles" in parsed:
                            if not isinstance(parsed["roles"], list):
                                print(
                                    f"The 'roles' key in the requirements file '{requirements_yml_path}' is not "
                                    f"of list type. Ignoring."
                                )
                                return {}

                            parsed["roles"] = Environment._validate_role_requirements(
                                parsed["roles"], requirements_yml_path
                            )
                    elif isinstance(parsed, list):
                        parsed = {"roles": Environment._validate_role_requirements(parsed, requirements_yml_path)}
                    else:
                        print(
                            f"Failed basic format checking for the requirements file '{requirements_yml_path}'. "
                            f"Ignoring."
                        )
                        return {}

                    return parsed  # type: ignore
                except ruamel.YAMLError:
                    return {}
        except OSError:
            return {}

    @classmethod
    def from_local_discovery(cls, paths: List[Path]) -> "Environment":
        """Set workspace variables discovered locally on user's system.

        :param paths: List of paths to directory where to look for local files
        :return: Environment object
        """
        # TODO: Add support to combine multiple galaxy.yml and requirements.yml, right now we use just the first one

        active_path = paths[0] if paths else None
        functions = [
            (active_path, lambda _: cls._get_installed_ansible_collections()),
            (active_path, lambda _: cls._get_installed_ansible_roles()),
            (active_path, lambda _: cls._get_installed_pip_packages()),
            (active_path, cls._get_ansible_config if active_path else lambda _: {}),
            (active_path, lambda _: cls._get_ansible_version()),
        ]

        pool = ThreadPool()
        results = pool.map(path_func, functions)

        return cls(
            python_version=cls._get_python_version(),
            ansible_version=EnvironmentAnsibleVersion(
                ansible_core=cls._get_ansible_core_python_version(),
                ansible_base=cls._get_ansible_base_python_version(),
                ansible=results[4],
            ),
            installed_collections=results[0],
            installed_roles=results[1],
            installed_pip_packages=results[2],
            ansible_config=results[3],
            galaxy_yml=cls._get_galaxy_yml(paths[0]) if paths else {},
            collection_requirements=cls._get_requirements(paths[0]) if paths else {},
            aap_data=cls._get_aap_data(),
        )

    @classmethod
    def from_config_file(cls, config_path: Path) -> "Environment":
        """
        Set workspace variables from config file.

        :param config_path: Configuration file path (must exist)
        :return: Environment object
        """
        try:
            if not config_path.exists():
                print(f"Error: config file at {config_path} does not exist.", file=sys.stderr)
                sys.exit(2)

            with config_path.open("r", encoding="utf-8") as config_file:
                yaml = ruamel.YAML(typ="safe", pure=True)
                config = yaml.load(config_file)

                if config is None:
                    print(f"Warning: empty configuration file '{config_path}'. Ignoring.", file=sys.stderr)
                    return cls()

                if not isinstance(config, dict) and all(isinstance(k, str) for k in config):
                    print(
                        f"Error: the content of configuration file '{config_path}' should be of type dict but is "
                        f"'{type(config)}'.",
                        file=sys.stderr,
                    )
                    sys.exit(2)

                valid_config_entries = {"ansible_version": str, "skip_checks": list, "enforce_checks": list}
                extra_keys = config.keys() - valid_config_entries.keys()
                if extra_keys:
                    print(
                        f"Error: invalid keys '{extra_keys}' in configuration file '{config_path}'. "
                        f"Supported keys are '{valid_config_entries.keys()}'.",
                        file=sys.stderr,
                    )
                    sys.exit(2)

                for key, typ in valid_config_entries.items():
                    entry = config.get(key, None)
                    if entry and not isinstance(entry, typ):
                        print(
                            f"Error: the '{key}' key in the configuration file '{config_path}' should be of type "
                            f"{typ} but is '{type(entry)}'.",
                            file=sys.stderr,
                        )
                        sys.exit(2)

                environment = cls()
                ansible_version = config.get("ansible_version", None)
                if ansible_version:
                    environment.ansible_version = EnvironmentAnsibleVersion(ansible_core=config.get("ansible_version"))

                skip_checks = config.get("skip_checks", [])
                if isinstance(skip_checks, list) and all(isinstance(e, str) for e in skip_checks):
                    skip_checks = [SpotterNoqa(event=e) for e in skip_checks]
                else:
                    skip_checks = [
                        SpotterNoqa(
                            event=e.get("event", None),
                            subevent_code=e.get("subevent_code", None),
                            fqcn=e.get("fqcn", None),
                        )
                        for e in skip_checks
                    ]

                enforce_checks = config.get("enforce_checks", [])
                if isinstance(enforce_checks, list) and all(isinstance(e, str) for e in enforce_checks):
                    enforce_checks = [SpotterNoqa(event=e) for e in enforce_checks]
                else:
                    enforce_checks = [
                        SpotterNoqa(
                            event=e.get("event", None),
                            subevent_code=e.get("subevent_code", None),
                            fqcn=e.get("fqcn", None),
                        )
                        for e in enforce_checks
                    ]

                environment.cli_scan_args = {"skip_checks": skip_checks, "enforce_checks": enforce_checks}

                return environment
        except (ruamel.YAMLError, AttributeError) as e:
            print(f"Error: invalid configuration file: {e}", file=sys.stderr)
            sys.exit(2)

    @classmethod
    def from_project_configuration_file(cls) -> "Environment":
        """Set workspace variables from project-level configuration file.

        :return: Configuration object
        """
        possible_project_config_paths = (
            Path.cwd() / ".spotter.json",
            Path.cwd() / ".spotter.yml",
            Path.cwd() / ".spotter.yaml",
        )
        project_config_paths = [p for p in possible_project_config_paths if p.exists()]
        if len(project_config_paths) > 1:
            print(
                f"Error: there should be exactly one Spotter configuration file in the '{Path.cwd()}' project. Found "
                f"{len(project_config_paths)} files: {[p.name for p in project_config_paths]}.",
                file=sys.stderr,
            )
            sys.exit(2)

        if project_config_paths:
            return cls.from_config_file(project_config_paths[0])
        return cls()

    def combine(self, other: "Environment") -> "Environment":
        """
        Combine two dataclasses into one, overriding with values from `other`.

        Null values in `other` do not override original values.

        :param other: Environment to combine with
        :return: Environment object
        """
        original_dict_copy = deepcopy(to_jsonable_python(self))
        other_dict_copy = deepcopy(to_jsonable_python(other))
        other_dict_without_nulls = {k: v for k, v in other_dict_copy.items() if v is not None}
        original_dict_copy.update(other_dict_without_nulls)
        return self.__class__(**original_dict_copy)


class EnvironmentV3(BaseModel):
    """User environment/workspace state discovery (retrieves system info and versions of installed packages)."""

    model_config = ConfigDict(extra="ignore")

    python_version: Optional[str] = None
    ansible_version: Optional[EnvironmentAnsibleVersion] = None
    installed_collections: Optional[List[Dict[str, Optional[str]]]] = None
    ansible_config: Optional[Dict[str, Any]] = None
    galaxy_yml: Optional[Dict[str, Any]] = None
    collection_requirements: Optional[Dict[str, Any]] = None
    cli_scan_args: Optional[Dict[str, Any]] = None


class Statistics(BaseModel):
    included_files_count: int
    excluded_paths_count: int
    path_loops_detected: int = 0
