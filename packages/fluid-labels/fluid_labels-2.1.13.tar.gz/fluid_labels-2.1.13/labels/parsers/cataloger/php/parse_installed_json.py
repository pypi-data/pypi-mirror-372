import logging
from typing import cast

from labels.model.file import Location, LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship, RelationshipType
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.php.model import PhpComposerInstalledEntry, PhpComposerLockEntry
from labels.parsers.cataloger.php.package import new_package_from_composer
from labels.parsers.collection.json import parse_json_with_tree_sitter

LOGGER = logging.getLogger(__name__)
EMPTY_LIST: IndexedList[ParsedValue] = IndexedList()


def _is_dev_package(
    package: IndexedDict[str, ParsedValue], dev_packages: IndexedList[ParsedValue]
) -> bool:
    name_value = package.get("name")
    name = name_value if isinstance(name_value, str) else None

    return name in dev_packages if name else False


def _extract_packages(
    package_json: IndexedDict[str, ParsedValue],
    location: Location,
) -> list[Package]:
    packages = []
    if isinstance(package_json, IndexedDict) and "dev-package-names" in package_json:
        dev_packages = cast("IndexedList[ParsedValue]", package_json["dev-package-names"])
    else:
        dev_packages = EMPTY_LIST

    packages_list = (
        package_json["packages"] if isinstance(package_json, IndexedDict) else package_json
    )

    for package in packages_list if isinstance(packages_list, IndexedList) else EMPTY_LIST:
        if not isinstance(package, IndexedDict):
            continue

        is_dev = _is_dev_package(package, dev_packages)
        pkg_item = new_package_from_composer(package, location, is_dev=is_dev)
        if pkg_item:
            packages.append(pkg_item)

    return packages


def _extract_relationships(packages: list[Package]) -> list[Relationship]:
    relationships = []
    for package in packages:
        if not isinstance(package.metadata, PhpComposerInstalledEntry | PhpComposerLockEntry):
            continue
        package_metadata = package.metadata.require
        dependencies = list(package_metadata.keys()) if package_metadata else []
        for dep_name in dependencies:
            package_dep = next((x for x in packages if x.name == dep_name), None)
            if package_dep:
                relationships.append(
                    Relationship(
                        from_=package.id_,
                        to_=package_dep.id_,
                        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                    ),
                )

    return relationships


def parse_installed_json(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_json = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )

    packages = _extract_packages(package_json, reader.location)
    relationships = _extract_relationships(packages)

    return packages, relationships
