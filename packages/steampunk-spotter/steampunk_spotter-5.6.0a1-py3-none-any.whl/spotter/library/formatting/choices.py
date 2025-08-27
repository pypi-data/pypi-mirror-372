import sys
from enum import Enum
from typing import Type

from spotter.library.formatting.json_formatter import JsonFormatter
from spotter.library.formatting.junit_formatter import JUnitFormatter
from spotter.library.formatting.models import OutputFormatter
from spotter.library.formatting.sarif_formatter import SarifFormatter
from spotter.library.formatting.text_formatter import TextFormatter
from spotter.library.formatting.yaml_formatter import YamlFormatter


class OutputFormat(Enum):
    TEXT = (1, TextFormatter)
    JSON = (2, JsonFormatter)
    YAML = (3, YamlFormatter)
    JUNIT = (4, JUnitFormatter)
    SARIF = (5, SarifFormatter)

    def __init__(self, identifier: int, formatter_class: Type[OutputFormatter]):
        self.identifier = identifier
        self.formatter_class = formatter_class

    def __str__(self) -> str:
        return str(self.name.lower())

    @classmethod
    def from_string(cls, output_format: str) -> "OutputFormat":
        try:
            return cls[output_format.upper()]
        except KeyError:
            print(
                f"Error: nonexistent output format: {output_format}, "
                f"valid values are: {[str(e) for e in OutputFormat]}.",
                file=sys.stderr,
            )
            sys.exit(2)

    def formatter(self) -> OutputFormatter:
        return self.formatter_class()
