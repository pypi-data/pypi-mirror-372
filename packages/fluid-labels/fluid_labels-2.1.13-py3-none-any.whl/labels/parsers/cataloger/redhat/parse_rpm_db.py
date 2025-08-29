import logging
from itertools import zip_longest
from pathlib import Path
from typing import cast

from packageurl import PackageURL
from pydantic import BaseModel, ValidationError

from labels.model.file import Location, LocationReadCloser
from labels.model.package import Digest, Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment, Release
from labels.model.resolver import Resolver
from labels.parsers.cataloger.redhat.rpmdb import open_db
from labels.parsers.cataloger.redhat.rpmdb.package import PackageInfo
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning

LOGGER = logging.getLogger(__name__)


class RpmFileRecord(BaseModel):
    path: str
    mode: int
    size: int
    digest: Digest
    username: str
    group_name: str | None
    flags: str


class RpmDBEntry(BaseModel):
    id_: str
    name: str
    version: str
    epoch: int | None
    arch: str
    release: str
    source_rpm: str
    size: int
    vendor: str
    modularitylabel: str
    files: list[RpmFileRecord]


def package_url(  # noqa: PLR0913
    *,
    name: str,
    arch: str | None,
    epoch: int | None,
    source_rpm: str,
    version: str,
    release: str,
    distro: Release | None,
) -> str:
    namespace = ""
    if distro:
        namespace = distro.id_
    qualifiers: dict[str, str] = {}
    if arch:
        qualifiers["arch"] = arch
    if epoch:
        qualifiers["epoch"] = str(epoch)
    if source_rpm:
        qualifiers["upstream"] = source_rpm

    return PackageURL(
        type="rpm",
        namespace=namespace,
        name=name,
        version=f"{version}-{release}",
        qualifiers=qualifiers,
        subpath="",
    ).to_string()


def to_int(value: int | None, default: int = 0) -> int:
    return int(value) if isinstance(value, int) else default


def extract_rmp_file_records(resolver: Resolver, entry: PackageInfo) -> list[RpmFileRecord]:
    records: list[RpmFileRecord] = []
    file_attributes = cast(
        "tuple[tuple[str, int, str, int, int, int, str, str], ...]",
        zip_longest(
            entry.base_names,
            entry.dir_indexes,
            entry.file_digests,
            entry.file_flags,
            entry.file_modes,
            entry.file_sizes,
            entry.user_names,
            entry.group_names,
        ),
    )

    records.extend(
        record
        for attrs in file_attributes
        if (record := create_rpm_file_record(resolver, entry, attrs))
    )

    return records


def create_rpm_file_record(
    resolver: Resolver,
    entry: PackageInfo,
    attrs: tuple[str, int, str, int, int, int, str, str],
) -> RpmFileRecord | None:
    (
        base_name,
        dir_index,
        file_digest,
        file_flag,
        file_mode,
        file_size,
        file_username,
        file_groupname,
    ) = attrs

    if not base_name or not isinstance(dir_index, int):
        return None

    file_path = Path(str(entry.dir_names[dir_index]), str(base_name))
    file_location = resolver.files_by_path(str(file_path))

    if not file_location:
        return None

    return RpmFileRecord(
        path=str(file_path),
        mode=to_int(file_mode, default=0),
        size=to_int(file_size, default=0),
        digest=Digest(
            algorithm="md5" if file_digest else None,
            value=str(file_digest) if file_digest else None,
        ),
        username=str(file_username),
        flags=str(file_flag),
        group_name=str(file_groupname) if file_groupname else None,
    )


def new_redhat_package(
    *,
    entry: PackageInfo,
    resolver: Resolver,
    location: Location,
    env: Environment,
) -> Package | None:
    name = entry.name
    version = entry.version

    if not name or not version:
        return None

    metadata = RpmDBEntry(
        id_="",
        name=name,
        version=version,
        epoch=entry.epoch,
        arch=entry.arch,
        release=entry.release,
        source_rpm=entry.source_rpm,
        vendor=entry.vendor,
        size=entry.size,
        modularitylabel=entry.modularity_label,
        files=extract_rmp_file_records(resolver, entry),
    )

    new_location = get_enriched_location(location)

    try:
        return Package(
            name=name,
            version=version,
            locations=[new_location],
            language=Language.UNKNOWN_LANGUAGE,
            licenses=[entry.license],
            type=PackageType.RpmPkg,
            metadata=metadata,
            p_url=package_url(
                name=name,
                arch=entry.arch,
                epoch=entry.epoch,
                source_rpm=entry.source_rpm,
                version=version,
                release=entry.release,
                distro=env.linux_release,
            ),
        )
    except ValidationError as ex:
        log_malformed_package_warning(new_location, ex)
        return None


def parse_rpm_db(
    resolver: Resolver,
    env: Environment,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []

    if not reader.location.coordinates:
        return packages, []

    database = open_db(reader.location.coordinates.real_path)

    if not database:
        return packages, []

    for entry in database.list_packages():
        package = new_redhat_package(
            resolver=resolver,
            entry=entry,
            env=env,
            location=reader.location,
        )
        if package is not None:
            packages.append(package)
    return packages, []
