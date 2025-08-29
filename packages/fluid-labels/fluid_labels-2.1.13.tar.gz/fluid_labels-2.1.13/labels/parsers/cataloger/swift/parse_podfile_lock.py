import logging
from typing import (
    cast,
)

from labels.model.file import (
    LocationReadCloser,
)
from labels.model.indexables import (
    IndexedDict,
    IndexedList,
    ParsedValue,
)
from labels.model.package import Package
from labels.model.relationship import (
    Relationship,
    RelationshipType,
)
from labels.model.release import Environment
from labels.model.resolver import (
    Resolver,
)
from labels.parsers.cataloger.swift.package import (
    new_cocoa_pods_package,
)
from labels.parsers.cataloger.utils import get_enriched_location
from labels.parsers.collection.yaml import (
    parse_yaml_with_tree_sitter,
)

LOGGER = logging.getLogger(__name__)


def parse_podfile_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    try:
        podfile: IndexedDict[str, ParsedValue] = cast(
            "IndexedDict[str, ParsedValue]",
            parse_yaml_with_tree_sitter(reader.read_closer.read()),
        )
    except ValueError:
        return [], []

    if not podfile or "PODS" not in podfile:
        return [], []

    packages, dependencies_index = process_pods(podfile, reader)
    if not packages:
        return [], []

    relationships = generate_relations(dependencies_index, packages)

    return packages, relationships


def process_pods(
    podfile: IndexedDict[str, ParsedValue],
    reader: LocationReadCloser,
) -> tuple[list[Package], dict[str, list[str]]]:
    packages: list[Package] = []
    dependencies_index: dict[str, list[str]] = {}

    direct_dependencies = podfile["DEPENDENCIES"]
    pods = podfile["PODS"]
    if not isinstance(direct_dependencies, IndexedList) or not isinstance(pods, IndexedList):
        return [], {}

    for index, pod in enumerate(pods):
        pod_name, pod_version = extract_pod_info(pod)
        if not pod_name or not pod_version:
            return [], {}

        pod_root_package = pod_name.split("/")[0]
        checksums = podfile["SPEC CHECKSUMS"]
        if not isinstance(checksums, IndexedDict):
            return [], {}

        is_transitive = pod_name not in direct_dependencies
        new_location = get_enriched_location(
            reader.location,
            is_transitive=is_transitive,
            line=pods.get_position(index).start.line,
        )

        if pkg := new_cocoa_pods_package(
            pod_name,
            pod_version,
            checksums[pod_root_package],
            new_location,
        ):
            packages.append(pkg)
            dependencies_index[pod_name] = dependencies_index.get(pod_name, [])

    return packages, dependencies_index


def extract_pod_info(pod: ParsedValue) -> tuple[str, str]:
    if isinstance(pod, str | IndexedDict):
        pod_blob = pod if isinstance(pod, str) else next(iter(pod))
        pod_name = pod_blob.split(" ")[0]
        pod_version = pod_blob.split(" ")[1].strip("()")
        return pod_name, pod_version
    return "", ""


def generate_relations(
    dependencies_index: dict[str, list[str]],
    packages: list[Package],
) -> list[Relationship]:
    relationships: list[Relationship] = []
    for package_name, dependencies in dependencies_index.items():
        package = next(x for x in packages if x.name == package_name)
        relationships.extend(
            Relationship(
                from_=package_dep.id_,
                to_=package.id_,
                type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
            )
            for dependency in dependencies
            if (
                package_dep := next(
                    (x for x in packages if x.name == dependency.split(" ")[0]),
                    None,
                )
            )
        )

    return relationships
