import logging
from typing import cast

from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.javascript.model import NpmPackage
from labels.parsers.cataloger.javascript.package import package_url
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning
from labels.parsers.collection.json import parse_json_with_tree_sitter

LOGGER = logging.getLogger(__name__)


def _create_package(
    package_json: IndexedDict[str, ParsedValue],
    reader: LocationReadCloser,
    package_name: str,
    specifier: str,
    *,
    is_dev: bool,
) -> Package | None:
    dependencies_key = "devDependencies" if is_dev else "dependencies"
    pkg: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        package_json[dependencies_key],
    )

    new_location = get_enriched_location(
        reader.location,
        line=pkg.get_key_position(package_name).start.line,
        is_dev=is_dev,
        is_transitive=False,
    )

    try:
        return Package(
            name=package_name,
            version=specifier,
            type=PackageType.NpmPkg,
            language=Language.JAVASCRIPT,
            licenses=[],
            locations=[new_location],
            p_url=package_url(package_name, specifier),
            metadata=NpmPackage(
                name=package_name,
                version=specifier,
                is_dev=is_dev,
            ),
            is_dev=is_dev,
        )
    except ValidationError as ex:
        log_malformed_package_warning(new_location, ex)
        return None


def parse_package_json(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_json: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    deps: ParsedValue = package_json.get("dependencies", IndexedDict())
    if not isinstance(deps, IndexedDict):
        LOGGER.warning("No deps found in package JSON")
        return ([], [])

    packages = []
    for package_name, specifier in deps.items():
        if not package_name or not specifier:
            continue

        package = _create_package(
            package_json,
            reader,
            package_name,
            str(specifier),
            is_dev=False,
        )
        if package:
            packages.append(package)

    dev_deps: ParsedValue = package_json.get("devDependencies", IndexedDict())
    if not isinstance(dev_deps, IndexedDict):
        LOGGER.warning("No dev deps found in package JSON")
        return ([], [])
    for package_name, specifier in dev_deps.items():
        if not package_name or not specifier:
            continue

        package = _create_package(
            package_json,
            reader,
            package_name,
            str(specifier),
            is_dev=True,
        )
        if package:
            packages.append(package)

    return packages, []
