"""Provide register CLI command."""

import argparse
import sys
import webbrowser
from pathlib import Path

from spotter.client.utils import UsagePrefixRawDescriptionHelpFormatter


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for register command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "register",
        help="Register for a new Steampunk Spotter user account",
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog, usage_prefix="Register for a new Steampunk Spotter user account", max_help_position=48
        ),
        usage="spotter register [OPTIONS]",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace, project_root: Path) -> None:
    """
    Execute callback for register command.

    :param args: Argparse arguments
    :param project_root: The root directory of the project.
    """
    register()


def register() -> None:
    """Open the browser at the registration form."""
    registration_url = "https://spotter.steampunk.si/register/team-plan"
    try:
        webbrowser.open(registration_url)
    except webbrowser.Error as e:
        print(
            f"Error: cannot open a browser to display the registration form: {e}.\n"
            f"Please visit {registration_url} in your browser.",
            file=sys.stderr,
        )
        sys.exit(2)
