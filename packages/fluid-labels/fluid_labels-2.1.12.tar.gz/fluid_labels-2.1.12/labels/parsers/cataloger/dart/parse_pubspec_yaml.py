from typing import TYPE_CHECKING, cast

from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning
from labels.parsers.collection.yaml import parse_yaml_with_tree_sitter

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import ItemsView


def _get_packages(
    reader: LocationReadCloser,
    dependencies: IndexedDict[str, str] | None,
    *,
    is_dev: bool = False,
) -> list[Package]:
    if dependencies is None:
        return []
    packages = []
    items: ItemsView[str, IndexedDict[str, str] | str] = dependencies.items()
    for name, version in items:
        if not name or not isinstance(version, str) or not version:
            continue

        new_location = get_enriched_location(
            reader.location,
            line=dependencies.get_key_position(name).start.line,
            is_dev=is_dev,
            is_transitive=False,
        )

        try:
            packages.append(
                Package(
                    name=name,
                    version=version,
                    locations=[new_location],
                    language=Language.DART,
                    licenses=[],
                    type=PackageType.DartPubPkg,
                    p_url=PackageURL(  # type: ignore[misc]
                        type="pub",
                        name=name,
                        version=version,
                    ).to_string(),
                ),
            )
        except ValidationError as ex:
            log_malformed_package_warning(new_location, ex)
            continue
    return packages


def parse_pubspec_yaml(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    content = cast(
        "IndexedDict[str, IndexedDict[str, str]]",
        parse_yaml_with_tree_sitter(reader.read_closer.read()),
    )

    if not content:
        return [], []

    deps: IndexedDict[str, str] | None = content.get("dependencies")
    dev_deps: IndexedDict[str, str] | None = content.get("dev_dependencies")
    packages = [
        *_get_packages(reader, deps, is_dev=False),
        *_get_packages(reader, dev_deps, is_dev=True),
    ]
    return packages, []
