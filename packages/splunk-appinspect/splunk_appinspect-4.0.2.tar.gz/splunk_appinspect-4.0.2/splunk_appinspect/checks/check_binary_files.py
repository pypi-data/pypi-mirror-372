"""
### Binary file standards
"""

from __future__ import annotations

# Copyright 2021 Splunk Inc. All rights reserved.
import logging
import platform
from collections import ChainMap
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator

import magic

from splunk_appinspect.check_messages import CheckMessage, FailMessage, NotApplicableMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import Tags
from splunk_appinspect.python_analyzer import utilities
from splunk_appinspect.python_analyzer.ast_analyzer import AstAnalyzer

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy

logger = logging.getLogger(__name__)


def _check_binary_status(file_path: str) -> dict[str, bool | str | None]:
    binary_status = {
        "python": False,
        "text": False,
        "binary": False,
        "x86_64": False,
        "arm": False,
    }
    mimetype = magic.from_file(str(file_path), mime=True)
    if "text" in mimetype:
        binary_status["text"] = True
        if file_path.suffix == ".py":
            binary_status["python"] = True

    if "python" in mimetype:
        binary_status["python"] = True

    if mimetype == "application/x-executable" or mimetype == "application/x-sharedlib":
        binary_status["binary"] = True

        human_readable_output = magic.from_file(str(file_path))
        if "x86-64" in human_readable_output.lower():
            binary_status["x86_64"] = True
        if "arm" in human_readable_output.lower():
            binary_status["arm"] = True

    return binary_status


def _traverse_all_imported_python_files(file_full_path: Path) -> tuple[set[Path], ChainMap[Path, str]]:
    all_imported_python_file = set()
    invalid_files = ChainMap()

    def __traverse_all_imported_python_files(file_full_path: Path) -> None:
        if file_full_path in all_imported_python_file:
            return
        all_imported_python_file.add(file_full_path)

        try:
            imported_files = utilities.find_imports(file_full_path)
        except (SyntaxError, TabError) as ex:
            invalid_files[file_full_path] = str(ex)
            return

        if any([imports[3] is None for imports in imported_files if len(imports) > 3]):
            invalid_files[file_full_path] = "Unable to locate all imported modules"
            return

        for imports in imported_files:
            try:
                file_path = imports[3]
            except IndexError:
                continue
            if file_path not in all_imported_python_file:
                __traverse_all_imported_python_files(file_path)

    __traverse_all_imported_python_files(file_full_path)

    return all_imported_python_file, invalid_files


