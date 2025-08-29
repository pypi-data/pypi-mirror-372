import json
import logging
from pathlib import Path

from pydantic import ValidationError

from labels.model.file import Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.python.model import PythonDirectURLOriginInfo, PythonFileRecord
from labels.parsers.cataloger.python.parse_wheel_egg_metadata import (
    ParsedData,
    parse_wheel_or_egg_metadata,
)
from labels.parsers.cataloger.python.parse_wheel_egg_record import (
    parse_installed_files,
    parse_wheel_or_egg_record,
)
from labels.parsers.cataloger.python.utils import package_url
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning
from labels.utils.strings import normalize_name

LOGGER = logging.getLogger(__name__)


def fetch_record_files(
    resolver: Resolver,
    metadata_location: Location,
) -> tuple[list[PythonFileRecord] | None, list[Location] | None]:
    files: list[PythonFileRecord] = []
    sources: list[Location] = []
    if not metadata_location.coordinates:
        return None, None

    record_path = Path(metadata_location.coordinates.real_path).parent / "RECORD"
    record_ref: Location | None = resolver.relative_file_path(metadata_location, str(record_path))
    if not record_ref:
        return None, None
    sources.append(record_ref)
    record_content = resolver.file_contents_by_location(record_ref)
    if not record_content:
        return None, None
    records = parse_wheel_or_egg_record(record_content)
    files.extend(records)
    return files, sources


def fetch_installed_packages(
    resolver: Resolver,
    metadata_location: Location,
    site_packages_root_path: str,
) -> tuple[list[PythonFileRecord] | None, list[Location] | None]:
    files: list[PythonFileRecord] = []
    sources: list[Location] = []

    if not metadata_location.coordinates:
        return None, None

    installed_files_path = Path(metadata_location.coordinates.real_path, "installed-files.txt")

    installed_files_ref = resolver.relative_file_path(metadata_location, str(installed_files_path))

    if installed_files_ref:
        sources.append(installed_files_ref)
        installed_files_content = resolver.file_contents_by_location(installed_files_ref)
        if not installed_files_content:
            return None, None

        installed_files = parse_installed_files(
            installed_files_content,
            str(installed_files_path),
            site_packages_root_path,
        )

        files.extend(installed_files)
    return files, sources


def fetch_top_level_packages(
    resolver: Resolver,
    metadata_location: Location,
) -> tuple[list[str] | None, list[Location] | None]:
    pkgs: list[str] = []
    if not metadata_location.coordinates:
        return None, None
    parent_dir = Path(metadata_location.coordinates.real_path).parent
    top_level_path = parent_dir / "top_level.txt"
    top_level_location = resolver.relative_file_path(metadata_location, str(top_level_path))
    if not top_level_location:
        return None, None

    sources = [top_level_location]
    top_level_content = resolver.file_contents_by_location(top_level_location)
    if not top_level_content:
        return None, None

    pkgs.extend(line.rstrip("\n") for line in top_level_content.readlines())

    return pkgs, sources


def fetch_direct_url_data(
    resolver: Resolver,
    metadata_location: Location,
) -> tuple[PythonDirectURLOriginInfo | None, list[Location] | None]:
    if not metadata_location.coordinates:
        return None, None
    direct_url_path = Path(metadata_location.coordinates.real_path, "direct_url.json")
    direct_url_location = resolver.relative_file_path(metadata_location, str(direct_url_path))
    if not direct_url_location:
        return None, None

    sources = [direct_url_location]
    direct_url_content = resolver.file_contents_by_location(direct_url_location)
    if not direct_url_content:
        return None, None
    decoded_dat = json.load(direct_url_content)
    return (
        PythonDirectURLOriginInfo(
            url=decoded_dat["url"],
            commit_id=decoded_dat["vcs_info"]["commit_id"],
            vcs=decoded_dat["vcs_info"]["vcs"],
        ),
        sources,
    )


def assemble_egg_or_wheel_metadata(
    resolver: Resolver,
    metadata_location: Location,
) -> tuple[ParsedData | None, list[Location] | None]:
    sources_r = [metadata_location]
    sources: list[Location] | None = None
    metadata_content = resolver.file_contents_by_location(metadata_location)
    if not metadata_content or not metadata_location.coordinates:
        return None, None
    p_data = parse_wheel_or_egg_metadata(metadata_location.coordinates.real_path, metadata_content)
    if not p_data:
        return None, None
    records, sources = fetch_record_files(resolver, metadata_location)
    if not records or not sources:
        records, sources = fetch_installed_packages(
            resolver,
            metadata_location,
            p_data.python_package.site_package_root_path or "",
        )
    if sources:
        sources_r.extend(sources or [])
    p_data.python_package.files = records

    top_packages, sources = fetch_top_level_packages(resolver, metadata_location)
    sources_r.extend(sources or [])
    p_data.python_package.top_level_packages = top_packages
    direct_url, sources = fetch_direct_url_data(resolver, metadata_location)

    if direct_url and sources_r:
        sources_r.extend(sources or [])
        p_data.python_package.direct_url_origin = direct_url

    return p_data, sources_r


def new_package_from_python_package(
    data: ParsedData,
    location: Location,
) -> Package | None:
    name = data.python_package.name
    version = data.python_package.version

    if not name or not version:
        return None

    normalized_name = normalize_name(name, PackageType.PythonPkg)
    purl = package_url(normalized_name, version, data.python_package)
    new_location = get_enriched_location(location)

    try:
        return Package(
            name=normalized_name,
            version=version,
            p_url=purl,
            locations=[new_location],
            language=Language.PYTHON,
            type=PackageType.PythonPkg,
            metadata=data.python_package,
            licenses=[],
        )
    except ValidationError as ex:
        log_malformed_package_warning(new_location, ex)
        return None


def parse_wheel_or_egg(
    resolver: Resolver,
    _: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    p_data, _sources = assemble_egg_or_wheel_metadata(resolver, reader.location)
    if not p_data:
        return [], []

    pkg = new_package_from_python_package(p_data, reader.location)

    return [pkg] if pkg is not None else [], []
