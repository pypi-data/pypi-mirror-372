# Copyright 2019 Splunk Inc. All rights reserved.
"""The configuration parsing logic for Splunk .conf files."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, BinaryIO, Callable, Generator, Optional

import chardet

if TYPE_CHECKING:
    from splunk_appinspect.custom_types import ConfigurationFileType


class InvalidSectionError(Exception):
    """Exception raised when an invalid section is found."""

    def __init__(self, message="", file_name: Optional[str] = None, line_no: Optional[int] = None) -> None:
        super().__init__(message)
        self.file_name: Optional[str] = file_name
        self.line_no: Optional[int] = line_no


def join_lines(iterator: BinaryIO | list[str]) -> Generator[tuple[str, int, Optional[str]], Any, None]:
    currentLine = ""
    lineno = 0
    # the new lines and carriage returns are stripped for iterators, otherwise
    # the regex will be flagged and the confparse will fail
    error = None

    # ACD-1714, Sometimes the customer's file is not standard UTF-8 encoded file (e.g. UTF-8-SIG).
    # For compatibility, just check if the object is readable, though Splunk only expects ascii/UTF-8.
    # See: https://docs.splunk.com/Documentation/Splunk/latest/Admin/Howtoeditaconfigurationfile
    if hasattr(iterator, "read"):
        encoding = chardet.detect(iterator.read(32))["encoding"]
        if encoding == "ascii":
            encoding = "UTF-8"

        iterator.seek(0)
        iterator = (line.decode(encoding, errors="ignore") for line in iterator)

    for line in (line.rstrip("\r\n") for line in iterator):
        lineno += 1
        if re.search("\\\\\\s*$", line):
            if line != line.rstrip():
                error = "Continuation with trailing whitespace"
            newline = line[:-1] + "\n"
            currentLine += newline
        else:
            yield (currentLine + line, lineno, error)
            error = None  # Reset on each yield
            currentLine = ""


def configuration_lexer(
    iterator: BinaryIO | list[str],
) -> Generator[tuple[str, str | tuple[str, str], int, Optional[str]], Any, None]:
    try:
        for item, lineno, error in join_lines(iterator):
            if item == "" or item.isspace():
                yield ("WHITESPACE", "", lineno, error)
            elif re.match(r"^\s*[#;]", item):
                yield ("COMMENT", item.lstrip(), lineno, error)
            elif re.match(r"^\s*\[", item):
                start = item.index("[")
                end = item.rindex("]", start)
                yield ("STANZA", item[start + 1 : end], lineno, error)
            elif re.match(r"^\s*\S*\s*=", item):
                key, value = item.split("=", 1)
                yield ("KEYVAL", (key.strip(), value.strip()), lineno, error)
            else:
                yield ("RANDSTRING", item, lineno, error)
    except ValueError:
        raise InvalidSectionError(f"Invalid item: {item}", line_no=lineno)
    except Exception:
        # re-raise other errors, it might be code error that need to further investigation
        raise


def specification_lexer(
    iterator: BinaryIO | list[str],
) -> Generator[tuple[str, str | tuple[str, str], int, Optional[str]], Any, None]:
    try:
        for item, lineno, error in join_lines(iterator):
            if item == "" or item.isspace():
                yield ("WHITESPACE", "", lineno, error)
            elif re.match(r"^\s*[#;*]", item):
                yield ("COMMENT", item.lstrip(), lineno, error)
            elif re.match(r"^\[", item):
                start = item.index("[")
                end = item.rindex("]", start)
                yield ("STANZA", item[start + 1 : end], lineno, error)
            elif re.match(r"^\s*\S*\s*=", item):
                key, value = item.split("=", 1)
                yield ("KEYVAL", (key.strip(), value.strip()), lineno, error)
            else:
                yield ("RANDSTRING", item, lineno, error)
    except ValueError:
        raise InvalidSectionError(f"Invalid item: {item}", line_no=lineno)
    except Exception:
        # re-raise other errors, it might be code error that need to further investigation
        raise


def parse(
    iterator_or_string: BinaryIO | list[str] | str,
    configuration_file: "ConfigurationFileType",
    lexer: Callable[[BinaryIO | list[str]], Generator[tuple[str, str, int, Optional[str]], Any, None]],
) -> "ConfigurationFileType":
    if isinstance(iterator_or_string, str):
        return parse(iterator_or_string.split("\n"), configuration_file, lexer)

    headers = []
    current_section = None

    for type, item, lineno, error in lexer(iterator_or_string):
        if type in ["WHITESPACE", "COMMENT", "RANDSTRING"]:
            # Not propagating errors on comments.
            headers.append(item)
        if type in ["STANZA", "KEYVAL"] and current_section is None:
            configuration_file.set_main_headers(headers)
            headers = []
        if type == "STANZA":
            if configuration_file.has_section(item):
                configuration_file.add_error("Duplicate stanza", lineno, item)
            current_section = configuration_file.add_section(item, header=headers, lineno=lineno)
            if error:
                configuration_file.add_error(error, lineno, item)
            headers = []
        if type == "KEYVAL":
            if not current_section:
                current_section = configuration_file.add_section("default", header=headers, lineno=lineno)
            if error:
                configuration_file.add_error(error, lineno, current_section.name)

            if current_section.has_option(item[0]):
                error_message = f"Repeat item name '{item[0]}'"
                configuration_file.add_error(error_message, lineno, current_section.name)

            current_section.add_option(item[0], item[1], header=headers, lineno=lineno)
            headers = []

    return configuration_file
