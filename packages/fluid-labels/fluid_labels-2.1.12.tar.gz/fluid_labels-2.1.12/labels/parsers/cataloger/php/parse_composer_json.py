from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import ItemsView

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.php.package import package_url
from labels.parsers.cataloger.utils import get_enriched_location
from labels.parsers.collection.json import parse_json_with_tree_sitter

EMPTY_DICT: IndexedDict[str, ParsedValue] = IndexedDict()


def _get_packages(
    reader: LocationReadCloser,
    dependencies: IndexedDict[str, ParsedValue],
    *,
    is_dev: bool,
) -> list[Package]:
    if not dependencies:
        return []

    items: ItemsView[str, ParsedValue] = dependencies.items()
    packages = []
    for name, version in items:
        if not isinstance(version, str):
            continue

        new_location = get_enriched_location(
            reader.location,
            line=dependencies.get_key_position(name).start.line,
            is_dev=is_dev,
            is_transitive=False,
        )
        p_url = package_url(name, version)

        packages.append(
            Package(
                name=name,
                version=version,
                locations=[new_location],
                language=Language.PHP,
                licenses=[],
                type=PackageType.PhpComposerPkg,
                p_url=p_url,
                is_dev=is_dev,
            )
        )

    return packages


def parse_composer_json(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    content = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    deps: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        content.get("require", EMPTY_DICT),
    )
    dev_deps: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        content.get("require-dev", EMPTY_DICT),
    )
    packages = [
        *_get_packages(reader, deps, is_dev=False),
        *_get_packages(reader, dev_deps, is_dev=True),
    ]
    return packages, []
