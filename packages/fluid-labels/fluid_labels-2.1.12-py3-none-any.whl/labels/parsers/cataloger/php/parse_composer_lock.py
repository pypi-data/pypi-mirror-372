import logging
from typing import cast

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship, RelationshipType
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.php.model import PhpComposerInstalledEntry, PhpComposerLockEntry
from labels.parsers.cataloger.php.package import new_package_from_composer
from labels.parsers.collection.json import parse_json_with_tree_sitter

LOGGER = logging.getLogger(__name__)
EMPTY_DICT: IndexedDict[str, ParsedValue] = IndexedDict()


def parse_composer_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_json: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    packages: list[Package] = []
    relationships: list[Relationship] = []
    pkgs: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        package_json.get("packages", EMPTY_DICT),
    )
    pkgs_dev: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        package_json.get("packages-dev", EMPTY_DICT),
    )
    for is_dev, package in [
        *[(False, x) for x in pkgs],
        *[(True, x) for x in pkgs_dev],
    ]:
        if not isinstance(package, IndexedDict):
            continue

        if pkg := new_package_from_composer(package, reader.location, is_dev=is_dev):
            packages.append(pkg)

    for parsed_pkg in packages:
        if not isinstance(parsed_pkg.metadata, PhpComposerInstalledEntry | PhpComposerLockEntry):
            continue
        for dep_name in parsed_pkg.metadata.require or []:
            package_dep = next(
                (x for x in packages if x.name == dep_name),
                None,
            )
            if package_dep:
                relationships.append(
                    Relationship(
                        from_=parsed_pkg.id_,
                        to_=package_dep.id_,
                        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                    ),
                )
    return packages, relationships
