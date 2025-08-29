# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 8.0

The following features should not be supported in Splunk 8.0.0 or later. For more, see [Deprecated features](https://docs.splunk.com/Documentation/Splunk/8.0.0/ReleaseNotes/Deprecatedfeatures) and [Changes for Splunk App developers](https://docs.splunk.com/Documentation/Splunk/8.0.0/Installation/ChangesforSplunkappdevelopers).
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

from semver import VersionInfo

import splunk_appinspect
import splunk_appinspect.check_routine as check_routine
from splunk_appinspect.canary_modules import modules as canary_modules
from splunk_appinspect.check_messages import CheckMessage, FailMessage, WarningMessage
from splunk_appinspect.check_routine import util
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags
from splunk_appinspect.sideview_utils_modules import modules as sideview_modules

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy
    from splunk_appinspect.custom_types import FileViewType
    from splunk_appinspect.reporter import Reporter


logger = logging.getLogger(__name__)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.AST,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_removed_m2crypto_usage(app: "App", reporter: "Reporter"):
    """
    Check for the existence of the M2Crypto package usage, which is removed in the Splunk Enterprise 8.0.
    """
    # This package was removed in Splunk Enterprise 8.0 release and App shouldn't use it.
    # However, Since we don't know whether the user has packaged their own M2Crypto. We
    # only report warning once the usage is found.
    reporter_output = (
        "Remove dependencies on the M2Crypto package. This package was removed in the Splunk Enterprise 8.0."
    )
    client = app.python_analyzer_client
    for file_path, ast_info in client.get_all_ast_infos():
        lines = ast_info.get_module_usage("M2Crypto", lineno_only=True)
        for line in lines:
            reporter.fail(reporter_output, file_path, line)


class CheckForCherryPyCustomControllerWebConfEndpoints(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_cherry_py_custom_controller_web_conf_endpoints",
                description="Check for the existence of custom CherryPy endpoints, which must be upgraded to"
                "be Python 3-compatible for the Splunk Enterprise 8.0.",
                depends_on_config=("web",),
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_CLASSIC,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                ),
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        reporter_output_a = (
            "Update custom CherryPy endpoints to be Python 3-compatible"
            " for the Splunk Enterprise 8.0. Splunk Web, which CherryPy"
            " endpoints depend on, will support only Python 3.7."
            " If you've finished your update, please disregard this message."
        )
        reporter_output_b = (
            "CherryPy endpoints are defined in web.conf but no controller file found."
            " Please provide controller file under appserver/controllers as <py_module_name>.py"
            " and make sure it's Python 3-compatible for the Splunk Enterprise 8.0."
            " Splunk Web, which CherryPy endpoints depend on, will support only Python 3.7."
            " If you've finished your update, please disregard this message."
        )
        for section in config["web"].sections():
            if section.name.startswith("endpoint:"):
                python_module_name = re.search(r"endpoint:(\w+)", section.name).group(1)
                file_path = Path("appserver", "controllers", f"{python_module_name}.py")
                if app.file_exists(file_path):
                    reporter_output = reporter_output_a
                else:
                    file_path = config["web"].get_relative_path()
                    reporter_output = reporter_output_b

                yield WarningMessage(reporter_output, file_name=file_path)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_existence_of_python_code_block_in_mako_template(app: "App", reporter: "Reporter"):
    """
    Check for the existence of Python code block in Mako templates, which must be upgraded
    to be Python 3-compatible for the Splunk Enterprise 8.0.
    """
    reporter_output = (
        "Update Mako templates to be Python 3-compatible."
        " Splunk Web, which Mako templates depend on, will support only Python 3.7."
        " If you've finished your update, please disregard this message."
    )
    for directory, filename, _ in app.iterate_files(types=[".html"]):
        current_file_relative_path = Path(directory, filename)
        current_file_full_path = app.get_filename(directory, filename)
        if check_routine.is_mako_template(current_file_full_path):
            reporter.warn(reporter_output, current_file_relative_path)


class CheckForAdvancedXmlModuleElements(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_for_advanced_xml_module_elements",
                description="Check that there is no Advanced XML, which was deprecated in Splunk Enterprise 6.3.",
                depends_on_data=(Path("ui", "views"),),
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                ),
            )
        )

    def check_data(self, app: "App", file_view: "FileViewType") -> Generator[CheckMessage, Any, None]:
        for relative_path, full_path in file_view.get_filepaths_of_files(basedir="ui/views", types=[".xml"]):
            findings = util.find_xml_nodes_usages([(relative_path, full_path)], [check_routine.xml_node("module")])
            if len(findings) == 0:
                # no <module> nodes in this view xml, move on
                continue
            found_sideview = False
            for node, _ in findings:
                name_attr = None
                if node.has_attr("name"):
                    name_attr = node.attrs.get("name")
                if name_attr in canary_modules or name_attr in sideview_modules:
                    found_sideview = True
                    break
            if not found_sideview:
                # If no Sideview or Canary modules detected, this is Advanced XML
                yield FailMessage(
                    "`<module>` tag was found, indicating an Advanced XML view. Advanced XML was deprecated "
                    "in Splunk 6.3 and removed in Splunk 8.0.",
                    file_name=relative_path,
                    remediation="Replace Advanced XML with Simple XML",
                )


def app_conf_contain_stanza(app: "App", stanza_name: str) -> object:
    """Helper function to check app conf stanza"""

    class Floater:
        """Helper class to check app conf stanza"""

        @staticmethod
        def with_option(option_name):
            """Helper method to check app conf option"""
            for dir_name in ["local", "default"]:
                # Put local ahead of default as config of app.conf in local
                # would preempt those in default.
                value = app._get_app_info(stanza_name, option_name, dir_name)  # pylint: disable=W0212
                if value.startswith("[MISSING"):
                    continue
                return True
            return False

    return Floater()


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_python_script_existence(app: "App", reporter: "Reporter"):
    """
    Check for the existence of Python scripts, which must be upgraded to be cross-compatible
    with Python 2 and 3 for Splunk Enterprise 8.0.
    """
    count = 0
    for _, _, _ in app.iterate_files(types=[".py", ".py3", ".pyc", ".pyo", ".pyi", ".pyd", ".pyw", ".pyx", ".pxd"]):
        count += 1
    report_output = (
        f"{count} Python files found."
        " Update these Python scripts to be cross-compatible with Python 2 and 3 for Splunk Enterprise 8.0."
        " See https://docs.splunk.com/Documentation/Splunk/latest/Python3Migration/AboutMigration for more information."
        " If you've finished your update, please disregard this message."
    )
    if count > 0:
        reporter.warn(report_output)
