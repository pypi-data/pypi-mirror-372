# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 6.1

The following features should not be supported in Splunk 6.1 or later.
"""
from typing import TYPE_CHECKING

import splunk_appinspect
from splunk_appinspect import App, check_routine
from splunk_appinspect.constants import Tags

if TYPE_CHECKING:
    from splunk_appinspect.reporter import Reporter


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.AST,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_for_datamodel_acceleration_endpoint_usage(app: "App", reporter: "Reporter") -> None:
    """Check that deprecated datamodel/acceleration is not used.
    https://docs.splunk.com/Documentation/Splunk/6.2.0/RESTREF/RESTknowledge
    """
    kws = ["services/datamodel/acceleration"]
    report_output = (
        "From Splunk 6.1, datamodel/acceleration endpoint is deprecated. "
        "And it might be removed entirely in a future release."
        "An applicable replacement is"
        " https://answers.splunk.com/answers/326499/how-can-i-programmatically-monitor-data-model-acce.html"
    )

    regex_file_types = [".js", ".html", ".xml", ".conf"]

    for matched_file, matched_lineno in check_routine.find_endpoint_usage(
        app=app, kws=kws, regex_file_types=regex_file_types
    ):
        reporter.fail(report_output, matched_file, matched_lineno)
