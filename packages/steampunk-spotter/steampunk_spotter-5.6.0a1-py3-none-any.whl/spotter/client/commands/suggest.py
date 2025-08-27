"""Provide suggest CLI command."""

import argparse
import json
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

from spotter.client.utils import CommonParameters, UsagePrefixRawDescriptionHelpFormatter
from spotter.library.api import ApiClient
from spotter.library.storage import Storage


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new parser for suggest command to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "suggest",
        argument_default=argparse.SUPPRESS,
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog, usage_prefix="Get suggestions from Spotter's AI component", max_help_position=48
        ),
        usage="spotter suggest [OPTIONS] <QUERY>",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument(
        "-n",
        "--num-results",
        type=int,
        default=5,
        choices=range(1, 51),
        metavar="[1, 50]",
        help="Number of expected suggestions",
    )
    parser.add_argument(
        "query", type=str, help="Query that will be used to produce a suggestion from Spotter's AI component"
    )
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace, project_root: Path) -> None:
    """
    Execute callback for suggest command.

    :param args: Argparse arguments
    :param project_root: The root directory of the project.
    """
    common_params = CommonParameters.from_args(args)

    suggestions = suggest(
        common_params.api_endpoint,
        common_params.storage_path,
        common_params.api_token,
        common_params.username,
        common_params.password,
        common_params.timeout,
        args.query,
        args.num_results,
        common_params.cacert,
        common_params.verify,
    )

    try:
        print(json.dumps(suggestions, indent=2))
    except TypeError as e:
        print(f"Error: unable to serialize the object to JSON: {e!s}", file=sys.stderr)
        sys.exit(2)


def suggest(
    api_endpoint: str,
    storage_path: Path,
    api_token: Optional[str],
    username: Optional[str],
    password: Optional[str],
    timeout: Optional[int],
    query: str,
    num_results: int,
    cacert: Optional[Path],
    verify: bool,
) -> List[Dict[str, Any]]:
    """
    Suggest module and task examples by calling Spotter's AI component.

    :param api_endpoint: Steampunk Spotter API endpoint
    :param storage_path: Path to storage
    :param api_token: Steampunk Spotter API token
    :param username: Steampunk Spotter username
    :param password: Steampunk Spotter password
    :param timeout: Steampunk Spotter API timeout (in seconds)
    :param query: Query that will be used to produce a suggestion from Spotter's AI component
    :param num_results: Number of expected suggestions
    :param cacert: Path to file containing root CA certificates. If not listed, system's default will be used.
    :param verify: Verify server certificate
    :return: List of suggestions
    """
    storage = Storage(storage_path)
    api_client = ApiClient(api_endpoint, storage, api_token, username, password, False, cacert, verify)
    query_params = urllib.parse.urlencode({"query": query, "num_results": num_results})
    response = api_client.get(
        f"/v2/ai/query/modules/?{query_params}", timeout=timeout if timeout else ApiClient.DEFAULT_TIMEOUT
    )

    try:
        response_json = response.json()
        results: List[Dict[str, Any]] = response_json.get("results", [])
        results.sort(key=lambda k: k.get("score", 0), reverse=True)
        return results
    except json.JSONDecodeError as e:
        print(f"Error: scan result cannot be converted to JSON: {e!s}", file=sys.stderr)
        sys.exit(2)
