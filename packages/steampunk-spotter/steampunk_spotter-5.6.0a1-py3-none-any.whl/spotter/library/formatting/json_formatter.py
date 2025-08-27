import json

from spotter.library.formatting.models import OutputFormatOptions, OutputFormatter
from spotter.library.formatting.utils import format_scan_result_to_dict
from spotter.library.parsing.parsing import ParsingResult
from spotter.library.scanning.result import ScanResult


class JsonFormatter(OutputFormatter):
    def format(
        self,
        scan_result: ScanResult,
        parsing_result: ParsingResult,  # noqa: ARG002  # TODO: show parsing errors in this format too
        options: OutputFormatOptions,
    ) -> str:
        return (
            json.dumps(
                format_scan_result_to_dict(
                    scan_result, show_docs_url=options.show_docs_url, show_scan_url=options.show_scan_url
                ),
                indent=2,
            )
            + "\n"
        )  # ensure the final line is a proper (posix) line
