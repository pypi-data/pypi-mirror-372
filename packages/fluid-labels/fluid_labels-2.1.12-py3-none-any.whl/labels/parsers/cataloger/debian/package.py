import logging
from copy import deepcopy
from pathlib import Path
from typing import TextIO, cast

from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import Location
from labels.model.package import Language, Package, PackageType
from labels.model.release import Release
from labels.model.resolver import Resolver
from labels.parsers.cataloger.debian.model import DpkgDBEntry, DpkgFileRecord
from labels.parsers.cataloger.debian.parse_copyright import parse_licenses_from_copyright
from labels.parsers.cataloger.debian.parse_dpkg_info_files import (
    parse_dpkg_conffile_info,
    parse_dpkg_md5_info,
)
from labels.parsers.cataloger.utils import (
    get_enriched_location,
    log_malformed_package_warning,
    purl_qualifiers,
)
from labels.utils.licenses.validation import validate_licenses

LOGGER = logging.getLogger(__name__)


def package_url(pkg: DpkgDBEntry, distro: Release | None = None) -> str:
    qualifiers = {"arch": pkg.architecture}
    if distro and (distro.id_ == "debian" or "debian" in (distro.id_like or [])):
        if distro.version_id:
            qualifiers["distro_version_id"] = distro.version_id
        qualifiers["distro_id"] = distro.id_
    if pkg.source:
        qualifiers["upstream"] = (
            f"{pkg.source}@{pkg.source_version}" if pkg.source_version else pkg.source
        )

    return PackageURL(
        type="deb",
        namespace=distro.id_ if distro and distro.id_ else "",
        name=pkg.package,
        version=pkg.version,
        qualifiers=purl_qualifiers(qualifiers, distro),
        subpath="",
    ).to_string()


def md5_key(metadata: DpkgDBEntry) -> str:
    content_key = metadata.package
    if metadata.architecture not in ("", "all"):
        return f"{content_key}:{metadata.architecture}"
    return content_key


def fetch_md5_content(
    resolver: Resolver,
    db_location: Location,
    entry: DpkgDBEntry,
) -> tuple[TextIO | None, Location | None] | None:
    if not db_location.coordinates:
        return None
    search_path = Path(db_location.coordinates.real_path).parent
    if not str(search_path).endswith("status.d"):
        search_path = search_path / "info"
    name = md5_key(entry)
    md5_file = name + ".md5sums"
    location = resolver.relative_file_path(
        db_location,
        str(search_path / md5_file),
    )
    if not location:
        md5_file = entry.package + ".md5sums"
        location = resolver.relative_file_path(
            db_location,
            str(search_path / md5_file),
        )
    if not location:
        return None

    reader = resolver.file_contents_by_location(location)
    if not reader:
        LOGGER.warning(
            "failed to fetch deb md5 contents (package=%s)",
            entry.package,
        )
    return reader, location


def fetch_conffile_contents(
    resolver: Resolver,
    db_location: Location,
    entry: DpkgDBEntry,
) -> tuple[TextIO | None, Location | None] | None:
    if not db_location.coordinates:
        return None
    parent_path = Path(db_location.coordinates.real_path).parent

    name = md5_key(entry)
    md5_file = name + ".conffiles"
    location = resolver.relative_file_path(
        db_location,
        str(parent_path.joinpath("info", md5_file)),
    )
    if not location:
        md5_file = entry.package + ".conffiles"
        location = resolver.relative_file_path(
            db_location,
            str(parent_path.joinpath("info", md5_file)),
        )
    if not location:
        return None, None
    reader = resolver.file_contents_by_location(location)
    if not reader:
        LOGGER.warning(
            "failed to fetch deb conffiles contents (package=%s)",
            entry.package,
        )
    return reader, location


