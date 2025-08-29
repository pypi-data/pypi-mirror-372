import logging
import re
from typing import NotRequired, TypedDict

from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.javascript.model import YarnLockEntry
from labels.parsers.cataloger.javascript.package import package_url
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning

LOGGER = logging.getLogger(__name__)


def _resolve_pair(line: str) -> tuple[str, str]:
    line = line.strip()
    if ": " in line:
        key, value = line.split(": ")
        return key.strip(), value.strip()

    key, value = line.split(" ", maxsplit=1)
    return key.strip(), value.strip()


def _count_indentation(line: str) -> int:
    # Stripping the leading spaces and comparing the length difference
    return len(line) - len(line.lstrip(" "))


def _is_start_of_list(
    current_package: str | None,
    current_package_version: str | None,
    line: str,
) -> bool:
    return bool(
        current_package and current_package_version and ":" in line and line.strip().endswith(":"),
    )


def _is_list_item(
    current_package: str | None,
    current_package_version: str | None,
    current_key: str | None,
    current_indentation: int | None,
    line: str,
) -> bool:
    return bool(
        current_package
        and current_package_version
        and current_key
        and current_indentation
        and _count_indentation(line) > current_indentation,
    )


class YarnPackage(TypedDict):
    checksum: str
    dependencies: NotRequired[list[tuple[str, str]]]
    integrity: NotRequired[str]
    line: int
    resolution: NotRequired[str]
    resolved: NotRequired[str]
    version: str


def parse_current_package(line: str, index: int) -> tuple[str | None, int | None]:
    line = line.strip()
    if match_ := re.match(r'^"?((?:@\w[\w\-\.]*/)?\w[\w\-\.]*)@', line):
        current_package = match_.groups()[0]
        current_package_line = index
    else:
        current_package = None
        current_package_line = None

    return current_package, current_package_line


def _parse_yarn_file(yarn_lock_content: str) -> dict[tuple[str, str], YarnPackage]:
    yarn_lock_lines = yarn_lock_content.strip().split("\n")

    # Dictionary to store the parsed yarn lock data
    parsed_yarn_lock = {}

    # Temporary variables for current package and dependencies
    current_package: str | None = None
    current_package_version: str | None = None
    current_indentation = None
    current_key = None

    # Iterate through each line and parse the content
    for index, line in enumerate(yarn_lock_lines, 1):
        if not line:
            current_indentation = None
            continue
        if line.startswith("#"):
            continue
        if not line.startswith(" "):
            current_package, current_package_line = parse_current_package(line, index)
            current_package_version = None
        if current_package and line.strip().startswith("version"):
            _, raw_version = _resolve_pair(line)
            current_package_version = raw_version.strip('"')
            parsed_yarn_lock[(current_package, current_package_version)] = {
                "line": current_package_line,
                "version": current_package_version,
            }
        elif _is_start_of_list(current_package, current_package_version, line):
            current_indentation = _count_indentation(line)
            current_key = line.strip().split(":")[0]
            parsed_yarn_lock[(current_package, current_package_version)][current_key] = []  # type: ignore[index, assignment]
        elif _is_list_item(
            current_package,
            current_package_version,
            current_key,
            current_indentation,
            line,
        ):
            parsed_yarn_lock[(current_package, current_package_version)][current_key].append(  # type: ignore[union-attr, index]
                _resolve_pair(line)
            )
        elif current_package and current_package_version:
            current_indentation = None
            key, value = _resolve_pair(line)
            parsed_yarn_lock[(current_package, current_package_version)][key] = value.strip('"')

    return parsed_yarn_lock  # type: ignore[return-value]


def _get_name(pkg_info: tuple[str, str], item: YarnPackage) -> str:
    if resolution := item.get("resolution"):
        is_scoped_package = resolution.startswith("@")
        if is_scoped_package:
            return f"@{resolution.split('@')[1]}"
        return resolution.split("@")[0]

    return pkg_info[0]


def _extract_packages(
    parsed_yarn_lock: dict[tuple[str, str], YarnPackage],
    reader: LocationReadCloser,
) -> list[Package]:
    packages = []
    for pkg_info, item in parsed_yarn_lock.items():
        name = _get_name(pkg_info, item)
        version = item.get("version")

        if not name or not version:
            continue

        new_location = get_enriched_location(reader.location, line=item["line"])

        try:
            packages.append(
                Package(
                    name=name,
                    version=version,
                    locations=[new_location],
                    language=Language.JAVASCRIPT,
                    licenses=[],
                    type=PackageType.NpmPkg,
                    p_url=package_url(name, version),
                    metadata=YarnLockEntry(
                        resolved=item.get("resolved"),
                        integrity=item.get("integrity"),
                    ),
                ),
            )
        except ValidationError as ex:
            log_malformed_package_warning(new_location, ex)
            continue

    return packages


def _extract_relationships(
    parsed_yarn_lock: dict[tuple[str, str], YarnPackage],
    packages: list[Package],
) -> list[Relationship]:
    relationships = []
    for pkg_info, item in parsed_yarn_lock.items():
        current_pkg = next(
            (package for package in packages if package.name == _get_name(pkg_info, item)),
            None,
        )

        if current_pkg is None:
            continue

        if "dependencies" in item:
            for raw_dep_name, _ in item["dependencies"]:
                dep_name = raw_dep_name.strip('"')
                # TO-DO: check if the version matches
                if dep := next(
                    (package for package in packages if package.name == dep_name),
                    None,
                ):
                    relationships.append(
                        Relationship(
                            from_=dep.id_,
                            to_=current_pkg.id_,
                            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                        ),
                    )
    return relationships


def parse_yarn_lock(
    _resolver: Resolver | None,
    _environment: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    parsed_yarn_lock = _parse_yarn_file(reader.read_closer.read())
    packages = _extract_packages(parsed_yarn_lock, reader)
    relationships = _extract_relationships(parsed_yarn_lock, packages)
    return packages, relationships
