"""Provide utility functions that can be used as helpers throughout the library code."""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

if sys.version_info >= (3, 8):
    from importlib.metadata import PackageNotFoundError as TestError
    from importlib.metadata import distribution as get_distribution
else:
    from pkg_resources import DistributionNotFound as TestError
    from pkg_resources import get_distribution


def get_package_version(package: str, throw: bool) -> Optional[str]:
    """
    Retrieve current version of Python package.

    :return: Version string
    """
    try:
        return get_distribution(package).version
    except TestError as e:
        if throw:
            print(f"Error: retrieving current {package} version failed: {e}", file=sys.stderr)
            sys.exit(2)
    return None


def get_current_cli_version() -> Optional[str]:
    """
    Retrieve current version of Steampunk Spotter CLI (steampunk-spotter Python package).

    :return: Version string
    """
    version = get_package_version("steampunk-spotter", False)
    if not version:
        package_info = subprocess.check_output(["rpm", "-q", "steampunk-spotter"], stderr=subprocess.DEVNULL).decode(
            "utf-8"
        )
        match = re.search(r".*(\d+\.\d+\.\d+).*", package_info)
        return match.group(1) if match else None
    return version


def validate_url(url: str) -> str:
    """
    Validate URL.

    :param url: URL to validate
    :return: The same URL as input
    """
    parsed_url = urlparse(url)
    supported_url_schemes = ("http", "https")
    if parsed_url.scheme not in supported_url_schemes:
        raise argparse.ArgumentTypeError(
            f"URL '{url}' has an invalid URL scheme '{parsed_url.scheme}', "
            f"supported are: {', '.join(supported_url_schemes)}."
        )

    if len(url) > 2048:
        raise argparse.ArgumentTypeError(f"URL '{url}' exceeds maximum length of 2048 characters.")

    if not parsed_url.netloc:
        raise argparse.ArgumentTypeError(f"No URL domain specified in '{url}'.")

    return url


def get_relative_path_to_cwd(file_name: str) -> str:
    """
    Trim the part of the directory that is shared with current working directory if this is possible.

    :param file_name: Name of the file
    :return: Trimmed path or original if trimming is not possible
    """
    try:
        return str(Path(file_name).relative_to(Path.cwd()))
    except (ValueError, TypeError):
        return file_name
