"""Provide utility functions that can be used as helpers throughout the client code."""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Iterable, NoReturn, Optional, Sequence, Union

from pydantic import BaseModel

from spotter.library.api import ApiClient
from spotter.library.storage import Storage
from spotter.library.utils import get_current_cli_version


class CommonParameters(BaseModel):
    """A container for common client parameters."""

    api_endpoint: str
    storage_path: Path
    api_token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    timeout: Optional[int] = None
    debug: bool = False
    cacert: Optional[Path] = None
    verify: bool = False

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "CommonParameters":
        """
        Convert CLI arguments to CommonParameters object.

        :param args: Argparse arguments
        :return: CommonParameters object
        """
        api_endpoint = args.endpoint or os.environ.get("SPOTTER_ENDPOINT", "")
        storage_path = args.storage_path or Storage.DEFAULT_PATH
        api_token = args.token or os.environ.get("SPOTTER_TOKEN") or os.environ.get("SPOTTER_API_TOKEN")
        username = args.username or os.environ.get("SPOTTER_USERNAME")
        password = args.password or os.environ.get("SPOTTER_PASSWORD")
        timeout = args.timeout
        debug = args.debug
        cacert = args.cacert or os.environ.get("SPOTTER_CACERT")
        verify = not (args.insecure or os.environ.get("SPOTTER_INSECURE", False) in ["1", "true", "True", "TRUE"])

        # discovery for a persistent API config
        storage = Storage(storage_path)
        if not api_endpoint:
            if storage.exists("spotter.json"):
                storage_configuration_json = storage.read_json("spotter.json")
                api_endpoint = storage_configuration_json.get("endpoint", ApiClient.DEFAULT_ENDPOINT)
            else:
                api_endpoint = ApiClient.DEFAULT_ENDPOINT

        return cls(
            api_endpoint=api_endpoint,
            storage_path=storage_path,
            api_token=api_token,
            username=username,
            password=password,
            timeout=timeout,
            debug=debug,
            cacert=cacert,
            verify=verify,
        )


class UsagePrefixRawDescriptionHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """A help formatter that retains any formatting in descriptions and also capitalizes usage prefix."""

    def __init__(self, *args: Any, usage_prefix: Optional[str] = None, **kwargs: Any):
        """
        Initialize UsagePrefixRawDescriptionHelpFormatter.

        :param args: Keyword arguments
        :param usage_prefix: Usage prefix (e.g., can tell what the command does)
        :param kwargs: Non-keyword arguments
        """
        self.usage_prefix = usage_prefix
        super().__init__(*args, **kwargs)

    def add_usage(
        self,
        usage: Optional[str],
        actions: Iterable[argparse.Action],
        groups: Iterable[argparse._MutuallyExclusiveGroup],
        prefix: Optional[str] = None,
    ) -> None:
        """
        Add usage command section.

        :param usage: Usage message
        :param actions: List of argparse.Action objects
        :param groups: List of groups
        :param prefix: Usage message prefix
        """
        if prefix is None:
            prefix = f"{self.usage_prefix}\n\nUsage: " if self.usage_prefix else "Usage: "

        super().add_usage(usage, actions, groups, prefix)

    def _format_action(self, action: argparse.Action) -> str:
        """
        Format argparse action (remove the first metavar line if formatting a PARSER action).

        :param action: The argparse.Action object
        :return: Formatted action
        """
        parts = super(argparse.RawDescriptionHelpFormatter, self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts


class PrintCurrentVersionAction(argparse.Action):
    """An argument parser action for displaying current Python package version."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Union[str, Sequence[str], None],
        option_string: Optional[str] = None,
    ) -> NoReturn:
        """
        Overridden the original __call__ method for argparse.Action.

        :param parser: ArgumentParser object
        :param namespace: Namespace object
        :param values: Command-line arguments
        :param option_string: Option string used to invoke this action.
        """
        print(get_current_cli_version())
        sys.exit(0)


def get_absolute_path(file_name: str, check_exists: bool = True) -> Path:
    """
    Obtain an absolute path from file name.

    :param file_name: File name
    :param check_exists: Check if a file exists
    :return: Absolute path
    """
    absolute_path = Path(file_name).absolute()
    if check_exists and not absolute_path.exists():
        print(f"Error: provided file at {absolute_path} does not exist.", file=sys.stderr)
        sys.exit(2)
    else:
        return absolute_path
