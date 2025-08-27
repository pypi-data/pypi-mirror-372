"""Provide logout CLI command."""

import argparse
from pathlib import Path
from typing import Optional

from spotter.client.utils import CommonParameters, UsagePrefixRawDescriptionHelpFormatter
from spotter.library.api import ApiClient
from spotter.library.storage import Storage


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for logout command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "logout",
        help="Log out from Steampunk Spotter user account",
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog, usage_prefix="Log out from Steampunk Spotter user account", max_help_position=48
        ),
        usage="spotter logout [OPTIONS]",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace, project_root: Path) -> None:
    """
    Execute callback for logout command.

    :param args: Argparse arguments
    :param project_root: The root directory of the project.
    """
    common_params = CommonParameters.from_args(args)
    logout(
        common_params.api_endpoint,
        common_params.storage_path,
        common_params.api_token,
        common_params.username,
        common_params.password,
        common_params.cacert,
        common_params.verify,
    )

    print("Logout successful!")


def logout(
    api_endpoint: str,
    storage_path: Path,
    api_token: Optional[str],
    username: Optional[str],
    password: Optional[str],
    cacert: Optional[Path],
    verify: bool,
) -> None:
    """
    Do user logout.

    This will remove storage folder with auth tokens.

    :param api_endpoint: Steampunk Spotter API endpoint
    :param storage_path: Path to storage
    :param api_token: Steampunk Spotter API token
    :param username: Steampunk Spotter username
    :param password: Steampunk Spotter password
    :param cacert: Path to file containing root CA certificates. If not listed, system's default will be used.
    :param verify: Verify server certificate
    """
    storage = Storage(storage_path)
    api_client = ApiClient(api_endpoint, storage, api_token, username, password, False, cacert, verify)
    api_client.logout()