class CheckIdxBinaryCompatibility(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_idx_binary_compatibility",
                description="Checks that binaries that are distributed to the IDX tier of "
                "a distributed Splunk platform deployment are compatible with aarch64.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.CLOUD,
                    Tags.PRIVATE_APP,
                    Tags.PRIVATE_VICTORIA,
                    Tags.MIGRATION_VICTORIA,
                    Tags.PRIVATE_CLASSIC,
                ),
                # Note: this check uses distsearch.conf but if
                # neither commands.conf nor transforms.conf is present
                # then this check should be not-applicable (there are no
                # binaries to check), thus "distsearch" was not included here
                depends_on_config=("commands", "transforms"),
            )
        )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        if platform.system() == "Windows":
            yield WarningMessage(
                "Please run AppInspect using another OS to enable this check. Or use AppInspect API. ",
            )
            return

        allowlist_hash_files = (
            # Splunklib external_search_command.py
            "047eff10d2f10452b850579e886bbb919a53a77d3c34537c99193b24a8abab73",
            "0a2c2e0a72bb85b1ca9916147bf69a706355f2f7bea2ff3ff5cea796b982c2e8",
            "22f651c1bc32e8f9a75290fdb815200972d17ebd12ed0b3bb9638628b10bf849",
            "24da27069eac27d5979dc8b564116060a7beafadd55519a26e0cd747ddd0edbf",
            "268297fa7375241623e3775ba33326752acacafb3abd976eb160bd688699c671",
            "48fa70a0ddd89af6a78dbd47f798500cbc224e8712292bccf77e8f023cbe58a2",
            "623fd10c4f61fc3b9112d31284e8ab5741007baa427abaf7e7bf4093fd0eb8eb",
            "6f79090c85c810a294bc642d5072d320d11dbc2c40eed6957869c0f183427839",
            "992d81bb729f43252ab07235c7bb13713295cee4da17c1afae3336cc8c285ed4",
            "9a5fbfe2a301671fccd0e62209ebc076945904b1bf8a1ee94d1b261256e7d9ad",
            "a8c3e417dc80eb96b132d8a571b81726a6b06c7b9bad62d13b97ae483eb85853",
            "b0e75e31669ba763a6545775940d2b54aea138340fc659a9c179cd48e4fa2320",
            "b48636726d2234720be6f16c000ae8b04bd3c2021f121256adf03a788f5664fd",
            "bdc90bae58b1c93f953f5001ccebec73c528ac3cb68e2c4861cd483d4b89667b",
            "edef82986765acf5e3491f537b6388385ccd6bdf30140e220275a0b8b7554fe4",
        )

        executable_files = []
        if "commands" in config:
            executable_files.extend(app.get_custom_executable_files(config, False))

        if "transforms" in config:
            executable_files.extend(app.get_transforms_executable_files(config))

        if "distsearch" in config:
            executable_files = list(set(executable_files) - set(app.get_non_distributed_files(config)))

        # List all imports python file. Warn if it's not a python file and not an arm binary
        all_imported_python_file = set()
        invalid_files = ChainMap()

        for executable_file in set(executable_files):
            file_full_path = app.get_filename(executable_file)
            binary_status = _check_binary_status(file_full_path)
            if binary_status["python"]:
                (
                    traversed_imported_files,
                    traversed_invalid_files,
                ) = _traverse_all_imported_python_files(file_full_path)
                all_imported_python_file = all_imported_python_file | traversed_imported_files
                invalid_files.update(traversed_invalid_files)
            elif binary_status["binary"] and not binary_status["arm"]:
                yield FailMessage(
                    "The following file is incompatible with the ARM aarch64 architecture. "
                    "Compatibility with this architecture is required for code that will be executed "
                    "on the Indexer tier of the Splunk Cloud Platform.",
                    file_name=executable_file,
                )
        for file, error in invalid_files.items():
            all_imported_python_file.remove(file)

            yield WarningMessage(
                f"AppInspect is unable to validate whether the following files are compatible with execution "
                f"on the ARM aarch64 platform because they do not appear to be compatible with Python 3. "
                f"This may cause issues when your app is run on the Splunk Cloud Platform. Error: {error}",
                file_name=file,
            )

        def check_report_binary_file_in_code(ast_node, file_name):
            if hasattr(ast_node, "elts") and ast_node.elts and hasattr(ast_node.elts[0], "s") and ast_node.elts[0].s:
                # ex) ast_node.elts = ["test.py", "option1", "option2"] => "test.py"
                inspect_file_name = Path("bin", ast_node.elts[0].s)
            elif hasattr(ast_node, "s") and ast_node.s:
                # ex) ast_node.s = "test.py option1 option2" => "test.py"
                inspect_file_name = Path("bin", ast_node.s.strip().split(" ")[0])
            else:
                yield WarningMessage(
                    "Code has been found that may have executed the binary file.",
                    file_name=file_name,
                    line_number=ast_node.lineno,
                )
                return

            if app.file_exists(inspect_file_name):
                binary_status = _check_binary_status(app.get_filename(inspect_file_name))
                if binary_status["binary"] and not binary_status["arm"]:
                    # Change from warning to fail 3 months after deploying
                    yield FailMessage(
                        "The following file is incompatible with the ARM aarch64 architecture. "
                        "Compatibility with this architecture is required for code that will be executed "
                        "on the Indexer tier of the Splunk Cloud Platform.",
                        file_name=file_name,
                        line_number=ast_node.lineno,
                    )
            else:
                yield WarningMessage(
                    f"It looks like {file_name} tries to run {inspect_file_name} which may be a binary file, "
                    f"but {inspect_file_name} does not exist.",
                    file_name=file_name,
                    line_number=ast_node.lineno,
                )

        # Determine if the script imports .so files or running by subprocess.
        # Warn if the binary file is not an arm binary
        for python_path in all_imported_python_file:
            try:
                analyzer = AstAnalyzer(python_file_path=python_path)
            except Exception as ex:
                yield WarningMessage(
                    f"AppInspect is unable to validate whether the following files are compatible with execution "
                    f"on the ARM aarch64 platform because they do not appear to be compatible with Python 3. "
                    f"This may cause issues when your app is run on the Splunk Cloud Platform. Error: {ex}",
                    file_name=python_path,
                )
                continue

            if analyzer.content_hash in allowlist_hash_files:
                continue

            if analyzer.get_module_usage("ctypes"):
                for name, ctypes_usages in analyzer.function_call_usage.items():
                    if name == "CDLL" or name == "LoadLibrary":
                        for ctypes_usage in ctypes_usages:
                            if hasattr(ctypes_usage, "args") and ctypes_usage.args:
                                yield from check_report_binary_file_in_code(ctypes_usage.args[0], python_path)

            if analyzer.get_module_usage("subprocess"):
                subprocess_usages = set(analyzer.get_module_function_call_usage("subprocess", fuzzy=True))
                for subprocess_usage in subprocess_usages:
                    if hasattr(subprocess_usage, "args") and subprocess_usage.args:
                        yield from check_report_binary_file_in_code(subprocess_usage.args[0], python_path)


