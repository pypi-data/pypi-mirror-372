import itertools
import sys
import xml.etree.ElementTree as ET

from spotter.library.formatting.models import OutputFormatOptions, OutputFormatter
from spotter.library.formatting.utils import format_check_result
from spotter.library.parsing.parsing import ParsingResult
from spotter.library.scanning.check_result import CheckResult
from spotter.library.scanning.result import ScanResult


class JUnitFormatter(OutputFormatter):
    def format(
        self,
        scan_result: ScanResult,
        parsing_result: ParsingResult,  # noqa: ARG002  # TODO: show parsing errors in this format too
        options: OutputFormatOptions,
    ) -> str:
        root_node = self.add_root_node()

        def get_check_class(res: CheckResult) -> str:
            return res.catalog_info.check_class

        for c_class, c_results in itertools.groupby(
            sorted(scan_result.check_results, key=get_check_class), get_check_class
        ):
            test_suite = self.add_test_suite(root_node, c_class)
            check_count = 0

            for result in c_results:
                test_case = self.add_test_case(
                    test_suite,
                    f"{result.catalog_info.event_code}-{result.catalog_info.event_value}[{check_count}]",
                    c_class,
                )
                self.add_attribute(test_case, "id", str(result.catalog_info.event_code))
                self.add_attribute(test_case, "file", str(result.metadata.file_name if result.metadata else ""))
                self.add_failure_info(
                    test_case,
                    format_check_result(
                        result, show_colors=False, show_docs_url=options.show_docs_url, rewriting_enabled=False
                    ),
                    result.level.name.upper(),
                )

                check_count += 1

            self.add_attribute(test_suite, "tests", str(check_count))
            self.add_attribute(test_suite, "errors", str(check_count))

        if sys.version_info >= (3, 9):
            # ET.indent works only for Python >= 3.9
            ET.indent(root_node)

        return ET.tostring(root_node, encoding="unicode", method="xml")

    def add_root_node(self) -> ET.Element:
        root = ET.Element("testsuites")
        return root

    def add_test_suite(self, root_node: ET.Element, name: str) -> ET.Element:
        test_suite = ET.SubElement(root_node, "testsuite", name=name)
        return test_suite

    def add_test_case(self, test_suite: ET.Element, name: str, classname: str) -> ET.Element:
        test_case = ET.SubElement(test_suite, "testcase", name=name, classname=classname)
        return test_case

    def add_failure_info(self, test_case: ET.Element, message: str, typ: str) -> ET.Element:
        error_case = ET.SubElement(test_case, "error", message=message, type=typ)
        return error_case

    def add_attribute(self, element: ET.Element, key: str, value: str) -> None:
        element.set(key, value)
