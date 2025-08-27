"""Provide config clear CLI command."""

import argparse
import sys
from pathlib import Path
from typing import List

from spotter.client.utils import UsagePrefixRawDescriptionHelpFormatter
from spotter.library.builder.builder import SpotterBuilder
from spotter.library.builder.utils import (
    is_ansible_builder_installed,
    is_ansible_galaxy_installed,
)


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for config clear command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "build",
        help="Build execution environment which includes steampunk spotter.",
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog,
            usage_prefix="Build a ready-to-use container image with steampunk spotter integrated"
            " and preserved build context, which you can use to rebuild the image at a "
            "different time and/or location with the tooling of your choice.",
            max_help_position=48,
        ),
        add_help=False,
    )
    parser.add_argument("positionals", type=str, nargs="+", help="Ansible builder flags")
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace, project_root: Path) -> None:
    """
    Execute callback for build command.

    :param args: Argparse arguments
    :param project_root: The root directory of the project
    """
    try:
        internal_parser = argparse.ArgumentParser(
            usage="spotter build [-h] [--file FILE] positionals [positionals ...]",
            prog="build",
            description="positional arguments:\n  *  Other ansible-builder arguments passed through.",
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=True,
        )
        internal_parser.add_argument("--file", type=str)
        new_args, leftovers = internal_parser.parse_known_args(args.positionals)

        ansible_build(new_args.file, leftovers, project_root)
    except Exception as e:  # noqa: BLE001  # safety catchall
        print(f"Something went wrong while building your spotter execution environment image: \n {e}")


def ansible_build(file: Path, leftover_args: List[str], project_root: Path) -> None:
    """
    Run spotter builder

    :param file: Path to execution_environment.yml
    :param leftover_args: Leftover arguments of internal parser
    :param project_root: Project root path
    """
    if file is None:
        print("File path is missing. Please provide it with --file flag.")
        sys.exit(1)
    if not is_ansible_builder_installed():
        print("To execute the spotter build command, ansible-builder must be installed.")
        sys.exit(2)
    if not is_ansible_galaxy_installed():
        print("To execute the spotter build command, ansible-core must be installed.")
        sys.exit(3)

    builder = SpotterBuilder(file, leftover_args, project_root)
    builder.build()
