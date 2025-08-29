import logging
from typing import TYPE_CHECKING, cast

from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.python.utils import package_url
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning
from labels.parsers.collection.json import parse_json_with_tree_sitter
from labels.utils.strings import normalize_name

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import ItemsView

LOGGER = logging.getLogger(__name__)


def _get_version(value: IndexedDict[str, ParsedValue]) -> str:
    version = value.get("version")
    if not isinstance(version, str):
        return ""
    return version.strip("=<>~^ ")


def _get_packages(
    reader: LocationReadCloser,
    dependencies: ParsedValue | None,
    *,
    is_dev: bool = False,
) -> list[Package]:
    if dependencies is None or not isinstance(dependencies, IndexedDict):
        return []

    packages = []

    items: ItemsView[str, ParsedValue] = dependencies.items()
    for name, value in items:
        if not isinstance(value, IndexedDict) or not isinstance(name, str):
            continue
        version = _get_version(value)
        if not name or not version:
            continue

        new_location = get_enriched_location(
            reader.location, line=value.position.start.line, is_dev=is_dev
        )

        normalized_name = normalize_name(name, PackageType.PythonPkg)
        p_url = package_url(normalized_name, version, None)

        try:
            packages.append(
                Package(
                    name=normalized_name,
                    version=version,
                    locations=[new_location],
                    language=Language.PYTHON,
                    type=PackageType.PythonPkg,
                    p_url=p_url,
                    licenses=[],
                    is_dev=is_dev,
                ),
            )
        except ValidationError as ex:
            log_malformed_package_warning(new_location, ex)
            continue

    return packages


def parse_pipfile_lock_deps(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    content = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    deps: ParsedValue | None = content.get("default")
    dev_deps: ParsedValue | None = content.get("develop")
    packages = [
        *_get_packages(reader, deps),
        *_get_packages(reader, dev_deps, is_dev=True),
    ]
    return packages, []
