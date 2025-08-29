import logging
import re
from typing import cast

from pydantic import ValidationError

from labels.model.file import Location, LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Digest, Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.javascript.model import PnpmEntry
from labels.parsers.cataloger.javascript.package import package_url
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning
from labels.parsers.collection.yaml import parse_yaml_with_tree_sitter

LOGGER = logging.getLogger(__name__)

VERSION_PATTERN = re.compile(r"(\d+\.\d+\.\d+(-[0-9A-Za-z\.]+)?)")


def extract_package_name_from_key_dependency(item: str) -> str | None:
    # Regex pattern to extract the package name
    pattern = r"^@?[\w-]+/[\w-]+$"
    match = re.match(pattern, item)
    if match:
        return match.group(0)
    return None


def extract_version_from_value_dependency(item: str) -> str | None:
    # Regex pattern to extract the version number before any parentheses
    pattern = r"^(\d+\.\d+\.\d+)"
    match = re.match(pattern, item)
    if match:
        return match.group(1)
    return None


def _get_package(
    packages: list[Package],
    dep_name: str | None,
    dep_version: str | None,
) -> Package | None:
    return next(
        (x for x in packages if x.name == dep_name and x.version == dep_version),
        None,
    )


def _process_relationships(
    dependencies: IndexedDict[str, ParsedValue],
    packages: list[Package],
    current_package: Package | None,
) -> list[Relationship]:
    relationships: list[Relationship] = []
    for raw_dep_name, raw_dep_version in dependencies.items():
        if not isinstance(raw_dep_version, str):
            continue
        dep_name = extract_package_name_from_key_dependency(
            raw_dep_name,
        )
        dep_version = extract_version_from_value_dependency(
            raw_dep_version,
        )
        if (dep := _get_package(packages, dep_name, dep_version)) and current_package:
            relationships.append(
                Relationship(
                    from_=dep.id_,
                    to_=current_package.id_,
                    type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                ),
            )
    return relationships


def _generate_relations_relationship(
    package_yaml: IndexedDict[str, ParsedValue],
    packages: list[Package],
) -> list[Relationship]:
    relationships: list[Relationship] = []
    packages_items = package_yaml["packages"]
    if not isinstance(packages_items, IndexedDict):
        return relationships
    for package_key, package_value in packages_items.items():
        if not isinstance(package_value, IndexedDict):
            continue
        if match_ := re.search(r"/(@?[^@]+)@(\d+\.\d+\.\d+)", package_key):
            package_name = match_.groups()[0]
            package_version = match_.groups()[1]
            current_package = _get_package(
                packages,
                dep_name=package_name,
                dep_version=package_version,
            )
            dependencies = package_value.get("dependencies")
            if dependencies and isinstance(dependencies, IndexedDict):
                relationships.extend(
                    _process_relationships(dependencies, packages, current_package),
                )
    return relationships


def _get_package_metadata(
    package_value: IndexedDict[str, ParsedValue],
    *,
    is_dev: bool,
) -> PnpmEntry:
    resolution_value = package_value.get("resolution")
    integrity_value = (
        resolution_value.get("integrity") if isinstance(resolution_value, IndexedDict) else None
    )

    integrity_value = integrity_value if isinstance(integrity_value, str) else None

    return PnpmEntry(
        is_dev=is_dev if isinstance(is_dev, bool) else False,
        integrity=Digest(
            algorithm="sha-512",
            value=integrity_value,
        ),
    )


def manage_coordinates(
    package_yaml: IndexedDict[str, ParsedValue],
    package_info: dict[str, str | list[ParsedValue]],
    base_location: Location,
    *,
    is_dev: bool,
) -> Location:
    packages = package_yaml.get("packages")
    if not isinstance(packages, IndexedDict):
        return base_location

    key = package_info.get("key")
    name = package_info.get("name")
    deps = package_info.get("dependencies")

    if not isinstance(key, str) or not isinstance(name, str) or not isinstance(deps, list):
        return base_location

    position = packages.get_key_position(key)
    is_transitive = name not in deps

    return get_enriched_location(
        base_location,
        line=position.start.line,
        is_transitive=is_transitive,
        is_dev=is_dev,
    )


def process_package_string(
    package: str,
    spec: IndexedDict[str, ParsedValue],
) -> tuple[str, str] | None:
    if package.startswith("github"):
        pkg_name = spec.get("name", "")
        pkg_version = spec.get("version", "")
    else:
        pkg_info: list[str] = VERSION_PATTERN.split(package.strip("\"'"))
        if len(pkg_info) < 2:
            return None
        pkg_name = pkg_info[0].lstrip("/")[0:-1]
        pkg_version = pkg_info[1]

    if not isinstance(pkg_name, str) or not isinstance(pkg_version, str):
        return None
    return pkg_name, pkg_version


def _process_package(
    package_key: str,
    pkg_spec: IndexedDict[str, ParsedValue],
    package_yaml: IndexedDict[str, ParsedValue],
    direct_dependencies: list[ParsedValue],
    base_location: Location,
) -> Package | None:
    if match_ := process_package_string(package_key, pkg_spec):
        package_name = match_[0]
        package_version = match_[1]

        if not package_name or not package_version:
            return None

        is_dev = pkg_spec.get("dev") is True

        package_info: dict[str, str | list[ParsedValue]] = {
            "key": package_key,
            "name": package_name,
            "dependencies": direct_dependencies,
        }

        new_location = manage_coordinates(package_yaml, package_info, base_location, is_dev=is_dev)

        try:
            return Package(
                name=package_name,
                version=package_version,
                locations=[new_location],
                language=Language.JAVASCRIPT,
                licenses=[],
                type=PackageType.NpmPkg,
                p_url=package_url(package_name, package_version),
                metadata=_get_package_metadata(pkg_spec, is_dev=is_dev),
            )
        except ValidationError as ex:
            log_malformed_package_warning(new_location, ex)
    return None


def parse_pnpm_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_yaml: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        parse_yaml_with_tree_sitter(reader.read_closer.read()),
    )

    if not package_yaml:
        return [], []
    dependencies = package_yaml.get("dependencies")
    dev_dependencies = package_yaml.get("devDependencies")
    direct_dependencies: list[ParsedValue] = []
    if isinstance(dependencies, IndexedList) and isinstance(dev_dependencies, IndexedList):
        direct_dependencies = [*dev_dependencies, *dependencies]
    packages: list[Package] = []
    relationships: list[Relationship] = []
    packages_items = package_yaml["packages"]
    if not isinstance(packages_items, IndexedDict):
        return [], []
    for package_key, pkg_spec in packages_items.items():
        if not isinstance(pkg_spec, IndexedDict):
            continue
        if package := _process_package(
            package_key,
            pkg_spec,
            package_yaml,
            direct_dependencies,
            reader.location,
        ):
            packages.append(package)

    relationships = _generate_relations_relationship(package_yaml, packages)

    return packages, relationships
