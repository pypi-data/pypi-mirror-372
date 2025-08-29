import logging
from collections.abc import Iterator
from typing import TYPE_CHECKING, cast

from more_itertools import flatten
from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.dotnet.utils import get_relationships_from_declared_dependencies
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning
from labels.parsers.collection.json import parse_json_with_tree_sitter
from labels.utils.strings import normalize_name

if TYPE_CHECKING:
    from collections.abc import Iterator

LOGGER = logging.getLogger(__name__)
EMPTY_DICT: IndexedDict[str, ParsedValue] = IndexedDict()


def parse_dotnet_package_lock(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_json = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    packages: list[Package] = []
    target_deps: ParsedValue = package_json.get("dependencies", IndexedDict())
    if not isinstance(target_deps, IndexedDict):
        LOGGER.warning("No deps found in package JSON")
        return ([], [])
    dependencies: dict[str, ParsedValue] = {}

    for package_name, package_value in cast(
        "Iterator[IndexedDict[str, ParsedValue]]",
        flatten(x.items() for x in target_deps.values() if isinstance(x, IndexedDict)),
    ):
        if not isinstance(package_value, IndexedDict):
            continue

        is_transitive = package_value.get("type", "") == "Transitive"
        version: str | None = package_value.get("resolved")

        if not package_name or not version:
            continue

        normalized_package_name = normalize_name(package_name, PackageType.DotnetPkg)
        p_url = PackageURL(
            type="nuget",
            namespace="",
            name=normalized_package_name,
            version=version,
            qualifiers={},
            subpath="",
        ).to_string()

        new_location = get_enriched_location(
            reader.location, line=package_value.position.start.line, is_transitive=is_transitive
        )

        dependencies[normalized_package_name] = package_value.get("dependencies", EMPTY_DICT)

        try:
            packages.append(
                Package(
                    name=normalized_package_name,
                    version=version,
                    locations=[new_location],
                    licenses=[],
                    type=PackageType.DotnetPkg,
                    language=Language.DOTNET,
                    metadata=None,
                    p_url=p_url,
                ),
            )
        except ValidationError as ex:
            log_malformed_package_warning(new_location, ex)
            continue

    return packages, get_relationships_from_declared_dependencies(packages, dependencies)
