"""Provide login CLI command."""

import argparse
from getpass import getpass
from pathlib import Path
from typing import Optional

from spotter.client.utils import CommonParameters, UsagePrefixRawDescriptionHelpFormatter
from spotter.library.api import ApiClient
from spotter.library.storage import Storage


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for login command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "login",
        help="Log in to Steampunk Spotter user account",
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog, usage_prefix="Log in to Steampunk Spotter user account", max_help_position=48
        ),
        usage="spotter login [OPTIONS]",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace, project_root: Path) -> None:
    """
    Execute callback for login command.

    :param args: Argparse arguments
    :param project_root: The root directory of the project.
    """
    common_params = CommonParameters.from_args(args)

    if not common_params.api_token and not common_params.username:
        common_params.username = input("Username: ")
    if not common_params.api_token and not common_params.password:
        common_params.password = getpass()

    login(
        common_params.api_endpoint,
        common_params.storage_path,
        common_params.api_token,
        common_params.username,
        common_params.password,
        common_params.timeout,
        common_params.debug,
        common_params.cacert,
        common_params.verify,
    )

    print("Login successful!")


def login(
    api_endpoint: str,
    storage_path: Path,
    api_token: Optional[str],
    username: Optional[str],
    password: Optional[str],
    timeout: Optional[int],
    debug: bool,
    cacert: Optional[Path],
    verify: bool,
) -> None:
    """
    Do user login.

    :param api_endpoint: Steampunk Spotter API endpoint
    :param storage_path: Path to storage
    :param api_token: Steampunk Spotter API token
    :param username: Steampunk Spotter username
    :param password: Steampunk Spotter password
    :param timeout: Steampunk Spotter API timeout (in seconds)
    :param debug: Enable or disable debug mode
    :param cacert: Path to file containing root CA certificates. If not listed, system's default will be used.
    :param verify: Verify server certificate
    """
    storage = Storage(storage_path)
    api_client = ApiClient(api_endpoint, storage, api_token, username, password, debug, cacert, verify)
    api_client.login(timeout=timeout if timeout else ApiClient.DEFAULT_TIMEOUT)
