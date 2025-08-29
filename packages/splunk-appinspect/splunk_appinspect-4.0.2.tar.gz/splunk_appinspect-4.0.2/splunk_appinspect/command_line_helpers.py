"""Command-line helpers in order to help with command-line presentation."""

from __future__ import annotations

import collections
from typing import TYPE_CHECKING, Optional

import click
import painter

import splunk_appinspect
from splunk_appinspect.common.string_utils import print_ascii

if TYPE_CHECKING:
    from splunk_appinspect.validation_report import ApplicationValidationReport


result_colors = collections.defaultdict(
    dict,
    {
        "error": {"bg": "red", "fg": "white"},
        "failure": {"fg": "red", "bg": "black"},
        "success": {"fg": "green"},
        "not_applicable": {"fg": "blue"},
        "warning": {"fg": "black", "bg": "yellow"},
    },
)


glyphs = {
    "error": " E ",
    "failure": " F ",
    "skipped": " S ",
    "warning": " W ",
    "success": " P ",
    "not_applicable": "N/A",
}


def output_summary(summary: dict[str, int], summary_header: Optional[str] = None) -> None:
    """
    Prints a summary of checks executed during a Splunk AppInspect run.

    Args:
        summary: A dictionary of key representing the check result states possible and the values being the aggregate
            counts of results.
        summary_header: A string that can be the alternative header denoting the summary results.

    """
    if summary_header is None:
        click.echo("Summary:\n")
    else:
        click.echo(f"{summary_header}:\n")

    total = 0
    for key, value in iter(summary.items()):
        total = total + value
        click.echo(click.style(f"{key:>14}: {str(value):>2}", **result_colors[key]))
    click.echo("-" * 19)
    total_str = "Total"
    click.echo(f"{total_str:>14}: {str(total):>2}")

    click.echo()


def print_result_records(
    application_validation_report: "ApplicationValidationReport",
    max_messages: Optional[int] = None,
    result_types: Optional[list[str]] = None,
    message_types: Optional[list[str]] = None,
) -> None:
    """
    Args:
        application_validation_report: An application validation report that should have completed.
        max_messages: the maximum number of messages to return for a single check.
        result_types: A list of result types of what to print.
        message_types: A list of message types of what to print.

    """
    if result_types is None:
        result_types = splunk_appinspect.reporter.STATUS_TYPES
    if message_types is None:
        message_types = splunk_appinspect.reporter.STATUS_TYPES
    if max_messages is None:
        max_messages = splunk_appinspect.main.MAX_MESSAGES_DEFAULT
    if max_messages == splunk_appinspect.main.MAX_MESSAGES_DEFAULT:
        click.echo(f"A default value of {str(max_messages)} for max-messages will be used.")

    for grouping in application_validation_report.groups():
        checks_with_errors = [
            (group, check, reporter) for group, check, reporter in grouping if reporter.state() in result_types
        ]
        if checks_with_errors:
            print_group_documentation = True
            for group, check, reporter in checks_with_errors:
                if print_group_documentation:
                    formatted_group_documentation = format_cli_string(group.doc(), left_padding=0)
                    click.echo(painter.paint.green(formatted_group_documentation))
                    print_group_documentation = False

                formatted_check_documentation = format_cli_string(check.doc(), left_padding=4)
                click.echo(formatted_check_documentation)
                for report_record in reporter.report_records(max_records=max_messages):
                    if report_record.result in message_types:
                        format_string = format_cli_string(report_record.message, left_padding=12).lstrip()

                        fmt = result_colors[report_record.result]
                        result_message = f"        {report_record.result.upper()}: {format_string}"
                        # click (and terminals in general) has bad support for unicode,
                        # so it's easier to filter the printed characters
                        click.secho(print_ascii(result_message), **fmt)


def format_cli_string(string_to_format: str, left_padding: int = 4, column_wrap: int = 80) -> str:
    """
    Takes in a string and then formats it to support padding and column wrapping for prettier output.

    Args:
      string_to_format: An unformatted string.
      left_padding: The amount of left padding applied to each new line.
      column_wrap: The string length at which a newline is determined.

    """
    allowed_line_length = column_wrap - left_padding
    new_string = ""
    new_string += " " * left_padding  # Gotta pad that first line
    split_strings = string_to_format.split()
    current_index = len(new_string)

    for split_string in split_strings:
        current_word_length = len(split_string)
        new_index = current_index + current_word_length + 1  # The plus 1 is for the space that is added at the end
        # The line is over the column wrap, add a new line and then the word
        if new_index > allowed_line_length:
            new_string += "\n" + (" " * left_padding)
            new_string += split_string
            new_index = current_word_length
        # Just add the word
        else:
            new_string += split_string

        new_string += " "
        current_index = new_index

    return new_string
