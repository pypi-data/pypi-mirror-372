# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Splunk app packaging standards

These checks validate that a Splunk app has been correctly packaged, and can be provided safely for package validation.
"""
import gzip
import io
import json
import logging
import os
import stat
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, Iterable, Tuple

import semver
from packaging_legacy import version

import splunk_appinspect
from splunk_appinspect.app_configuration_file import _is_check_app_config_file
from splunk_appinspect.app_package_handler import TarAppPackage
from splunk_appinspect.app_util import AppVersionNumberMatcher
from splunk_appinspect.check_messages import CheckMessage, FailMessage, SkipMessage, WarningMessage
from splunk_appinspect.checks import Check, CheckConfig
from splunk_appinspect.constants import SPLUNK_PACKAGING_DOC_URL, Tags

if TYPE_CHECKING:
    from splunk_appinspect import App
    from splunk_appinspect.configuration_file import ConfigurationProxy
    from splunk_appinspect.reporter import Reporter

report_display_order = 1
logger = logging.getLogger(__name__)


def app_package_extractable(check: Callable) -> Callable:
    """Decorator to pre-check if package is extractable."""

    @wraps(check)
    def wrap(app: "App", reporter: "Reporter") -> None:
        if app.package.is_origin_artifact_valid_compressed_file():
            check(app, reporter)
        else:
            reporter_output = (
                "Splunk App package is not a valid compressed file and cannot be extracted."
                f" Origin artifact name: {app.package.origin_artifact_name}"
            )
            reporter.fail(reporter_output)

    return wrap


# ------------------------------------------------------------------------------
# ORIGIN ARTIFACT CHECKS
# ------------------------------------------------------------------------------
@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PACKAGING_STANDARDS,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
@app_package_extractable
def check_that_splunk_app_package_has_read_permission(app: "App", reporter: "Reporter") -> None:
    """
    Check that the Splunk app provided does not contain incorrect permissions.
    Packages must have the owner's read permission set to r (400).
    """
    if not app.package.does_origin_artifact_have_read_permission():
        reporter_output = "Splunk App package does not contain owner read permission and cannot be extracted."
        reporter.fail(reporter_output)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PACKAGING_STANDARDS,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_that_splunk_app_package_valid_compressed_file(app: "App", reporter: "Reporter") -> None:
    """Check that the Splunk app provided a valid compressed file."""
    if not app.package.is_origin_artifact_valid_compressed_file():
        reporter_output = (
            "Splunk App package is not a valid compressed file and cannot be extracted. "
            f"Origin artifact name: {app.package.origin_artifact_name}"
        )
        reporter.fail(reporter_output)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PACKAGING_STANDARDS,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
@app_package_extractable
def check_that_splunk_app_package_name_does_not_start_with_period(app: "App", reporter: "Reporter") -> None:
    """Check that the Splunk app provided does not start with a `.` character."""
    if app.package.does_origin_artifact_start_with_period():
        if app.package.origin_artifact_name.startswith("."):
            reporter_output = (
                "Splunk App packages cannot start with a `.` as its name. "
                f"Origin artifact name: {app.package.origin_artifact_name}"
            )
        else:
            reporter_output = (
                "Splunk App packages cannot start with a `.` as its name. "
                f"Origin package name: {app.package.origin_package_name}"
            )
        reporter.fail(reporter_output)


# ------------------------------------------------------------------------------
# WORKING ARTIFACT CHECKS
# ------------------------------------------------------------------------------
@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PACKAGING_STANDARDS,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_that_splunk_app_package_extracts_to_visible_directory(app: "App", reporter: "Reporter") -> None:
    """Check that the compressed artifact extracts to a directory that does not start with a `.` character."""
    if app.package.working_artifact_name.startswith("."):
        reporter_output = (
            "Splunk App packages must extract to a directory"
            " that is not hidden. The Splunk App package"
            f" extracted to: {app.package.working_artifact_name}"
        )

        reporter.fail(reporter_output)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PACKAGING_STANDARDS,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
@app_package_extractable
def check_that_splunk_app_package_does_not_contain_files_outside_of_app(app: "App", reporter: "Reporter") -> None:
    """
    Check that the Splunk App package does not contain any non-app files. Files within a valid app folder or valid
    dependencies within a .dependencies folder are permitted, all other files are not.
    """
    # Files inside app package's working_artifact
    for file_or_folder_outside_app in app.package.find_files_not_part_of_valid_apps():
        # Relative path to the app_dir, since these are outside the app_dir they
        # will most likely be of the form "../myfile.txt"
        relative_loc = Path(os.path.relpath(file_or_folder_outside_app, app.app_dir))
        if relative_loc == Path("."):
            pass
        else:
            reporter_output = (
                "A file or folder was found outside of the app"
                f" directory. Please remove this file or folder: {relative_loc}"
            )
            reporter.fail(reporter_output)

    # Special case: if an origin artifact has non-app files associated with it
    # those are passed to the app.package to be called out here
    # For example, a tarball of tarball apps mixed with non-app files.
    # The app.package would be the first valid app tarball, the paths to
    # the non-app files within the overall package are captured here.

    # Files inside the origin package's working_artifact
    for file_or_folder_outside_app in app.package.origin_package_non_app_files:
        # These paths are relative to the origin app package which may or may
        # not be relative to the app_dir.
        reporter_output = (
            "A file or folder was found outside of the app"
            " within the overall package. OR the file or folder does not have expected permission. "
            f"Please remove this file or folder OR modify the permission : {file_or_folder_outside_app}"
        )
        reporter.fail(reporter_output)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PACKAGING_STANDARDS,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
@app_package_extractable
def check_that_splunk_app_package_with_static_dependencies_has_exactly_one_app_folder(
    app: "App", reporter: "Reporter"
) -> None:
    """Check that the Splunk App package with a .dependencies directory also contains exactly one valid app folder."""
    # If no .dependencies folder exists, return N/A
    if not app.package.does_package_contain_dependencies_folder():
        reporter_output = (
            f"No {app.dependencies_directory_path} folder found. "
            "Please add a .dependencies directory with an valid "
            "app folder."
        )
        reporter.not_applicable(reporter_output)
        return

    # If .dependencies folder exists but more than one folder exists as
    # sibling directories, return FAIL (app of apps + .dependencies are not
    # supported, only one or the other)
    contents = os.listdir(app.package.working_artifact)
    all_contents_are_folders = all(
        [os.path.isdir(os.path.join(app.package.working_artifact, path)) for path in contents]
    )
    relative_dependencies_path = app.package.DEPENDENCIES_LOCATION
    relative_working_app_path = os.path.relpath(app.package.working_app_path, app.package.working_artifact)
    if (
        len(contents) != 2
        or not all_contents_are_folders
        or relative_dependencies_path not in contents
        or relative_working_app_path not in contents
    ):
        reporter_output = (
            f"Only a single app folder and a single {app.dependencies_directory_path} "
            "folder should be included for apps packaged with static dependencies "
            "using the Splunk Packaging Toolkit."
        )
        reporter.fail(reporter_output)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
@app_package_extractable
def check_that_splunk_app_package_with_static_dependencies_has_app_manifest(app: "App", reporter: "Reporter") -> None:
    """
    Check that the Splunk App package with a .dependencies directory also
    contains an app folder with an app.manifest.
    """
    # If no .dependencies folder exists, return N/A
    if not app.package.does_package_contain_dependencies_folder():
        reporter_output = (
            f"No {app.dependencies_directory_path} folder found. "
            "Please add a .dependencies directory that contains "
            "an app folder with an app.manifest."
        )
        reporter.not_applicable(reporter_output)
        return

    # If .dependencies folder exists and single sibling directory is a valid
    # app but contains no app.manifest, return FAIL (.dependencies is only
    # valid when packaged and specified with slim)
    if not app.package.does_working_artifact_contain_app_manifest():
        reporter_output = (
            "App folder associated with package does not"
            f" contain an app.manifest file but contains "
            f" a {app.dependencies_directory_path} directory."
            " Apps packaged with static dependencies using the"
            " Splunk Packaging Toolkit are required to have an"
            " app.manifest file."
        )
        reporter.fail(reporter_output)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PACKAGING_STANDARDS,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
@app_package_extractable
def check_that_splunk_app_package_has_valid_static_dependencies(app: "App", reporter: "Reporter") -> None:
    """Check that the Splunk App package contains only valid dependencies.
    Dependencies are valid if a .dependencies directory contains only valid
    app packages inside.
    """
    # If no .dependencies folder exists, return N/A
    if not app.package.does_package_contain_dependencies_folder():
        reporter_output = (
            f"No {app.dependencies_directory_path} folder found. "
            "Please check that the Splunk App "
            "package contains only valid dependencies."
        )
        reporter.not_applicable(reporter_output)
        return

    # At this point, we accept that the .dependencies folder is valid - now
    # let's validate the contents of it. It should contain only valid app
    # packages and nothing else
    dependencies_folder = app.package.dependencies_folder
    dependencies_contents = os.listdir(dependencies_folder)

    for dependency_resource in dependencies_contents:
        resource_path = Path(app.package.dependencies_folder, dependency_resource)
        generated_app_package = app.package.generate_app_package_from_file_or_folder(resource_path)
        if generated_app_package is None:
            reporter_output = (
                "Resource within the .dependencies folder that"
                " does not appear to be a valid app package."
                " Please remove this file or folder: "
                f" {app.dependencies_directory_path}/{dependency_resource}"
            )
            reporter.fail(reporter_output)

    # TODO: we may want to do some sort of validation that the dependencies
    # listed in app.manifest match what we see in the .dependencies
    # directory at some point. SLIM is probably the best place to do this
    # validation, however it does not appear to be supported at this time.
    # (running `slim validate` on an app with extra apps in the
    # .dependencies folder not listed in the app.manifest does not raise any
    # errors) - see APPMAN-20.


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PACKAGING_STANDARDS,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
@app_package_extractable
def check_that_extracted_splunk_app_does_not_contain_prohibited_directories_or_files(
    app: "App", reporter: "Reporter"
) -> None:
    """
    Check that the extracted Splunk App does not contain any directories or
    files that start with a `.`, or directories that start with `__MACOSX`.
    """
    prohibited_directories_and_files = app.package.find_prohibited_files(
        app.package.working_artifact, [app.package.DEPENDENCIES_LOCATION]
    )
    for prohibited_directory_or_file in prohibited_directories_and_files:
        # Relative path to the app_dir
        relative_loc = os.path.relpath(prohibited_directory_or_file, app.app_dir)
        reporter_output = f"A prohibited file or directory was found in the extracted Splunk App: {relative_loc}"
        reporter.fail(reporter_output)

    # Check that the .tar Splunk Cloud App package does not contain files starting with `./`
    if not isinstance(app.package, TarAppPackage):
        return
    found_dot_slash_paths = []
    for content_path_name in app.package.get_content_path_names():
        if any(content_path_name.startswith(found_path) for found_path in found_dot_slash_paths):
            continue
        if content_path_name.startswith("./"):
            reporter.fail(
                "Paths inside of tar file installed on a splunk cloud should not start with dot slash `./`.",
                file_name=content_path_name,
            )
            found_dot_slash_paths.append(content_path_name)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PACKAGING_STANDARDS,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
@app_package_extractable
def check_that_extracted_splunk_app_contains_default_app_conf_file(app: "App", reporter: "Reporter") -> None:
    """Check that the extracted Splunk App contains a `default/app.conf` file."""
    _is_check_app_config_file(app, reporter, "fail")


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
def check_that_extracted_splunk_app_does_not_contains_only_app_conf_file(app: "App", reporter: "Reporter") -> None:
    """Check that the extracted Splunk App does not contain only `app.conf`"""
    conf_dirs = {Path("local"), Path("default"), *app.get_user_paths("local")}
    for directory, filename, _ in app.iterate_files():
        if directory in conf_dirs and filename != "app.conf":
            return
        elif directory not in conf_dirs:
            return

    reporter.fail("The app package must have some directories, assets, code or .conf files apart from app.conf.")


class CheckVersionIsValidSemver(Check):
    settings_to_check = (
        # (section, option, action_if_missing, action_if_invalid)
        ("id", "version", WarningMessage, FailMessage),
        ("launcher", "version", WarningMessage, FailMessage),
    )

    def __init__(self):
        super().__init__(
            config=CheckConfig(
                name="check_version_is_valid_semver",
                description="Check that the extracted Splunk App contains a `default/app.conf` file "
                "that contains an `[id]` or `[launcher]` stanza with a `version` property that "
                "is formatted as Semantic Versioning 2.0.0 (https://semver.org/).",
                depends_on_config=("app",),
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

    @staticmethod
    def _is_valid_version_number(version_number: str) -> bool:
        is_valid = semver.VersionInfo.isvalid if hasattr(semver.VersionInfo, "isvalid") else semver.Version.is_valid
        return is_valid(version_number)

    def check(self, app: "App") -> Generator[CheckMessage, Any, None]:
        # Initialize the list of version
        self._versions = []

        # Run all the check methods
        yield from super(type(self), self).check(app) or []

        # Verify that all the versions match
        if len(set([app_version for (_, _, _, _, app_version) in self._versions])) == 1:
            return

        for (
            file_name,
            stanza,
            property_name,
            line_number,
            app_version,
        ) in self._versions:
            if line_number:
                reporter_output = (
                    f"{app_version} specified in {property_name} in the "
                    f"`[{stanza}]` stanza of {file_name} does not match other "
                    "versions specified in the app. All version numbers specified in an app must match."
                )
            else:
                reporter_output = (
                    f"{app_version} specified in {property_name} of {file_name} "
                    "does not match other versions specified in the app. All "
                    "version numbers specified in an app must match."
                )

            yield FailMessage(
                reporter_output,
                file_name=file_name,
                line_number=line_number,
            )

    def check_config(self, app: "App", config: "ConfigurationProxy") -> Generator[CheckMessage, Any, None]:
        conf_versions = []

        conf_file = config["app"]

        for (
            section_name,
            option_name,
            action_if_missing,
            action_if_invalid,
        ) in self.settings_to_check:
            if not conf_file.has_section(section_name):
                # Missing the config file or the section
                yield action_if_missing(
                    f"No `[{section_name}]` section found in app.conf file.",
                    file_name=conf_file.get_relative_path() if conf_file else "default/app.conf",
                )
                continue

            section = conf_file.get_section(section_name)

            if not section.has_option(option_name):
                # Has the config file and section, but missing the option
                yield action_if_missing(
                    f"A `{option_name}` attribute formatted as a valid semver 2.0.0 string is required in "
                    f"the `[{section_name}]` stanza of app.conf.",
                    file_name=section.get_relative_path(),
                    line_number=section.get_line_number(),
                )
                continue

            option = section.get_option(option_name)

            if not self._is_valid_version_number(option.value):
                yield action_if_invalid(
                    f"The version {option.value} in the `{option_name}` attribute in the "
                    f"`[{section_name}]` stanza of app.conf is invalid. Versions "
                    f"must be specified as a valid semver 2.0.0 string.",
                    file_name=option.get_relative_path(),
                    line_number=option.get_line_number(),
                )

            conf_versions.append(
                (
                    option.get_relative_path(),
                    section_name,
                    option_name,
                    option.get_line_number(),
                    option.value,
                )
            )

        if len(conf_versions) == 0:
            yield FailMessage(
                "The `version` attribute must be specified in either the `[id]` or `[launcher]` stanzas.",
                file_name=conf_file.get_relative_path(),
            )

        self._versions.extend(conf_versions)

    @Check.depends_on_files(names=["app.manifest"], recurse_depth=0)
    def check_app_manifest(self, app: "App", path_in_app: Path) -> Generator[CheckMessage, Any, None]:
        try:
            with open(app.get_filename(path_in_app), "r") as manifest_json_file:
                manifest_json = json.load(manifest_json_file)

            manifest_version = manifest_json.get("info").get("id").get("version")
        except (ValueError, AttributeError):
            # No version found in the app.manifest so don't try to validate it
            pass
        except Exception:
            yield SkipMessage("The `app.manifest` file could not be loaded.")
        else:
            if not self._is_valid_version_number(manifest_version):
                yield FailMessage(
                    f"App contains `app.manifest` but the version {manifest_version} specified in "
                    "`info.id.version` attribute is invalid. Versions must be specified as "
                    f"a valid semver 2.0.0 string.",
                    file_name=path_in_app,
                    remediation="Correct the value of `info.id.version`, or remove `app.manifest` "
                    "if it is not required.",
                )

            self._versions.append((path_in_app, None, "info.id.version", None, manifest_version))


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PACKAGING_STANDARDS,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
@app_package_extractable
def check_that_extracted_splunk_app_does_not_contain_invalid_directories(app: "App", reporter: "Reporter") -> None:
    """
    Check that the extracted Splunk App does not contain any directories with incorrect permissions. Directories and
    subdirectories must have the owner's permissions set to r/w/x (700).
    """

    invalid_directories = app.package.find_invalid_directories_with_wrong_permission(
        app.package.working_artifact, stat.S_IRWXU
    )
    for invalid_directory in invalid_directories:
        reporter_output = f"An invalid directory was found in the extracted Splunk App: {invalid_directory}"
        reporter.fail(reporter_output)


@splunk_appinspect.tags(
    Tags.SPLUNK_APPINSPECT,
    Tags.CLOUD,
    Tags.PACKAGING_STANDARDS,
    Tags.PRIVATE_APP,
    Tags.PRIVATE_VICTORIA,
    Tags.MIGRATION_VICTORIA,
    Tags.PRIVATE_CLASSIC,
)
@app_package_extractable
def check_that_extracted_splunk_app_does_not_contain_files_with_invalid_permissions(
    app: "App", reporter: "Reporter"
) -> None:
    """
    Check that the extracted Splunk App does not contain any files with incorrect permissions. Files must have the
    owner's permissions include read and write (600).
    """
    invalid_files = app.package.find_files_with_incorrect_permissions(
        app.package.working_artifact, stat.S_IRUSR | stat.S_IWUSR
    )
    for invalid_file in invalid_files:
        reporter_output = f"An invalid file was found in the extracted Splunk App: {invalid_file}"
        reporter.fail(reporter_output)


class CheckPackageCompression(Check):
    def __init__(self) -> None:
        super().__init__(
            config=CheckConfig(
                name="check_package_compression",
                description="Check that the package is compressed correctly.",
                tags=(
                    Tags.PACKAGING_STANDARDS,
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
        location = str(app.package.origin_path)

        # Skip checks for directories and .zip files
        if os.path.isdir(location) or location.lower().endswith(".zip"):
            return

        CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB
        data_found = False

        try:
            with gzip.open(location, "rb") as f:
                buffered = io.BufferedReader(f)
                while True:
                    chunk = buffered.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    data_found = True

            if not data_found:
                raise ValueError("Empty gzip archive")

        # TODO: Remove OSError once python3.7 is deprecated
        except (getattr(gzip, "BadGzipFile", OSError), EOFError, OSError, ValueError):
            yield FailMessage(
                "The package is not a valid gzip-compressed archive or is empty.",
                remediation=(
                    "Ensure the archive is properly gzip-compressed and contains valid files. "
                    "Avoid renaming unrelated files (e.g., .html) to .tar.gz. "
                    "The package may be corrupted, empty, truncated, or not compressed at all. "
                    "Repackage your app using standard tools. "
                    f"See: {SPLUNK_PACKAGING_DOC_URL}"
                ),
            )