class CheckArch64Compatibility(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_aarch64_compatibility",
                description="Check that every binary file is compatible with AArch64.",
                tags=(
                    Tags.SPLUNK_APPINSPECT,
                    Tags.AARCH_64,
                ),
            )
        )

    def check(self, app: "App") -> Generator[CheckMessage, Any, None]:
        if platform.system() == "Windows":
            yield WarningMessage(
                "Please run AppInspect using another OS to enable this check. Or use AppInspect API.",
            )
            return
        for directory, filename, _ in app.iterate_files():
            file_path = Path(directory, filename)
            file_full_path = app.get_filename(file_path)
            binary_status = _check_binary_status(file_full_path)
            if binary_status["binary"] and not binary_status["arm"]:
                yield FailMessage(
                    "Found AArch64-incompatible binary file. "
                    f"Remove or rebuild the file to be AArch64-compatible. File: {file_path}",
                    file_name=file_path,
                )


class CheckRequiresAdobeFlash(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_requires_adobe_flash",
                description="Check that the app does not use Adobe Flash files.",
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

    def check(self, app: "App") -> Generator[CheckMessage, Any, None]:
        flash_file_types = [
            ".f4v",
            ".fla",
            ".flv",
            ".jsfl",
            ".swc",
            ".swf",
            ".swt",
            ".swz",
            ".xfl",
        ]
        flash_files = [Path(f[0], f[1]) for f in app.iterate_files(types=flash_file_types)]
        has_flash_files = False
        for directory, filename, _ in app.iterate_files(excluded_types=flash_file_types):
            file_path = Path(directory, filename)
            file_full_path = app.get_filename(file_path)
            mime_type_str = magic.from_file(str(file_full_path))
            if "Macromedia Flash" in mime_type_str:
                has_flash_files = True
                yield FailMessage(
                    message="Flash file was detected.", remediation="Please remove the file.", file_name=file_path
                )

        if len(flash_files) > 0:
            for flash_file in flash_files:
                yield FailMessage(
                    message="Flash file was detected.", remediation="Please remove the file.", file_name=flash_file
                )
        if not has_flash_files and len(flash_files) == 0:
            yield NotApplicableMessage("Didn't find any flash files.")
