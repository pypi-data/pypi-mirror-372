import logging
from typing import cast

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.swift.package import new_swift_package_manager_package
from labels.parsers.cataloger.utils import get_enriched_location
from labels.parsers.collection.json import parse_json_with_tree_sitter

LOGGER = logging.getLogger(__name__)
EMPTY_DICT: IndexedDict[str, ParsedValue] = IndexedDict()
EMPTY_LIST: IndexedList[ParsedValue] = IndexedList()


def _get_name_and_version(
    pin: ParsedValue,
) -> tuple[str, str, IndexedDict[str, ParsedValue]] | None:
    if not isinstance(pin, IndexedDict):
        return None
    state: ParsedValue = pin.get("state", EMPTY_DICT)
    name = pin.get("identity")
    if not isinstance(state, IndexedDict):
        return None
    version = state.get("version")

    if not name or not version or not isinstance(version, str) or not isinstance(name, str):
        return None

    return name, version, state


def parse_package_resolved(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_resolved: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )

    packages: list[Package] = []
    relationships: list[Relationship] = []
    package_resolved_pins: ParsedValue = package_resolved.get("pins", EMPTY_LIST)

    if isinstance(package_resolved_pins, IndexedList):
        for pin in package_resolved_pins:
            if not isinstance(pin, IndexedDict):
                continue
            info = _get_name_and_version(pin)
            if not info:
                continue

            new_location = get_enriched_location(
                reader.location, line=pin.get_key_position("identity").start.line
            )

            if pkg := new_swift_package_manager_package(
                name=info[0],
                version=info[1],
                source_url=pin.get("location"),
                revision=info[2].get("revision"),
                location=new_location,
            ):
                packages.append(pkg)

    return packages, relationships
