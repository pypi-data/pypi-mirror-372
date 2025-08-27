"""Provide config clear CLI command."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from spotter.client.utils import CommonParameters, UsagePrefixRawDescriptionHelpFormatter
from spotter.library.api import ApiClient
from spotter.library.storage import Storage


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for config clear command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "clear",
        help="Clear configuration from organization",
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog,
            usage_prefix="Clear organization-level file with configuration "
            "(e.g., for enforcing and skipping checks)",
            max_help_position=48,
        ),
        usage="spotter config clear [OPTIONS]",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace, project_root: Path) -> None:
    """
    Execute callback for config clear command.

    :param args: Argparse arguments
    :param project_root: The root directory of the project.
    """
    common_params = CommonParameters.from_args(args)
    config_clear(
        common_params.api_endpoint,
        common_params.storage_path,
        common_params.api_token,
        common_params.username,
        common_params.password,
        common_params.timeout,
        args.organization_id,
        common_params.debug,
        common_params.cacert,
        common_params.verify,
    )


def _debug_print_project_and_org(api_client: ApiClient, organization_id: Optional[str]) -> None:
    if organization_id is not None:
        api_client.debug_print("Clearing configuration for organization id {}", organization_id)
        api_client.debug_organization(organization_id)
    else:
        api_client.debug_print("Clearing configuration for default organization")
        api_client.debug_my_default_organization()


def config_clear(
    api_endpoint: str,
    storage_path: Path,
    api_token: Optional[str],
    username: Optional[str],
    password: Optional[str],
    timeout: Optional[int],
    organization_id: Optional[str],
    debug: bool,
    cacert: Optional[Path],
    verify: bool,
) -> None:
    """
    Clear configuration file for organization.

    By default, this will clear configuration from the default organization.

    :param api_endpoint: Steampunk Spotter API endpoint
    :param storage_path: Path to storage
    :param api_token: Steampunk Spotter API token
    :param username: Steampunk Spotter username
    :param password: Steampunk Spotter password
    :param timeout: Steampunk Spotter API timeout (in seconds)
    :param organization_id: UUID of an existing Steampunk Spotter organization to clear configuration from
    :param debug: Enable debug mode
    """
    storage = Storage(storage_path)
    api_client = ApiClient(api_endpoint, storage, api_token, username, password, debug, cacert, verify)
    api_client.debug_print_me()
    _debug_print_project_and_org(api_client, organization_id)
    if organization_id:
        response = api_client.patch(
            f"/v3/configuration/?organization={organization_id}",
            payload={"spotter_noqa": []},
            timeout=timeout if timeout else ApiClient.DEFAULT_TIMEOUT,
        )
    else:
        response = api_client.patch(
            "/v3/configuration/",
            payload={"spotter_noqa": []},
            timeout=timeout if timeout else ApiClient.DEFAULT_TIMEOUT,
        )
    if not response.ok:
        print(api_client.format_api_error(response), file=sys.stderr)
        sys.exit(2)

    print("Configuration successfully cleared.")
