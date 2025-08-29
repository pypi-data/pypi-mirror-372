import logging
from typing import (
    TypedDict,
    cast,
)

from pydantic import (
    BaseModel,
    ValidationError,
)

from labels.model.file import (
    Location,
    LocationReadCloser,
)
from labels.model.indexables import (
    IndexedDict,
    IndexedList,
    ParsedValue,
)
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import (
    Relationship,
    RelationshipType,
)
from labels.model.release import Environment
from labels.model.resolver import (
    Resolver,
)
from labels.parsers.cataloger.rust.utils import (
    package_url,
)
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning
from labels.parsers.collection.toml import (
    parse_toml_with_tree_sitter,
)

LOGGER = logging.getLogger(__name__)


class RustCargoLockEntry(BaseModel):
    name: str
    version: str
    source: str | None
    checksum: str | None
    dependencies: list[str]


class CargoLockEntry(TypedDict):
    name: str
    version: str
    source: str | None
    checksum: str | None
    dependencies: list[str]


class CargoLock(TypedDict):
    package: IndexedList[CargoLockEntry]


def _create_package(pkg: ParsedValue, location: Location) -> Package | None:
    if not isinstance(pkg, IndexedDict):
        return None
    name = str(pkg.get("name", "")) or None
    version = str(pkg.get("version", "")) or None

    if not name or not version:
        return None

    source = str(pkg.get("source", "")) or None
    dependencies: IndexedList[str] | None = cast("IndexedList[str] | None", pkg.get("dependencies"))
    checksum = str(pkg.get("checksum", "")) or None

    new_location = get_enriched_location(
        location,
        line=pkg.get_key_position("version").start.line,
    )

    try:
        return Package(
            name=name,
            version=version,
            locations=[new_location],
            language=Language.RUST,
            licenses=[],
            p_url=package_url(name, version),
            type=PackageType.RustPkg,
            metadata=RustCargoLockEntry(
                name=name,
                version=version,
                source=source,
                dependencies=list(dependencies or []),
                checksum=checksum,
            ),
        )
    except ValidationError as ex:
        log_malformed_package_warning(new_location, ex)
        return None


def _create_relationships(packages: list[Package]) -> list[Relationship]:
    relationships: list[Relationship] = []
    for pkg in packages:
        if isinstance(pkg.metadata, RustCargoLockEntry):
            relationships.extend(
                Relationship(
                    from_=pkg.id_,
                    to_=dep.id_,
                    type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                )
                for dep_name in pkg.metadata.dependencies
                if (dep := next((x for x in packages if x.name == dep_name), None))
            )
    return relationships


def parse_cargo_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []

    if not reader.location.coordinates:
        return packages, []

    _content = reader.read_closer.read()
    toml: IndexedDict[str, ParsedValue] = parse_toml_with_tree_sitter(
        _content,
    )

    toml_pkgs: ParsedValue = toml.get("package")
    if not isinstance(toml_pkgs, IndexedList):
        return [], []

    packages.extend(
        package
        for package in (_create_package(pkg, reader.location) for pkg in toml_pkgs)
        if package
    )

    relationships = _create_relationships(packages)

    return packages, relationships
