from typing import TYPE_CHECKING, cast

import os_release
from os_release.parser import OsReleaseParseException

from labels.model.package import Package
from labels.model.relationship import Relationship, RelationshipType
from labels.model.release import OsReleaseDict, Release
from labels.model.resolver import Resolver

if TYPE_CHECKING:
    from labels.parsers.cataloger.python.model import PythonPackage


def identify_release(resolver: Resolver) -> Release | None:
    possible_files = [
        "/etc/os-release",
        "/usr/lib/os-release",
        "/etc/system-release-cpe",
        "/etc/redhat-release",
        "/bin/busybox",
    ]

    for file in possible_files:
        if not resolver.has_path(file):
            continue
        location = resolver.files_by_path(file)[0]
        content_reader = resolver.file_contents_by_location(location)
        if not content_reader:
            continue
        content = content_reader.read()
        release = parse_os_release(content)
        if release:
            return release
    return None


def parse_os_release(content: str) -> Release | None:
    try:
        release: OsReleaseDict | None = os_release.parse_str(content)
    except OsReleaseParseException:
        release = _force_parse(content)
    if release:
        id_like: list[str] = []
        if "ID_LIKE" in release:
            id_like = sorted(release["ID_LIKE"].split(" "))
        return Release(
            pretty_name=release.get("PRETTY_NAME", ""),
            name=release.get("NAME", ""),
            id_=release.get("ID", ""),
            id_like=id_like,
            version=release.get("VERSION", ""),
            version_id=release.get("VERSION_ID", ""),
            version_code_name=release.get("VERSION_CODENAME", ""),
            build_id=release.get("BUILD_ID", ""),
            image_id=release.get("IMAGE_ID", ""),
            image_version=release.get("IMAGE_VERSION", ""),
            variant=release.get("VARIANT", ""),
            variant_id=release.get("VARIANT_ID", ""),
            home_url=release.get("HOME_URL", ""),
            support_url=release.get("SUPPORT_URL", ""),
            bug_report_url=release.get("BUG_REPORT_URL", ""),
            privacy_policy_url=release.get("PRIVACY_POLICY_URL", ""),
            cpe_name=release.get("CPE_NAME", ""),
            support_end=release.get("SUPPORT_END", ""),
        )
    return None


def _is_valid_key(key: str) -> bool:
    return key.isidentifier() and key.isupper()


def _force_parse(content: str) -> OsReleaseDict | None:
    lines: list[tuple[str, str]] = []

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip("\"'")

        if not _is_valid_key(key):
            continue

        lines.append((key, value))

    if not lines:
        return None
    return cast("OsReleaseDict", dict(lines))


def strip_version_specifier(item: str) -> str:
    # Define the characters that indicate the start of a version specifier
    specifiers = "[(<>="

    # Find the index of the first occurrence of any specifier character
    index = next((i for i, char in enumerate(item) if char in specifiers), None)

    # If no specifier character is found, return the original string
    if index is None:
        return item.strip()

    # Return the substring up to the first specifier character, stripped of
    # leading/trailing whitespace
    return item[:index].strip()


def handle_relationships(packages: list[Package]) -> list[Relationship]:
    relationships: list[Relationship] = []
    for package in packages:
        if package.found_by == "python-installed-package-cataloger":
            python_package: PythonPackage = cast("PythonPackage", package.metadata)
            for dep in python_package.dependencies if python_package.dependencies else []:
                dep_name = strip_version_specifier(dep)
                if dep_package := next((x for x in packages if x.name == dep_name), None):
                    relationships.append(
                        Relationship(
                            from_=dep_package.id_,
                            to_=package.id_,
                            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                        ),
                    )
    return relationships
