"""
Splunk AppInspect JUnit report formatter
"""

# Written by Aplura, LLC
# Released under GPLv2

from builtins import str as text
from typing import TYPE_CHECKING, Optional

import lxml.etree as et
from lxml.etree import (  # noqa pylint: disable=no-name-in-module; noqa pylint: disable=no-name-in-module
    Element,
    SubElement,
)

import splunk_appinspect
from splunk_appinspect.formatters import validation_report_formatter

if TYPE_CHECKING:
    from splunk_appinspect.checks import Check, Group
    from splunk_appinspect.reporter import Reporter
    from splunk_appinspect.validation_report import ApplicationValidationReport, ValidationReport


class ValidationReportJUnitXMLFormatter(validation_report_formatter.ValidationReportFormatter):
    """Splunk AppInspect JUnit report formatter."""

    def format_testsuite_element(
        self, application_validation_report: "ApplicationValidationReport", max_messages: Optional[int] = None
    ) -> Element:
        """Format application report test suite elements"""
        summary = application_validation_report.get_summary()
        metrics = application_validation_report.metrics

        summary_failure = summary["failure"]
        summary_warning = summary["warning"]
        summary_error = summary["error"]
        summary_na = summary["not_applicable"]
        summary_skipped = summary["skipped"]
        summary_success = summary["success"]

        metrics_execution_time = metrics["execution_time"]
        metrics_start_time = metrics["start_time"].isoformat()

        testsuite_element_attributes = {
            "name": "Splunk AppInspect",
            "failures": f"{summary_failure}",
            "warnings": f"{summary_warning}",
            "errors": f"{summary_error}",
            "skipped": f"{summary_na + summary_skipped}",
            "tests": f"{summary_skipped + summary_na + summary_success + summary_failure + summary_error}",
            "time": f"{metrics_execution_time}",
            "timestamp": f"{metrics_start_time}",
        }
        testsuite_element = Element("testsuite", testsuite_element_attributes)
        testsuite_element.append(self.format_testsuite_properties(application_validation_report))

        for grouping in application_validation_report.groups():
            for group, check, reporter in grouping:
                testsuite_element.append(self.format_testcase_element(group, check, reporter, max_messages))
        return testsuite_element

    @staticmethod
    def format_testsuite_properties(application_validation_report: "ApplicationValidationReport") -> Element:
        """Format application report properties."""
        properties_element = Element("properties")

        app_name_property_attributes = {
            "name": "app_name",
            "value": application_validation_report.app_name,
        }

        _ = SubElement(properties_element, "property", app_name_property_attributes)

        included_tags_property_attributes = {
            "name": "included_tags",
            "value": ",".join(application_validation_report.run_parameters["included_tags"]),
        }

        _ = SubElement(properties_element, "property", included_tags_property_attributes)

        excluded_tags_property_attributes = {
            "name": "excluded_tags",
            "value": ",".join(application_validation_report.run_parameters["excluded_tags"]),
        }

        _ = SubElement(properties_element, "property", excluded_tags_property_attributes)

        return properties_element

    def format_testcase_element(
        self, group: "Group", check: "Check", reporter: "Reporter", max_messages: Optional[int] = None
    ) -> Element:
        """
        Args:
            group: the result's group object
            check: the result's check object
            reporter: the result's reporter object format.

        Returns:
            An XML element object representing the test case.

        """
        testcase_element_attributes = {
            "classname": group.name,
            "name": check.name,
            "time": text(reporter.metrics["execution_time"]),
        }
        testcase_element = Element("testcase", testcase_element_attributes)
        test_case_element_system_out = SubElement(testcase_element, "system-out")
        test_case_element_system_out.text = self._sanitize(check.doc())
        result_element = self.format_testcase_result_element(group, check, reporter, max_messages)
        if result_element is not None:
            testcase_element.append(result_element)

        return testcase_element

    def format_testcase_result_element(
        self, group: "Group", check: "Check", reporter: "Reporter", max_messages: Optional[int] = None
    ) -> Optional[Element]:
        """
        Args:
            group: the result's group object.
            check: the result's check object.
            reporter: the result's reporter object format.

        Returns:
             None if no failures detected. Otherwise, it returns the respective result required by JUnit.

        """
        if max_messages is None:
            max_messages = splunk_appinspect.main.MAX_MESSAGES_DEFAULT

        # JUnit/Bamboo only use skipped/failure/success/errors as options, so
        # they are combined below
        result = reporter.state()
        result_element_to_return = None
        result_combined_messages = {"files": [], "messages": []}
        if result in ("skipped", "not_applicable"):
            result_element_to_return = Element("skipped")
        else:
            report_records = reporter.report_records(max_records=max_messages)
            result_combined_messages["filename"] = report_records[0].filename if report_records else "N/A"
            result_combined_messages["messages"] = map(lambda rd: rd.message, report_records)
        if result == "failure":
            result_element_to_return = Element("failure", {"message": result_combined_messages["filename"]})
            result_element_to_return.text = self._sanitize(", ".join(result_combined_messages["messages"]))
        if result == "error":
            result_element_to_return = Element("error", {"message": result_combined_messages["filename"]})
            result_element_to_return.text = self._sanitize(", ".join(result_combined_messages["messages"]))
        if result == "warning":
            result_element_to_return = Element(
                "success", {"type": "WARNING", "message": result_combined_messages["filename"]}
            )
            result_element_to_return.text = self._sanitize(", ".join(result_combined_messages["messages"]))

        return result_element_to_return

    def format_application_validation_report(
        self, application_validation_report: "ApplicationValidationReport", max_messages: Optional[int] = None
    ):
        """Returns JUnitXML testsuite element."""
        if max_messages is None:
            max_messages = splunk_appinspect.main.MAX_MESSAGES_DEFAULT
        return self.format_testsuite_element(application_validation_report, max_messages)

    def format_application_validation_reports(
        self, validation_report: "ValidationReport", max_messages: Optional[int] = None
    ) -> Element:
        """Returns JUnitXML top-level testsuites element."""
        root_element = Element("testsuites")
        for application_validation_report in validation_report.application_validation_reports:
            root_element.append(self.format_application_validation_report(application_validation_report, max_messages))

        return root_element

    @staticmethod
    def _sanitize(string: str) -> str:
        return string.replace("\x0c", "")

    def format(
        self, validation_report: "ValidationReport", max_messages: Optional[int] = None
    ) -> str:  # pylint: disable=W0221
        root_element = self.format_application_validation_reports(validation_report, max_messages)
        return et.tostring(root_element, encoding="UTF-8", xml_declaration=True, pretty_print=True).decode(
            "utf-8", "ignore"
        )
