from typing import TYPE_CHECKING, cast

from labels.model.file import LocationReadCloser
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.cpp.package import new_conan_lock_dep
from labels.parsers.cataloger.utils import get_enriched_location
from labels.parsers.collection.json import parse_json_with_tree_sitter

if TYPE_CHECKING:
    from labels.model.indexables import IndexedDict, IndexedList


def parse_conan_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages = []
    conan_file = cast(
        "IndexedDict[str, IndexedList[str]]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )

    for index, dep_line in enumerate(conan_file.get("requires", [])):
        new_location = get_enriched_location(
            reader.location,
            line=conan_file["requires"].get_position(index).start.line,
            is_dev=False,
        )
        packages.append(
            new_conan_lock_dep(dep_line, new_location, is_dev=False),
        )

    for index, dep_line in enumerate(conan_file.get("build_requires", [])):
        new_dev_location = get_enriched_location(
            reader.location,
            line=conan_file["build_requires"].get_position(index).start.line,
            is_dev=True,
        )
        packages.append(
            new_conan_lock_dep(dep_line, new_dev_location, is_dev=True),
        )

    return packages, []
