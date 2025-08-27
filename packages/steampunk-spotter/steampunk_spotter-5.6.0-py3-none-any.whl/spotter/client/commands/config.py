"""Provide config CLI command."""

from typing import TYPE_CHECKING

from spotter.client.commands.config_commands import config_clear, config_get, config_set
from spotter.client.utils import UsagePrefixRawDescriptionHelpFormatter

if TYPE_CHECKING:
    import argparse


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for config command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "config",
        help="Manage configuration for organization",
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog,
            usage_prefix="Manage organization-level file with configuration (e.g., for enforcing and skipping checks)",
            max_help_position=48,
        ),
        usage="spotter config [OPTIONS] <COMMAND>",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument(
        "--organization-id",
        type=str,
        help="UUID of an existing Steampunk Spotter organization manage configuration for "
        "(default organization will be used if not specified)",
    )

    subparsers = parser.add_subparsers()
    cmds = [
        (config_get.__name__.rsplit(".", maxsplit=1)[-1], config_get),
        (config_set.__name__.rsplit(".", maxsplit=1)[-1], config_set),
        (config_clear.__name__.rsplit(".", maxsplit=1)[-1], config_clear),
    ]
    for _, module in cmds:
        module.add_parser(subparsers)
