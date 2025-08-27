"""Provide policies clear CLI command."""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from spotter.client.utils import CommonParameters, UsagePrefixRawDescriptionHelpFormatter
from spotter.library.api import ApiClient
from spotter.library.storage import Storage


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for policies clear command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "clear",
        help="Clear custom policies (enterprise feature)",
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog, usage_prefix="Clear OPA policies for custom Spotter checks (enterprise feature)", max_help_position=48
        ),
        usage="spotter policies clear [OPTIONS]",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace, project_root: Path) -> None:
    """
    Execute callback for policies clear command.

    :param args: Argparse arguments
    :param project_root: The root directory of the project.
    """
    common_params = CommonParameters.from_args(args)
    policies_clear(
        common_params.api_endpoint,
        common_params.storage_path,
        common_params.api_token,
        common_params.username,
        common_params.password,
        common_params.timeout,
        args.project_id,
        args.organization_id,
        common_params.debug,
        common_params.cacert,
        common_params.verify,
    )


def _debug_print_project_and_org(
    api_client: ApiClient, project_id: Optional[str], organization_id: Optional[str]
) -> None:
    if project_id is not None:
        api_client.debug_print("Clearing polices for project id {}", project_id)
        api_client.debug_project(project_id)
    elif organization_id is not None:
        api_client.debug_print("Clearing polices for organization id {}", organization_id)
        api_client.debug_organization(organization_id)
    else:
        api_client.debug_print("Clearing polices for default organization")
        api_client.debug_my_default_organization()


def policies_clear(
    api_endpoint: str,
    storage_path: Path,
    api_token: Optional[str],
    username: Optional[str],
    password: Optional[str],
    timeout: Optional[int],
    project_id: Optional[str],
    organization_id: Optional[str],
    debug: bool,
    cacert: Optional[Path],
    verify: bool,
) -> None:
    """
    Clear custom OPA policies.

    By default, this will clear policies that belong to the default project from default organization.

    :param api_endpoint: Steampunk Spotter API endpoint
    :param storage_path: Path to storage
    :param api_token: Steampunk Spotter API token
    :param username: Steampunk Spotter username
    :param password: Steampunk Spotter password
    :param timeout: Steampunk Spotter API timeout (in seconds)
    :param project_id: UUID of an existing Steampunk Spotter project to clear custom policies from
    :param organization_id: UUID of an existing Steampunk Spotter organization to clear custom policies from
    :param debug: Enable debug mode
    """
    storage = Storage(storage_path)
    api_client = ApiClient(api_endpoint, storage, api_token, username, password, debug, cacert, verify)
    api_client.debug_print_me()
    _debug_print_project_and_org(api_client, project_id, organization_id)

    payload: Dict[str, Any] = {"policies": [], "project_id": project_id, "organization_id": organization_id}
    response = api_client.put(
        "/v2/opa/",
        payload=payload,
        timeout=timeout if timeout else ApiClient.DEFAULT_TIMEOUT,
        ignore_response_status_codes=True,
    )
    if response.status_code == 402:
        print(
            "Error: the use of custom policies is only available in Spotter's ENTERPRISE plan. "
            "Please upgrade your plan to use this functionality.",
            file=sys.stderr,
        )
        sys.exit(2)
    if response.status_code == 403 and project_id:
        print(
            "Error: the user is not a member of the organization that includes the project with the given ID.",
            file=sys.stderr,
        )
        sys.exit(2)
    if response.status_code == 403 and organization_id:
        print("Error: the user is not a member of the organization with the given ID.", file=sys.stderr)
        sys.exit(2)
    if response.status_code == 404 and project_id:
        print("Error: the project with the given ID was not found.", file=sys.stderr)
        sys.exit(2)
    if response.status_code == 404 and organization_id:
        print("Error: the organization with the given ID was not found.", file=sys.stderr)
        sys.exit(2)
    if not response.ok:
        print(api_client.format_api_error(response), file=sys.stderr)
        sys.exit(2)

    print("Custom policies successfully cleared.")
