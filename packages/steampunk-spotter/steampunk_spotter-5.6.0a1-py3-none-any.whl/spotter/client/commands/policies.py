"""Provide policies CLI command."""

from typing import TYPE_CHECKING

from spotter.client.commands.policies_commands import policies_clear, policies_set
from spotter.client.utils import UsagePrefixRawDescriptionHelpFormatter

if TYPE_CHECKING:
    import argparse


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for policies command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "policies",
        help="Manage custom policies (enterprise feature)",
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog,
            usage_prefix="Manage OPA policies for custom Spotter checks (enterprise feature)",
            max_help_position=48,
        ),
        usage="spotter policies [OPTIONS] <COMMAND>",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    project_organization_group = parser.add_mutually_exclusive_group()
    project_organization_group.add_argument(
        "-p",
        "--project-id",
        type=str,
        help="UUID of an existing Steampunk Spotter project to manage custom policies for "
        "(default project from the default organization will be used if not specified)",
    )
    project_organization_group.add_argument(
        "--organization-id",
        type=str,
        help="UUID of an existing Steampunk Spotter organization to manage custom policies for",
    )

    subparsers = parser.add_subparsers()
    cmds = [
        (policies_set.__name__.rsplit(".", maxsplit=1)[-1], policies_set),
        (policies_clear.__name__.rsplit(".", maxsplit=1)[-1], policies_clear),
    ]
    for _, module in cmds:
        module.add_parser(subparsers)
