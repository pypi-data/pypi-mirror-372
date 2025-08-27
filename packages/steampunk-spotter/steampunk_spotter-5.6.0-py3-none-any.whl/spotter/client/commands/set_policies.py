"""Provide set-policies CLI command."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from spotter.client.commands.policies_commands.policies_set import policies_set
from spotter.client.utils import CommonParameters, UsagePrefixRawDescriptionHelpFormatter, get_absolute_path


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for set-policies command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "set-policies",
        argument_default=argparse.SUPPRESS,
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog,
            usage_prefix="Set OPA policies (written in Rego Language) for custom Spotter checks "
            "(enterprise feature)",
            max_help_position=48,
        ),
        usage="spotter set-policies [OPTIONS] <PATH>",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    project_organization_group = parser.add_mutually_exclusive_group()
    project_organization_group.add_argument(
        "-p",
        "--project-id",
        type=str,
        default=None,
        help="UUID of an existing Steampunk Spotter project to set custom policies for "
        "(default project from the default organization will be used if not specified)",
    )
    project_organization_group.add_argument(
        "--organization-id",
        type=str,
        default=None,
        help="UUID of an existing Steampunk Spotter organization to set custom policies for",
    )
    parser.add_argument(
        "path",
        type=get_absolute_path,
        help="Path to the file or folder with custom OPA policies (written in Rego Language)",
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace, project_root: Path) -> None:
    """
    Execute callback for include-policies command.

    :param args: Argparse arguments
    :param project_root: The root directory of the project.
    """
    print("Warning: the set-policies command is deprecated. Use policies set instead.", file=sys.stderr)
    common_params = CommonParameters.from_args(args)

    path: Path = args.path
    if not path.is_file() and not path.is_dir():
        print(f"Error: path at {path} is not a file or directory.", file=sys.stderr)
        sys.exit(2)

    include_policies(
        common_params.api_endpoint,
        common_params.storage_path,
        common_params.api_token,
        common_params.username,
        common_params.password,
        common_params.timeout,
        args.project_id,
        args.organization_id,
        path,
        common_params.debug,
        common_params.cacert,
        common_params.verify,
    )


def include_policies(
    api_endpoint: str,
    storage_path: Path,
    api_token: Optional[str],
    username: Optional[str],
    password: Optional[str],
    timeout: Optional[int],
    project_id: Optional[str],
    organization_id: Optional[str],
    path: Path,
    debug: bool,
    cacert: Optional[Path],
    verify: bool,
) -> None:
    """
    Set custom OPA policies.

    By default, this will set policies for the default project from default organization.

    :param api_endpoint: Steampunk Spotter API endpoint
    :param storage_path: Path to storage
    :param api_token: Steampunk Spotter API token
    :param username: Steampunk Spotter username
    :param password: Steampunk Spotter password
    :param timeout: Steampunk Spotter API timeout (in seconds)
    :param project_id: UUID of an existing Steampunk Spotter project to set custom policies for
    :param organization_id: UUID of an existing Steampunk Spotter organization to set custom policies for
    :param path: Path to the file or folder with custom OPA policies (written in Rego Language)
    :param debug: Enable debug mode
    :param cacert: Path to file containing root CA certificates. If not listed, system's default will be used.
    :param verify: Verify server certificate
    """
    policies_set(
        api_endpoint,
        storage_path,
        api_token,
        username,
        password,
        timeout,
        project_id,
        organization_id,
        path,
        debug,
        cacert,
        verify,
    )
