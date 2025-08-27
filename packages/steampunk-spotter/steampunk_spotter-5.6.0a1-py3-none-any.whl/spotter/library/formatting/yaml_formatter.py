from io import StringIO

import ruamel.yaml as ruamel

from spotter.library.formatting.models import OutputFormatOptions, OutputFormatter
from spotter.library.formatting.utils import format_scan_result_to_dict
from spotter.library.parsing.parsing import ParsingResult
from spotter.library.scanning.result import ScanResult


class YamlFormatter(OutputFormatter):
    def format(
        self,
        scan_result: ScanResult,
        parsing_result: ParsingResult,  # noqa: ARG002  # TODO: show parsing errors in this format too
        options: OutputFormatOptions,
    ) -> str:
        stream = StringIO()
        yaml = ruamel.YAML(typ="rt")
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(
            format_scan_result_to_dict(
                scan_result, show_docs_url=options.show_docs_url, show_scan_url=options.show_scan_url
            ),
            stream=stream,
        )
        return stream.getvalue()
