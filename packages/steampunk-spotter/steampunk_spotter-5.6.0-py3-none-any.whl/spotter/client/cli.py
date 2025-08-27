"""Provide main CLI parser."""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, NoReturn

import colorama

from spotter.client.commands import (
    build,
    clear_config,
    clear_policies,
    config,
    get_config,
    login,
    logout,
    policies,
    register,
    scan,
    set_config,
    set_policies,
    suggest,
)
from spotter.client.utils import PrintCurrentVersionAction, UsagePrefixRawDescriptionHelpFormatter, get_absolute_path
from spotter.library.api import ApiClient
from spotter.library.storage import Storage
from spotter.library.utils import validate_url


class ArgParser(argparse.ArgumentParser):
    """An argument parser that displays help on error."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._positionals.title = "Arguments"
        self._optionals.title = "Options"

    def error(self, message: str) -> NoReturn:
        """
        Overridden the original error method.

        :param message: Error message
        """
        print(f"Error: {message}\n", file=sys.stderr)
        self.print_help()
        sys.exit(2)

    def add_subparsers(self, **kwargs: Dict[str, Any]) -> argparse._SubParsersAction:  # type: ignore
        """Overridden the original add_subparsers method (workaround for http://bugs.python.org/issue9253)."""
        subparsers = super().add_subparsers()
        subparsers.required = True
        subparsers.dest = "command"
        self._positionals.title = "Commands"
        return subparsers


def create_parser() -> ArgParser:
    """
    Create argument parser for CLI.

    :return: Parser as argparse.ArgumentParser object
    """
    parser = ArgParser(
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog,
            usage_prefix="Steampunk Spotter - Ansible Playbook Platform that scans, analyzes, enhances, and "
            "provides insights for your playbooks.",
            max_help_position=48,
        ),
        epilog="Additional information:\n"
        "  You will need Steampunk Spotter account to be able to use the CLI.\n"
        "  Run spotter register command or visit https://spotter.steampunk.si/ to create one.\n\n"
        "  To log in to Steampunk Spotter, you should provide your API token or username and password:\n"
        "    - using spotter login command;\n"
        "    - via --token/-t option;\n"
        "    - by setting SPOTTER_TOKEN environment variable;\n"
        "    - via --username/-u and --password/-p global options;\n"
        "    - by setting SPOTTER_USERNAME and SPOTTER_PASSWORD environment variables.\n\n"
        "  Refer to Steampunk Spotter Documentation at https://spotter.steampunk.si/docs/ for further instructions.\n"
        "  What do you think about Spotter? Visit https://spotter.steampunk.si/feedback to share your thoughts.\n"
        "  Need more help or having other questions? Visit https://steampunk.si/contact/ to contact us.",
        add_help=False,
        usage="spotter [OPTIONS] <COMMAND>",
    )

    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument(
        "-v",
        "--version",
        action=PrintCurrentVersionAction,
        nargs=0,
        help="Display the version of Steampunk Spotter CLI",
    )
    parser.add_argument(
        "-e",
        "--endpoint",
        type=validate_url,
        help=f"Steampunk Spotter API endpoint (instead of default {ApiClient.DEFAULT_ENDPOINT})",
    )
    parser.add_argument(
        "-s",
        "--storage-path",
        type=lambda p: get_absolute_path(p, False),
        help=f"Storage folder location (instead of default {Storage.DEFAULT_PATH})",
    )
    parser.add_argument("-t", "--token", type=str, help="Steampunk Spotter API token")
    parser.add_argument("--api-token", type=str, help=argparse.SUPPRESS)
    parser.add_argument("-u", "--username", type=str, help="Steampunk Spotter username")
    parser.add_argument("-p", "--password", type=str, help="Steampunk Spotter password")
    parser.add_argument("--timeout", type=int, help="Steampunk Spotter API timeout (in seconds)")
    parser.add_argument("--no-color", action="store_true", help="Disable output colors")
    parser.add_argument("--no-colors", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")

    cert_group = parser.add_mutually_exclusive_group()
    cert_group.add_argument(
        "--cacert",
        type=lambda p: get_absolute_path(p, False),
        help="Path to file containing root CA certificates. If not listed, system's default will be used.",
    )
    cert_group.add_argument(
        "-k",
        "--insecure",
        action="store_true",
        help="Do not verify server certificate.",
    )
    subparsers = parser.add_subparsers()
    cmds = [
        (register.__name__.rsplit(".", maxsplit=1)[-1], register),
        (login.__name__.rsplit(".", maxsplit=1)[-1], login),
        (logout.__name__.rsplit(".", maxsplit=1)[-1], logout),
        (scan.__name__.rsplit(".", maxsplit=1)[-1], scan),
        (suggest.__name__.rsplit(".", maxsplit=1)[-1], suggest),
        (set_policies.__name__.rsplit(".", maxsplit=1)[-1], set_policies),
        (clear_policies.__name__.rsplit(".", maxsplit=1)[-1], clear_policies),
        (get_config.__name__.rsplit(".", maxsplit=1)[-1], get_config),
        (set_config.__name__.rsplit(".", maxsplit=1)[-1], set_config),
        (clear_config.__name__.rsplit(".", maxsplit=1)[-1], clear_config),
        (config.__name__.rsplit(".", maxsplit=1)[-1], config),
        (policies.__name__.rsplit(".", maxsplit=1)[-1], policies),
        (build.__name__.rsplit(".", maxsplit=1)[-1], build),
    ]
    for _, module in cmds:
        module.add_parser(subparsers)

    return parser


def get_args() -> List[str]:
    args = sys.argv[1:]
    if "build" in args:
        args.insert(sys.argv.index("build"), "--")
    return args


def get_project_root() -> Path:
    executing_file = os.path.realpath(__file__)
    project_root = Path(os.path.realpath(executing_file)).parent.parent
    return project_root


def main() -> None:
    """Create main CLI parser and parse arguments."""
    parser = create_parser()
    cmd_args = get_args()
    args = parser.parse_args(args=cmd_args)
    project_root = get_project_root()
    if args.api_token:
        print("Warning: the --api-token option is deprecated. Use --token instead.", file=sys.stderr)
        args.token = args.api_token
    if args.no_colors:
        print("Warning: the --no-colors option is deprecated. Use --no-color instead.", file=sys.stderr)
        args.no_color = args.no_colors

    # init colorama if only when using colors
    if not args.no_color:
        colorama.init(autoreset=True)
    # check if any of the arguments is empty
    args_dict = vars(args)
    for k in args_dict:
        if args_dict[k] == "":
            print(
                f"Error: --{k.replace('_', '-')} argument is empty. "
                f"Please set the non-empty value or omit the argument if it is not needed.",
                file=sys.stderr,
            )
            sys.exit(2)
    args.func(args, project_root)


if __name__ == "__main__":
    main()
