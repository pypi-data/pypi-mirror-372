import re
from typing import Any, Dict

from colorama import Fore, Style

from spotter.library.scanning.check_result import CheckResult
from spotter.library.scanning.display_level import DisplayLevel
from spotter.library.scanning.item_metadata import ItemMetadata
from spotter.library.scanning.result import ScanResult


def format_scan_result_to_dict(scan_result: ScanResult, show_docs_url: bool, show_scan_url: bool) -> Dict[str, Any]:
    check_result_outputs = []
    for result in scan_result.check_results:
        metadata = result.metadata or ItemMetadata(file_name="", line=0, column=0)
        catalog_info = result.catalog_info
        suggestion_dict = {}
        if result.suggestion:
            suggestion_dict = {
                "start_mark": result.suggestion.start_mark,
                "end_mark": result.suggestion.end_mark,
                "suggestion": result.suggestion.suggestion_spec,
            }

        check_result_outputs.append(
            {
                "task_id": result.correlation_id,  # It is here because we want to be back compatible
                "file": metadata.file_name,
                "line": metadata.line,
                "column": metadata.column,
                "check_class": catalog_info.check_class,
                "event_code": catalog_info.event_code,
                "event_value": catalog_info.event_value,
                "event_message": catalog_info.event_message,
                "event_subcode": catalog_info.event_subcode,
                "event_submessage": catalog_info.event_submessage,
                "level": result.level.name.strip(),
                "message": result.message.strip(),
                "suggestion": suggestion_dict,
                "doc_url": result.doc_url if show_docs_url else None,
                "correlation_id": result.correlation_id,
                "check_type": result.check_type.name.strip(),
            }
        )

    return {
        "uuid": scan_result.uuid,
        "user": scan_result.user,
        "user_info": scan_result.user_info,
        "project": scan_result.project,
        "organization": scan_result.organization,
        "environment": scan_result.environment,
        "scan_date": scan_result.scan_date,
        "subscription": scan_result.subscription,
        "is_paid": scan_result.is_paid,
        "web_urls": scan_result.web_urls if show_scan_url else None,
        "summary": {
            "scan_time": scan_result.summary.scan_time,
            "num_errors": scan_result.summary.num_errors,
            "num_warnings": scan_result.summary.num_warnings,
            "num_hints": scan_result.summary.num_hints,
            "status": scan_result.summary.status,
        },
        "scan_progress": {
            "progress_status": str(scan_result.scan_progress.progress_status),
            "current": scan_result.scan_progress.current,
            "total": scan_result.scan_progress.total,
        },
        "check_results": check_result_outputs,
    }


def format_check_result(
    check_result: CheckResult, show_colors: bool, show_docs_url: bool, rewriting_enabled: bool
) -> str:
    # or: we can have results that relate to Environment - no file and position
    metadata = check_result.metadata or ItemMetadata(file_name="", line=0, column=0)
    result_level = check_result.level.name.strip().upper()
    file_location = f"{metadata.file_name}:{metadata.line}:{metadata.column}"

    if check_result.catalog_info.event_subcode:
        out_prefix = (
            f"{file_location}: {result_level}: "
            f"[{check_result.catalog_info.event_code}::{check_result.catalog_info.event_subcode}]"
        )
    else:
        out_prefix = f"{file_location}: {result_level}: [{check_result.catalog_info.event_code}]"

    out_message = check_result.message.strip()
    if show_colors:
        if result_level == DisplayLevel.ERROR.name:
            out_prefix = Fore.RED + out_prefix + Fore.RESET
            out_message = re.sub(r"'([^']*)'", Style.BRIGHT + Fore.RED + r"\1" + Fore.RESET + Style.NORMAL, out_message)
        elif result_level == DisplayLevel.WARNING.name:
            out_prefix = Fore.YELLOW + out_prefix + Fore.RESET
            out_message = re.sub(
                r"'([^']*)'", Style.BRIGHT + Fore.YELLOW + r"\1" + Fore.RESET + Style.NORMAL, out_message
            )
        else:
            out_message = re.sub(r"'([^']*)'", Style.BRIGHT + r"\1" + Style.NORMAL, out_message)

    if check_result.suggestion and rewriting_enabled:
        out_rewritable = "(rewritable)"
        if show_colors:
            out_rewritable = f"({Fore.MAGENTA}rewritable{Fore.RESET})"
        out_prefix = f"{out_prefix} {out_rewritable}"

    output = f"{out_prefix} {out_message}".strip()
    if not output.endswith("."):
        output += "."
    if show_docs_url and check_result.doc_url:
        out_docs = f"View docs at {check_result.doc_url} for more info."
        if show_colors:
            out_docs = f"View docs at {Fore.CYAN}{check_result.doc_url}{Fore.RESET} for more info."
        output = f"{output} {out_docs}"

    return output
