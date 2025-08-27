from typing import cast

from colorama import Fore, Style

from spotter.library.formatting.models import OutputFormatOptions, OutputFormatter
from spotter.library.formatting.utils import format_check_result
from spotter.library.parsing.parsing import ParsingResult
from spotter.library.scanning.display_level import DisplayLevel
from spotter.library.scanning.result import ScanResult


class TextFormatter(OutputFormatter):
    def format(  # noqa: PLR0912,PLR0915  # TODO: oh dear
        self, scan_result: ScanResult, parsing_result: ParsingResult, options: OutputFormatOptions
    ) -> str:
        output = ""

        parsing_error_label = ""
        parsing_errors = ""
        if len(parsing_result.errors) > 0:
            parsing_error_label = "YAML parsing errors"
            parsing_errors = "\n".join(
                f"{error.file_path}:{error.line}:{error.column}: {error.description}" for error in parsing_result.errors
            )

        fixed_check_results_label = ""
        fixed_check_results = ""
        if scan_result.fixed_check_results:
            fixed_check_results_label = "Rewritten check results"
            for result_fixed in scan_result.fixed_check_results:
                fixed_check_results += (
                    format_check_result(
                        result_fixed,
                        show_colors=options.show_colors,
                        show_docs_url=options.show_docs_url,
                        rewriting_enabled=False,
                    )
                    + "\n"
                )

        check_results_label = ""
        check_results = ""
        if scan_result.check_results:
            check_results_label = "Remaining check results" if scan_result.fixed_check_results else "Check results"
        for check_result in scan_result.check_results:
            check_results += (
                format_check_result(
                    check_result,
                    show_colors=options.show_colors,
                    show_docs_url=options.show_docs_url,
                    rewriting_enabled=True,
                )
                + "\n"
            )

        def level_sort_key(level: DisplayLevel) -> int:
            return cast(int, level.value)

        worst_level = DisplayLevel.SUCCESS
        scan_summary_label = "Scan summary"
        if len(scan_result.check_results) > 0:
            worst_level = max((cr.level for cr in scan_result.check_results), key=level_sort_key)

        if options.rewriting_enabled:
            suggestion_level_file_tuples = [
                (cr.suggestion, cr.metadata.file_name)
                for cr in scan_result.fixed_check_results
                if cr.suggestion is not None and cr.metadata is not None
            ]
        else:
            suggestion_level_file_tuples = [
                (cr.suggestion, cr.metadata.file_name)
                for cr in scan_result.check_results
                if cr.suggestion is not None and cr.metadata is not None
            ]
        rewrite_files_len = len({t[1] for t in suggestion_level_file_tuples})
        rewrite_message = (
            f"{'Did' if options.rewriting_enabled else 'Can'} rewrite {rewrite_files_len} file(s) with "
            f"{len(suggestion_level_file_tuples)} change(s)."
        )
        time_message = f"Spotter took {scan_result.summary.scan_time:.3f} s to scan your input."
        counts_message = f"{parsing_result.included_files_count} file(s) scanned, {parsing_result.excluded_paths_count} path(s) skipped."

        stats_message = (
            f"It resulted in {scan_result.summary.num_errors} error(s), {scan_result.summary.num_warnings} "
            f"warning(s) and {scan_result.summary.num_hints} hint(s)."
        )
        overall_status_message = f"Overall status: {worst_level.name.upper()}"

        view_scan_url_message = ""
        scan_url = None
        if options.show_scan_url and scan_result.web_urls:
            scan_url = scan_result.web_urls.get("scan_url", None)
            view_scan_url_message = f"Visit {scan_url} to view this scan result."

        if options.show_colors:
            if parsing_error_label:
                parsing_error_label = f"{Style.BRIGHT}{parsing_error_label}{Style.NORMAL}"
            if fixed_check_results_label:
                fixed_check_results_label = f"{Style.BRIGHT}{fixed_check_results_label}{Style.NORMAL}"
            if check_results_label:
                check_results_label = f"{Style.BRIGHT}{check_results_label}{Style.NORMAL}"
            if scan_summary_label:
                scan_summary_label = f"{Style.BRIGHT}{scan_summary_label}{Style.NORMAL}"
            time_message = (
                f"Spotter took {Style.BRIGHT}{scan_result.summary.scan_time:.3f} s{Style.NORMAL} to scan your input."
            )
            counts_message = f"{Style.BRIGHT}{parsing_result.included_files_count} file(s){Style.NORMAL} scanned, {Style.BRIGHT}{parsing_result.excluded_paths_count} path(s){Style.NORMAL} skipped."
            stats_message = (
                f"It resulted in {Style.BRIGHT + Fore.RED}{scan_result.summary.num_errors} error(s)"
                f"{Fore.RESET + Style.NORMAL}, {Style.BRIGHT + Fore.YELLOW}{scan_result.summary.num_warnings} "
                f"warning(s){Fore.RESET + Style.NORMAL} and {Style.BRIGHT}{scan_result.summary.num_hints} "
                f"hint(s){Style.NORMAL}."
            )
            rewrite_message = (
                f"{'Did' if options.rewriting_enabled else 'Can'} {Style.BRIGHT + Fore.MAGENTA}rewrite{Fore.RESET + Style.NORMAL} "
                f"{Style.BRIGHT}{rewrite_files_len} file(s){Style.NORMAL} with "
                f"{Style.BRIGHT}{len(suggestion_level_file_tuples)} change(s){Style.NORMAL}."
            )

            if worst_level == DisplayLevel.ERROR:
                overall_status_message = (
                    f"Overall status: {Style.BRIGHT + Fore.RED}{worst_level.name.upper()}{Fore.RESET + Style.NORMAL}"
                )
            elif worst_level == DisplayLevel.WARNING:
                overall_status_message = (
                    f"Overall status: {Style.BRIGHT + Fore.YELLOW}{worst_level.name.upper()}{Fore.RESET + Style.NORMAL}"
                )
            elif worst_level == DisplayLevel.HINT:
                overall_status_message = f"Overall status: {Style.BRIGHT}{worst_level.name.upper()}{Style.NORMAL}"
            else:
                overall_status_message = (
                    f"Overall status: {Style.BRIGHT + Fore.GREEN}{worst_level.name.upper()}{Fore.RESET + Style.NORMAL}"
                )

            if scan_url:
                view_scan_url_message = f"Visit {Fore.CYAN}{scan_url}{Fore.RESET} to view this scan result."
        if parsing_errors:
            output += f"{parsing_error_label}:\n{parsing_errors}\n\n"
        if scan_result.fixed_check_results and scan_result.check_results:
            output += (
                f"{fixed_check_results_label}:\n{fixed_check_results}\n{check_results_label}:\n"
                f"{check_results}\n{scan_summary_label}:\n{time_message} {counts_message}\n{stats_message}\n"
                f"{rewrite_message}\n{overall_status_message}"
            )
        elif scan_result.fixed_check_results:
            output += (
                f"{fixed_check_results_label}:\n{fixed_check_results}\n{scan_summary_label}:\n{time_message} {counts_message}"
                f"\n{stats_message}\n{rewrite_message}\n{overall_status_message}"
            )
        elif scan_result.check_results:
            output += (
                f"{check_results_label}:\n{check_results}\n{scan_summary_label}:\n{time_message} {counts_message}\n"
                f"{stats_message}\n{rewrite_message}\n{overall_status_message}"
            )
        else:
            output += f"{scan_summary_label}:\n{time_message} {counts_message}\n{stats_message}\n{rewrite_message}\n{overall_status_message}"

        if view_scan_url_message:
            output += f"\n{view_scan_url_message}"

        return output
