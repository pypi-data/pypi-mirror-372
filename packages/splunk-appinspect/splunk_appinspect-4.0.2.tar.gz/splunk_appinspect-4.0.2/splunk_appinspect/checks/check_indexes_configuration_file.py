# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Indexes.conf file standards

Ensure that the index configuration file located in the **/default** and **/local** folder is well-formed and valid. For more, see [indexes.conf](https://docs.splunk.com/Documentation/Splunk/latest/Admin/Indexesconf).
"""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any, Generator

from splunk_appinspect.check_messages import CheckMessage, FailMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import PYTHON_3_VERSIONS, PYTHON_LATEST_VERSION, Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy


report_display_order = 2
logger = logging.getLogger(__name__)

RE_INDEX_NAME = re.compile(r"\$SPLUNK_DB\/(?P<index_name>[$\w]+)\/(db|colddb|thaweddb)$")


CheckValidateDefaultIndexesNotModified = Check.disallowed_config_stanzas(
    conf_file="indexes",
    stanzas=[
        "_audit",
        "_internal",
        "_introspection",
        "_thefishbucket",
        "history",
        "main",
        "provider-family:hadoop",
        "splunklogger",
        "summary",
        "volume:_splunk_summaries",
    ],
    tags=(
        Tags.SPLUNK_APPINSPECT,
        Tags.CLOUD,
        Tags.PRIVATE_APP,
        Tags.PRIVATE_CLASSIC,
        Tags.PRIVATE_VICTORIA,
        Tags.MIGRATION_VICTORIA,
    ),
    check_name="check_validate_default_indexes_not_modified",
    check_description="Check that no default Splunk indexes are modified by the app.",
    message="The default Splunk index [{stanza}] was modified in {file_name}, "
    "which is not allowed in the Splunk Cloud. Please remove this stanza. ",
)


class CheckIndexesConfProperties(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_indexes_conf_properties",
                description="Check that indexes.conf only contains the required 'homePath', 'coldPath', and "
                "'thawedPath' properties or the optional 'frozenTimePeriodInSecs', 'disabled', "
                "'datatype' and 'repFactor' properties. All other properties are prohibited. Also, if 'repFactor' "
                "property exists, its value should be 'auto'.",
                depends_on_config=("indexes",),
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
        property_allow_list = ["homePath", "coldPath", "thawedPath"]
        property_optional_allow_list = [
            "frozenTimePeriodInSecs",
            "disabled",
            "datatype",
            "repFactor",
        ]
        for section in config["indexes"].sections():
            # check for all properties
            for option_name, option_value, option_lineno in section.items():
                # in allow list
                if option_name in property_allow_list:
                    pattern_dict = {
                        "homePath": "db",
                        "coldPath": "colddb",
                        "thawedPath": "thaweddb",
                    }
                    legal_path = f"$SPLUNK_DB/{section.name}/{pattern_dict[option_name]}"
                    actual_path = option_value
                    if legal_path != actual_path:
                        m = RE_INDEX_NAME.match(actual_path)
                        if m and m.group("index_name") == "$_index_name":
                            continue
                        yield FailMessage(
                            f"In stanza {section.name}, property {option_name}",
                            file_name=config["indexes"].get_relative_path(),
                            line_number=option_lineno,
                            remediation=f"should be {legal_path}, but is {actual_path}  ",
                        )
                # not in option_allow_list
                elif option_name not in property_optional_allow_list:
                    allowed_properties = ", ".join(property_allow_list + property_optional_allow_list)
                    yield FailMessage(
                        f"Illegal property {option_name} found in stanza {section.name}."
                        f" Only properties [{allowed_properties}] are allowed in",
                        file_name=config["indexes"].get_relative_path(),
                        line_number=option_lineno,
                    )

                # if repFactor exists and value is not auto
                elif option_name == "repFactor" and option_value != "auto":
                    yield FailMessage(
                        "repFactor is an optional property. If specified it should be set to 'auto' only.",
                        file_name=config["indexes"].get_relative_path(),
                        line_number=option_lineno,
                    )


class CheckColdToFrozenScriptHasValidPythonVersionProperty(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_coldToFrozenScript_has_valid_python_version_property",
                description="Check that all the coldToFrozenScript in `indexes.conf` are explicitly set "
                f"the python.version to one of: {', '.join(PYTHON_3_VERSIONS)} as required.",
                depends_on_config=("indexes",),
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
        for section in config["indexes"].sections():
            if section.has_option("coldToFrozenScript"):
                if (
                    not section.has_option("python.version")
                    or section.get_option("python.version").value != PYTHON_LATEST_VERSION
                    and section.get_option("python.version").value not in PYTHON_3_VERSIONS
                ):
                    yield FailMessage(
                        f"The python.version of coldToFrozenScript should be explicitly set to one of: {', '.join(PYTHON_3_VERSIONS)} as required.",
                        file_name=config["indexes"].get_relative_path(),
                        line_number=config["indexes"][section.name].get_line_number(),
                    )
                elif section.get_option("python.version").value == PYTHON_LATEST_VERSION:
                    yield WarningMessage(
                        f"The `python.version` of coldToFrozenScript is set to {PYTHON_LATEST_VERSION}."
                        f" Note that python.version={PYTHON_LATEST_VERSION} is not supported for Splunk <= 9.2.",
                        file_name=config["indexes"].get_relative_path(),
                        line_number=config["indexes"][section.name].get_line_number(),
                    )


class CheckLowerCasedIndexNames(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_lower_cased_index_names",
                description="Check that all index names consist only of lowercase characters,"
                " numbers, underscores and hyphens. They cannot begin with an underscore "
                " or hyphen, or contain the word 'kvstore'. If index names have any"
                " uppercase characters any attempts to edit the index in the UI"
                " will cause a duplicate index stanza creation which will cause many errors in Splunk.",
                depends_on_config=("indexes",),
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
        for section in config["indexes"].sections():
            if not re.match(r"^(?![_-]|.*kvstore)[a-z0-9_-]+$", section.name):
                yield FailMessage(
                    f"The index [{section.name}] contains either uppercase characters, starts"
                    " with an underscore or a hyphen, contains the word 'kvstore' or contains some"
                    " special characters which is not allowed. Please ensure index names contain only "
                    " lowercase characters, numbers, underscores and hyphens and do not start with an "
                    " underscore or hyphen, or contain the word 'kvstore'.",
                    file_name=config["indexes"].get_relative_path(),
                    line_number=config["indexes"][section.name].get_line_number(),
                )