def get_additional_file_listing(
    resolver: Resolver,
    db_location: Location,
    entry: DpkgDBEntry,
) -> tuple[list[DpkgFileRecord], list[Location]]:
    files: list[DpkgFileRecord] = []
    locations: list[Location] = []
    md5_result = fetch_md5_content(resolver, db_location, entry)
    if not md5_result:
        return files, locations
    md5_reader, md5_location = md5_result
    if md5_reader is not None and md5_location is not None:
        files.extend(parse_dpkg_md5_info(md5_reader))
        locations.append(md5_location)
    conffiles = fetch_conffile_contents(resolver, db_location, entry)
    if not conffiles:
        return files, locations
    conffiles_reader, conffiles_location = conffiles

    if conffiles_reader is not None and conffiles_location is not None:
        files.extend(parse_dpkg_conffile_info(conffiles_reader))
        locations.append(conffiles_location)

    return files, locations


def merge_file_listing(resolver: Resolver, db_location: Location, pkg: Package) -> None:
    metadata: DpkgDBEntry = cast("DpkgDBEntry", pkg.metadata)
    files, info_locations = get_additional_file_listing(resolver, db_location, metadata)

    if metadata.files is None:
        metadata.files = []

    for new_file in files:
        exists = False
        for existing_file in metadata.files:
            if existing_file.path == new_file.path:
                exists = True
                break
        if not exists:
            metadata.files.append(new_file)

    metadata.files = sorted(metadata.files, key=lambda x: x.path)
    pkg.metadata = metadata
    pkg.locations.extend(info_locations)


def fetch_copyright_contents(
    resolver: Resolver | None,
    db_location: Location,
    metadata: DpkgDBEntry,
) -> tuple[TextIO | None, Location | None]:
    if not resolver:
        return None, None

    copyright_path = Path("/usr/share/doc").joinpath(metadata.package, "copyright")
    location = resolver.relative_file_path(db_location, str(copyright_path))

    if not location:
        return None, None

    reader = resolver.file_contents_by_location(location)
    if not reader:
        LOGGER.warning(
            "Failed to fetch deb copyright contents (package=%s)",
            metadata.package,
        )

    return reader, location


def add_licenses(resolver: Resolver, db_location: Location, pkg: Package) -> None:
    metadata: DpkgDBEntry = cast("DpkgDBEntry", pkg.metadata)

    pkg.licenses = []
    copyright_reader, copyright_location = fetch_copyright_contents(resolver, db_location, metadata)

    if copyright_reader is not None and copyright_location is not None:
        licenses_strs = parse_licenses_from_copyright(copyright_reader)
        pkg.licenses = validate_licenses(licenses_strs)


def new_dpkg_package(
    entry: DpkgDBEntry,
    db_location: Location,
    _resolver: Resolver | None,
    release: Release | None = None,
) -> Package | tuple[Package, Package] | None:
    name = entry.package
    version = entry.version

    if not name or not version:
        return None

    new_location = get_enriched_location(db_location)

    try:
        dpkg = Package(
            name=name,
            version=version,
            licenses=[],
            p_url=package_url(entry, release),
            locations=[new_location],
            type=PackageType.DebPkg,
            metadata=entry,
            found_by=None,
            language=Language.UNKNOWN_LANGUAGE,
        )
        if _resolver is not None:
            # side effects
            merge_file_listing(_resolver, db_location, dpkg)
            add_licenses(_resolver, db_location, dpkg)

        source_dpkg: Package | None = None
        if (entry.source and entry.source != dpkg.name) or (
            entry.source and entry.source_version and entry.source_version != dpkg.version
        ):
            new_entry = deepcopy(entry)
            new_entry.package = entry.source
            new_entry.version = entry.source_version or dpkg.version
            new_entry.source = None
            new_entry.source_version = None
            new_entry.dependencies = None
            new_entry.pre_dependencies = None

            source_dpkg = deepcopy(dpkg)
            source_dpkg.name = new_entry.package
            source_dpkg.version = new_entry.version
            source_dpkg.p_url = package_url(new_entry, release)
    except ValidationError as ex:
        log_malformed_package_warning(new_location, ex)
        return None
    else:
        if source_dpkg:
            return dpkg, source_dpkg
        return dpkg
