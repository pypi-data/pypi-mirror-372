"""Provide scan CLI command."""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Optional

from pydantic_core import to_jsonable_python
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.style import Style
from rich.theme import Theme

from spotter.client.utils import CommonParameters, UsagePrefixRawDescriptionHelpFormatter, get_absolute_path
from spotter.library.api import ApiClient
from spotter.library.compat.rich import compat_progress_total
from spotter.library.environment import Environment
from spotter.library.formatting.choices import OutputFormat
from spotter.library.formatting.models import OutputFormatOptions
from spotter.library.parsing.noqa_comments import SpotterNoqa
from spotter.library.parsing.parsing import ParsingResult, parse_ansible_artifacts
from spotter.library.scanning.display_level import DisplayLevel
from spotter.library.scanning.origin import Origin
from spotter.library.scanning.payload import Payload, PayloadV4
from spotter.library.scanning.progress import Progress as ScanProgress
from spotter.library.scanning.progress_status import ProgressStatus as ScanProgressStatus
from spotter.library.scanning.result import ScanResult
from spotter.library.scanning.start_async import StartAsync
from spotter.library.storage import Storage
from spotter.library.utils import get_current_cli_version, get_relative_path_to_cwd


def add_parser(subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    """
    Add a new scan command parser to subparsers.

    :param subparsers: Subparsers action
    """
    parser = subparsers.add_parser(
        "scan",
        help="Initiate Ansible scan",
        formatter_class=lambda prog: UsagePrefixRawDescriptionHelpFormatter(
            prog, usage_prefix="Initiate Ansible scan", max_help_position=72
        ),
        usage="spotter scan [OPTIONS] [PATH ...]",
        add_help=False,
    )
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument(
        "-p",
        "--project-id",
        type=str,
        help="UUID of an existing Steampunk Spotter project where the scan result will be stored "
        "(default project from the default organization will be used if not specified)",
    )
    parser.add_argument("-c", "--config", type=get_absolute_path, help="Configuration file (as JSON/YAML)")

    ansible_version_group = parser.add_mutually_exclusive_group()
    ansible_version_group.add_argument(
        "-a",
        "--ansible-version",
        type=str,
        choices=[
            "2.0",
            "2.1",
            "2.2",
            "2.3",
            "2.4",
            "2.5",
            "2.6",
            "2.7",
            "2.8",
            "2.9",
            "2.10",
            "2.11",
            "2.12",
            "2.13",
            "2.14",
            "2.15",
            "2.16",
            "2.17",
            "2.18",
        ],
        metavar="[2.0, 2.18]",
        help="Target Ansible Core version to scan against (e.g., 2.18). If not specified, Spotter will try to discover "
        "it on your system. If not found, all Ansible versions are considered.",
    )
    ansible_version_group.add_argument(
        "--no-ansible-version", action="store_true", help="Disable automatic discovery of Ansible versions."
    )
    parser.add_argument(
        "--exclude-values", action="store_true", help="Omit parsing and uploading values from Ansible playbooks"
    )
    parser.add_argument("--include-vars", action="store_true", help="Parse and upload content from Ansible vars")
    parser.add_argument(
        "--exclude-metadata",
        action="store_true",
        help="Omit collecting and uploading metadata (i.e., file names, line and column numbers)",
    )
    parser.add_argument(
        "--exclude-environment",
        action="store_true",
        help="Omit collecting and uploading environment data "
        "(i.e., installed collection and roles, pip packages, ansible config)",
    )
    parser.add_argument(
        "--exclude-paths",
        nargs="?",
        action="append",
        default=[],
        type=lambda p: get_absolute_path(p, False),
        help="Omit scanning of specific paths (e.g., --exclude-paths file.yml --exclude-paths folder/)",
    )
    parser.add_argument("-r", "--rewrite", action="store_true", help="Rewrite files with fixes")
    parser.add_argument(
        "-l",
        "--display-level",
        type=DisplayLevel.from_string,
        choices=[DisplayLevel.HINT, DisplayLevel.WARNING, DisplayLevel.ERROR],
        default=DisplayLevel.HINT,
        help="Display only check results with specified level or greater "
        "(e.g., -l warning will show all warnings and errors, but suppress hints)",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="default",
        help="Set profile with selected set of checks to be used for scanning",
    )
    parser.add_argument(
        "--skip-checks",
        nargs="?",
        action="append",
        default=[],
        help="Skip checks with specified IDs (e.g., --skip-checks E101,H500,W1800)",
    )
    parser.add_argument(
        "--enforce-checks",
        nargs="?",
        action="append",
        default=[],
        help="Enforce checks with specified IDs (e.g., --enforce-checks E001,W400,H904)",
    )
    parser.add_argument("--no-docs-url", action="store_true", help="Disable outputting URLs to documentation")
    parser.add_argument("--no-scan-url", action="store_true", help="Disable outputting URL to scan result")
    parser.add_argument("--no-progress", action="store_true", help="Disable showing scanning progress")
    parser.add_argument("--skip-detect-secrets", action="store_true", help="Disable obfuscation of sensitive data")
    parser.add_argument(
        "--junit-xml",
        type=lambda p: get_absolute_path(p, False),
        help="Output file path to export the scan result to a file in JUnit XML format",
    )
    parser.add_argument(
        "--sarif",
        type=lambda p: get_absolute_path(p, False),
        help="Output file path to export the scan result to a file in Sarif format",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=OutputFormat.from_string,
        choices=list(OutputFormat),
        default=OutputFormat.TEXT,
        help="Output format for the scan result",
    )
    parser.add_argument(
        "--output",
        type=lambda p: get_absolute_path(p, False),
        help="Output file path where the formatted scan result will be exported to",
    )
    import_export_group = parser.add_mutually_exclusive_group()
    import_export_group.add_argument(
        "-i",
        "--import-payload",
        type=get_absolute_path,
        help="Path to the previously exported file to be sent for scanning",
    )
    import_export_group.add_argument(
        "-e",
        "--export-payload",
        type=lambda p: get_absolute_path(p, False),
        help="Output file path to export the locally scanned data without sending anything for scanning at the server",
    )
    parser.add_argument(
        "--origin",
        type=Origin.from_string,
        choices=list(Origin),
        default=Origin.CLI,
        help="Source that scan originates from (i.e., cli, ci, ide)",
    )
    parser.add_argument("path", type=get_absolute_path, nargs="*", help="Path to Ansible artifact or directory")
    parser.set_defaults(func=_parser_callback)


def _parser_callback(args: argparse.Namespace, project_root: Path) -> None:
    """
    Execute callback for scan command.

    :param args: Argparse arguments
    :param project_root: The root directory of the project.
    """
    common_params = CommonParameters.from_args(args)
    scan_paths = args.path

    if args.import_payload and scan_paths:
        print("Error: the --import-payload is mutually exclusive with positional arguments.", file=sys.stderr)
        sys.exit(2)

    if (
        args.export_payload
        and not scan_paths
        or (not args.export_payload and not args.import_payload and not scan_paths)
    ):
        print("Error: no paths provided for scanning.", file=sys.stderr)
        sys.exit(2)

    if args.export_payload and args.exclude_metadata:
        print(
            "Warning: exporting without the metadata will not allow you to properly import payload. "
            "Consider omitting the --exclude-metadata option.",
            file=sys.stderr,
        )

    # handle cases where this function is called directly with incorrect types of parameters
    if isinstance(args.format, str):
        args.format = OutputFormat.from_string(args.format)

    # ensure that colors and showing progress are possible only for text output that will be printed to the console
    if args.output or args.format != OutputFormat.TEXT:
        args.no_color = True
        args.no_progress = True

    scan(
        common_params.api_endpoint,
        common_params.storage_path,
        common_params.api_token,
        common_params.username,
        common_params.password,
        common_params.timeout,
        args.no_color,
        args.no_progress,
        args.project_id,
        args.config,
        args.ansible_version,
        args.no_ansible_version,
        not args.exclude_values,
        not args.exclude_metadata,
        args.exclude_environment,
        args.rewrite,
        args.display_level,
        args.profile,
        args.skip_checks,
        args.enforce_checks,
        args.no_docs_url,
        args.no_scan_url,
        args.format,
        args.output,
        args.junit_xml,
        args.sarif,
        args.import_payload,
        args.export_payload,
        args.origin,
        args.exclude_paths,
        scan_paths,
        common_params.debug,
        common_params.cacert,
        common_params.verify,
        args.include_vars,
        args.skip_detect_secrets,
    )


def exponential_backoff(iteration: int) -> None:
    """
    Increment sleep between requesting scan status.

    :param iteration: Iteration number
    """
    if iteration == 0:
        return
    time.sleep(0.1 if iteration == 1 else 0.5)


def scan(  # noqa: PLR0912,PLR0915  # TODO: oh dear
    api_endpoint: str,
    storage_path: Path,
    api_token: Optional[str],
    username: Optional[str],
    password: Optional[str],
    timeout: Optional[int],
    no_color: bool,
    no_progress: bool,
    project_id: Optional[str],
    config_path: Optional[Path],
    ansible_version: Optional[str],
    no_ansible_version: bool,
    include_values: bool,
    include_metadata: bool,
    exclude_environment: bool,
    rewrite: bool,
    display_level: DisplayLevel,
    profile: str,
    skip_checks: List[str],
    enforce_checks: List[str],
    no_docs_url: bool,
    no_scan_url: bool,
    output_format: OutputFormat,
    output_path: Optional[Path],
    junit_xml: Optional[Path],
    sarif: Optional[Path],
    import_payload: Optional[Path],
    export_payload: Optional[Path],
    origin: Origin,
    exclude_paths: Optional[List[Path]],
    scan_paths: List[Path],
    debug: bool,
    cacert: Optional[Path],
    verify: bool,
    include_vars: bool,
    skip_detect_secrets: bool,
) -> None:
    """
    Scan Ansible content and return scan result.

    :param api_endpoint: Steampunk Spotter API endpoint
    :param storage_path: Path to storage
    :param api_token: Steampunk Spotter API token
    :param username: Steampunk Spotter username
    :param password: Steampunk Spotter password
    :param timeout: Steampunk Spotter API timeout (in seconds)
    :param no_color: Disable output colors
    :param no_progress: Disable showing progress
    :param project_id: UUID of an existing Steampunk Spotter project
    :param config_path: Path to configuration file
    :param ansible_version: Target Ansible version to scan against (e.g., 2.14)
    :param no_ansible_version: Set target Ansible version to scan against as unknown
    :param include_values: Parse and upload values from Ansible task parameters to the server
    :param include_metadata: Upload metadata (i.e., file names, line and column numbers) to the server
    :param rewrite: Rewrite files with fixes
    :param display_level: Display only check results with specified level or greater
    :param profile: Profile with selected set of checks to be used for scanning
    :param skip_checks: List of check IDs for checks to be skipped
    :param enforce_checks: List of check IDs for checks to be enforced
    :param no_docs_url: Disable outputting URLs to documentation
    :param no_scan_url: Disable outputting URL to scan result
    :param junit_xml: Path where JUnit XML report will be exported to
    :param sarif: Path where Sarif report will be exported to
    :param output_format: Output format of the scan result
    :param output_path: Output file path where the formatted scan result will be exported to
    :param import_payload: Path to the previously exported file to be sent for scanning
    :param export_payload: Path to export the locally scanned data without sending anything for scanning to the server
    :param origin: A source where the scanning is initiated from
    :param exclude_paths: Files and folders to exclude from scan
    :param scan_paths: Path to Ansible artifact or directory
    :param debug: Enable debug mode
    :param cacert: Path to file containing root CA certificates. If not listed, system's default will be used.
    :param verify: Verify server certificate
    :param include_vars: Parse and upload content from Ansible vars
    """
    # create and set environment
    # the order that we read configuration is the following (in each step we overwrite what the previous one has):
    # 1. local discovery (from user's current workspace)
    # 2. project config file (.spotter.json/.spotter.yml/.spotter.yaml file in the current working directory)
    # 3. config file (JSON/YAML file provided after --config flag)
    # 4. optional CLI arguments (e.g., --ansible-version)
    environment = Environment.from_local_discovery(scan_paths)
    environment = environment.combine(Environment.from_project_configuration_file())
    if config_path:
        environment = environment.combine(Environment.from_config_file(config_path))
    if ansible_version and environment.ansible_version:
        environment.ansible_version.ansible_core = ansible_version
    if no_ansible_version and environment.ansible_version:
        environment.ansible_version.ansible_core = None
        environment.ansible_version.ansible_base = None
        environment.ansible_version.ansible = None
    cli_scan_args_skip_checks = []
    cli_scan_args_enforce_checks = []
    if environment.cli_scan_args:
        cli_scan_args_skip_checks = environment.cli_scan_args.get("skip_checks", [])
        cli_scan_args_enforce_checks = environment.cli_scan_args.get("enforce_checks", [])
    if skip_checks:
        cli_scan_args_skip_checks = []
        for skip_check in skip_checks:
            cli_scan_args_skip_checks.extend(SpotterNoqa.parse_noqa_comment(skip_check, use_noqa_regex=False))
    if enforce_checks:
        cli_scan_args_enforce_checks = []
        for enforce_check in enforce_checks:
            cli_scan_args_enforce_checks.extend(SpotterNoqa.parse_noqa_comment(enforce_check, use_noqa_regex=False))

    environment = environment.combine(
        Environment(
            cli_scan_args={
                "parse_values": include_values,
                # FIXME: Remove this deprecated option that is currently mandatory on backend.
                "include_values": include_values,
                "include_metadata": include_metadata,
                "include_environment": not exclude_environment,
                "rewrite": rewrite,
                "display_level": str(display_level),
                "profile": str(profile),
                "skip_checks": cli_scan_args_skip_checks,
                "enforce_checks": cli_scan_args_enforce_checks,
                "version": get_current_cli_version(),
                "origin": str(origin),
                "include_vars": include_vars,
            }
        )
    )

    progress_custom_theme = Theme(
        {
            "bar.pulse": Style(color="rgb(103,174,202)"),
            "bar.complete": Style(color="rgb(103,174,202)"),
            "bar.finished": Style(color="rgb(86,194,133)"),
            "progress.percentage": Style(color="rgb(103,174,202)"),
            "progress.elapsed": Style.null(),
            "progress.remaining": Style.null(),
        }
    )
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=Console(theme=progress_custom_theme, no_color=no_color),
    )
    if no_progress:
        progress.disable = True

    with progress:
        progress_task = progress.add_task("Parsing...", total=compat_progress_total(progress))
        if import_payload:
            parsing_result = ParsingResult(
                tasks=[],
                playbooks=[],
                blocks=[],
                dynamic_inventories=[],
                roles=[],
                plugins=[],
                variables=[],
                errors=[],
                included_files_count=0,
                excluded_paths_count=0,
                path_loops_detected=0,
            )
            scan_payload = PayloadV4.from_args(
                parsing_result, environment, include_metadata, exclude_environment, import_payload
            )
            parsing_result.tasks = scan_payload.tasks
            parsing_result.playbooks = scan_payload.playbooks
            parsing_result.blocks = scan_payload.blocks or []
            parsing_result.dynamic_inventories = scan_payload.dynamic_inventories or []
            parsing_result.roles = scan_payload.roles or []
            parsing_result.variables = scan_payload.variables or []
            parsing_result.included_files_count = (
                scan_payload.statistics.included_files_count if scan_payload.statistics else 0
            )
            parsing_result.excluded_paths_count = (
                scan_payload.statistics.excluded_paths_count if scan_payload.statistics else 0
            )
            parsing_result.path_loops_detected = (
                scan_payload.statistics.path_loops_detected if scan_payload.statistics else 0
            )
        else:
            parsing_result = parse_ansible_artifacts(
                scan_paths,
                exclude_paths,
                parse_values=bool(include_values),
                parse_vars=include_vars,
                skip_detect_secrets=skip_detect_secrets,
            )
            scan_payload = PayloadV4.from_args(
                parsing_result, environment, include_metadata, exclude_environment, import_payload
            )

        if export_payload:
            scan_payload.to_json_file(export_payload)
            file_name = get_relative_path_to_cwd(str(export_payload))

            progress_custom_theme.styles["progress.percentage"] = Style(color="rgb(86,194,133)")
            progress.console.use_theme(progress_custom_theme)
            if compat_progress_total(progress):
                progress.update(progress_task, advance=compat_progress_total(progress))
            else:
                progress.update(progress_task, total=100.0, advance=100.0)
            progress.stop()
            if not no_progress:
                print()

            ### Yaml errors should be also shown on export
            if len(parsing_result.errors) > 0:
                print("YAML parsing errors")
                parsing_errors = "\n".join(
                    f"{error.file_path}:{error.line}:{error.column}: {error.description}"
                    for error in parsing_result.errors
                )
                print(parsing_errors)
                print()
            print(
                f"Scan data saved to {file_name}.\nNote: this operation is fully offline. No actual scan was executed."
            )
            sys.exit(0)
        else:
            storage = Storage(storage_path)
            api_client = ApiClient(api_endpoint, storage, api_token, username, password, debug, cacert, verify)
            api_client.debug_print_me()

            supported_api_version = api_client.negotiate_api_version()
            if supported_api_version == "v3":
                versioned_scan_payload: Payload = scan_payload.as_payload_v3()
            else:
                versioned_scan_payload = scan_payload

            progress.update(progress_task, description="Scanning...", total=compat_progress_total(progress))
            if project_id:
                api_client.debug_print("Scanning with project id {}", project_id)
                api_client.debug_project(project_id)
                scan_start_time = time.time()
                response_scan_async = api_client.post(
                    f"/{supported_api_version}/scans_async/?project={project_id}",
                    payload=to_jsonable_python(versioned_scan_payload),
                    timeout=timeout if timeout else 120,
                )
            else:
                api_client.debug_print("Scanning with default organization and project")
                api_client.debug_my_default_organization()
                scan_start_time = time.time()
                response_scan_async = api_client.post(
                    f"/{supported_api_version}/scans_async/",
                    payload=to_jsonable_python(versioned_scan_payload),
                    timeout=timeout if timeout else 120,
                )

            try:
                response_scan_start_json = response_scan_async.json()
                scan_start_async = StartAsync.from_api_response(response_scan_start_json)
                scan_progress = scan_start_async.scan_progress
                progress.update(
                    progress_task,
                    description=f"Scanning ({scan_progress.progress_status})...",
                    total=compat_progress_total(progress),
                )

                response_scan_result_json = {}
                ending_statuses = [s.value for s in ScanProgressStatus if s.value > 1]

                iteration = 0
                while scan_progress.progress_status.value not in ending_statuses:
                    exponential_backoff(iteration)
                    iteration = iteration + 1

                    response_scan = api_client.get(
                        f"/{supported_api_version}/scans/{scan_start_async.uuid}", timeout=timeout if timeout else 120
                    )
                    response_scan_result_json = response_scan.json()
                    scan_progress = ScanProgress.from_api_response_element(
                        response_scan_result_json.get("scan_progress", None)
                    )
                    if scan_progress.progress_status.value > 0:
                        progress.update(
                            progress_task,
                            description=f"Scanning ({scan_progress.progress_status})...",
                            completed=scan_progress.current,
                            total=scan_progress.total,
                            advance=scan_progress.current,
                        )

                scan_time = time.time() - scan_start_time
            except json.JSONDecodeError as e:
                print(f"Error: error when converting to JSON: {e!s}", file=sys.stderr)
                sys.exit(2)

            if scan_progress.progress_status == ScanProgressStatus.SUCCESS:
                progress_custom_theme.styles["progress.percentage"] = Style(color="rgb(86,194,133)")
            else:
                progress_custom_theme.styles["bar.finished"] = Style(color="rgb(249,78,112)")
                progress_custom_theme.styles["progress.percentage"] = Style(color="rgb(249,78,112)")

            progress.console.use_theme(progress_custom_theme)
            progress.update(progress_task, description=f"Scanning...{scan_progress.progress_status}.")
            progress.stop()
            if not no_progress:
                print()

            scan_result = ScanResult.from_api_response(
                response_scan_result_json,
                parsing_result.tasks,
                parsing_result.playbooks,
                parsing_result.dynamic_inventories,
                parsing_result.variables,
                scan_time,
            )

            # we have to do rewrite before any filtering and sorting to keep original order of check results
            if rewrite:
                scan_result.apply_check_result_suggestions(display_level, scan_paths)

            # TODO: figure out if we can filter and/or sort returned check results on the backend
            scan_result.filter_check_results(display_level)
            scan_result.sort_check_results()

            format_options = OutputFormatOptions(
                show_docs_url=not no_docs_url,
                show_scan_url=not no_scan_url,
                show_colors=not no_color,
                rewriting_enabled=rewrite,
            )

            try:
                formatted_output = output_format.formatter().format(scan_result, parsing_result, format_options)
                if output_path:
                    output_path.write_text(formatted_output, encoding="utf-8")
                    print(f"Scan result exported to {output_path}.", file=sys.stderr)
                else:
                    print(formatted_output)

                if junit_xml:
                    junit_xml_string = OutputFormat.JUNIT.formatter().format(
                        scan_result, parsing_result, format_options
                    )
                    junit_xml.write_text(junit_xml_string, encoding="utf-8")
                    print(f"JUnitXML report saved to {junit_xml}.", file=sys.stderr)
                if sarif:
                    sarif_string = OutputFormat.SARIF.formatter().format(scan_result, parsing_result, format_options)
                    sarif.write_text(sarif_string, encoding="utf-8")
                    print(f"Sarif report saved to {sarif}.", file=sys.stderr)
            except TypeError as e:
                print(f"Error: {e!s}", file=sys.stderr)
                sys.exit(2)

            if len(scan_result.check_results) > 0:
                sys.exit(1)
