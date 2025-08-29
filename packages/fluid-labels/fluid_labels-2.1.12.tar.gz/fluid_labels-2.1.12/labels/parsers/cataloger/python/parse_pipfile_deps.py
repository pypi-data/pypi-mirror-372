import logging

from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.python.model import PythonPackage
from labels.parsers.cataloger.python.utils import package_url
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning
from labels.parsers.collection import toml
from labels.utils.strings import normalize_name

LOGGER = logging.getLogger(__name__)


def _get_packages(
    reader: LocationReadCloser,
    toml_packages: IndexedDict[str, ParsedValue],
    *,
    is_dev: bool = False,
) -> list[Package]:
    result = []
    for package, version_data in toml_packages.items():
        version: str = ""
        if isinstance(version_data, str):
            version = version_data.strip("=<>~^ ")
        if isinstance(version_data, IndexedDict):
            version = str(version_data.get("version", "*")).strip("=<>~^ ")

        if not package or not version or "*" in version:
            continue

        new_location = get_enriched_location(
            reader.location,
            line=package.position.start.line
            if isinstance(package, IndexedDict)
            else toml_packages.get_key_position(package).start.line,
            is_dev=is_dev,
            is_transitive=False,
        )

        normalized_name = normalize_name(package, PackageType.PythonPkg)
        p_url = package_url(normalized_name, version, None)

        try:
            result.append(
                Package(
                    name=normalized_name,
                    version=version,
                    locations=[new_location],
                    language=Language.PYTHON,
                    type=PackageType.PythonPkg,
                    metadata=PythonPackage(
                        name=package,
                        version=version,
                    ),
                    p_url=p_url,
                    licenses=[],
                    is_dev=is_dev,
                ),
            )
        except ValidationError as ex:
            log_malformed_package_warning(new_location, ex)
            continue
    return result


def parse_pipfile_deps(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages = []
    file_content = reader.read_closer.read()
    toml_content: IndexedDict[str, ParsedValue] = toml.parse_toml_with_tree_sitter(file_content)
    toml_packages = toml_content.get("packages")
    if not isinstance(toml_packages, IndexedDict):
        return [], []
    packages = _get_packages(reader, toml_packages)
    dev_deps = toml_content.get("dev-packages")
    if isinstance(dev_deps, IndexedDict):
        dev_pkgs = _get_packages(reader, dev_deps, is_dev=True)
        packages.extend(dev_pkgs)
    return packages, []
