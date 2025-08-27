import json
from typing import TYPE_CHECKING, List, Optional, Union

from pydantic import BaseModel, Field
from pydantic_core import to_jsonable_python

from spotter.library.formatting.models import OutputFormatOptions, OutputFormatter
from spotter.library.parsing.parsing import ParsingResult
from spotter.library.scanning.display_level import DisplayLevel
from spotter.library.scanning.result import ScanResult
from spotter.library.utils import get_current_cli_version

if TYPE_CHECKING:
    from spotter.library.scanning.check_result import CheckResult


class SarifFormatter(OutputFormatter):
    """Render the SARIF (Static Analysis Results Interchange Format) report."""

    TOOL_NAME = "Steampunk Spotter"
    CATALOG_URL = "https://spotter.steampunk.si/check-catalogue/"
    INFORMATION_URI = "https://steampunk.si/spotter/"

    def format(
        self,
        scan_result: ScanResult,
        parsing_result: ParsingResult,  # noqa: ARG002  # TODO: show parsing errors in this format too
        options: OutputFormatOptions,
    ) -> str:
        if len(scan_result.check_results) == 0:
            return json.dumps(to_jsonable_python(SarifFile(), by_alias=True), indent=4)

        driver_rules = []
        results = []
        for cr in scan_result.check_results:
            location = self._create_location(cr)
            driver_rule = self._create_driver_rule(cr, options.show_docs_url)
            if driver_rule not in driver_rules:
                driver_rules.append(driver_rule)
            result = self._create_results(cr, location)
            if result not in results:
                results.append(result)
        tool = self._create_tool(driver_rules)
        return json.dumps(
            to_jsonable_python(SarifFile(runs=[Run(tool=tool, results=results)]), by_alias=True), indent=4
        )

    def _convert_level_error(self, spotter_error_lvl: DisplayLevel) -> str:
        """
        Convert the error level from the spotter to a standardized format.

        :param spotter_error_lvl: The error level from the spotter.
        :return: The standardized error level.
        """
        lvl = spotter_error_lvl.name.lower()
        if lvl == "hint":
            return "note"
        return lvl

    def _create_driver_rule(self, check_result: "CheckResult", show_docs_url: bool) -> "DriverRules":
        """
        Create a driver rule object based on the provided check result.

        :param check_result: The check result object.
        :return: The driver rule generated.
        """
        driver_help = DriverRulesHelp(text="")
        if show_docs_url and check_result.doc_url is not None:
            driver_help.text = check_result.doc_url
        return DriverRules(
            id=check_result.catalog_info.event_code,
            name=check_result.catalog_info.event_value,
            shortDescription=DriverRulesShortDescription(text=check_result.catalog_info.event_value),
            help=driver_help,
        )

    def _create_results(self, check_result: "CheckResult", location: Union["Location", None]) -> "SarifResult":
        """
        Create results object based on the provided check result and location.

        :param check_result: The check result object.
        :param location: The location of the check result, if available.
        :return: The generated result.
        """
        return SarifResult(
            ruleId=check_result.catalog_info.event_code,
            level=self._convert_level_error(check_result.level),
            message=Message(text=check_result.message),
            locations=[location],
        )

    def _create_location(self, check_result: "CheckResult") -> Union["Location", None]:
        """
        Create a location object based on the provided check result.

        :param check_result: The check result object.
        :return: The generated location, or None if metadata is not available.
        """
        if check_result.metadata:
            uri = check_result.metadata.file_name
            if uri.startswith("/"):  # sarif does not support leading slash in uri
                uri = uri[1:]

            return Location(
                physicalLocation=PhysicalLocation(
                    artifactLocation=ArtifactLocation(uri=uri),
                    region=Region(startLine=check_result.metadata.line, startColumn=check_result.metadata.column),
                )
            )
        return None

    def _create_tool(self, driver_rules: List["DriverRules"]) -> "Tool":
        """
        Create a tool object based on the provided driver rules.

        :param driver_rules: The list of driver rules.
        :return: The generated tool.
        """
        return Tool(
            driver=ToolDriver(
                name=self.TOOL_NAME,
                version=get_current_cli_version(),
                informationUri=self.INFORMATION_URI,
                rules=driver_rules,
            )
        )


class ArtifactLocation(BaseModel):
    uri: str


class Region(BaseModel):
    startLine: int
    startColumn: int


class PhysicalLocation(BaseModel):
    artifactLocation: ArtifactLocation
    region: Region


class Message(BaseModel):
    text: str


class Location(BaseModel):
    physicalLocation: Optional[PhysicalLocation] = None


class SarifResult(BaseModel):
    ruleId: str
    level: str
    message: Message
    locations: List[Location]


class DriverRulesHelp(BaseModel):
    text: str


class DriverRulesShortDescription(BaseModel):
    text: str


class DriverRules(BaseModel):
    id: str
    name: str
    shortDescription: DriverRulesShortDescription
    help: DriverRulesHelp


class ToolDriver(BaseModel):
    name: str
    version: str
    informationUri: str
    rules: List[DriverRules]


class Tool(BaseModel):
    driver: Optional[ToolDriver]


class Run(BaseModel):
    tool: Optional[Tool] = None
    results: Optional[List[SarifResult]] = []


class SarifFile(BaseModel):
    schema_url: str = Field(
        default="https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        alias="$schema",
    )
    version: str = "2.1.0"
    runs: Optional[List[Run]] = []
