from datetime import datetime

from packageurl import PackageURL
from pydantic import BaseModel, ValidationError

from labels.model.file import Location
from labels.model.package import Digest, Language, Package, PackageType
from labels.model.release import Release
from labels.parsers.cataloger.utils import (
    get_enriched_location,
    log_malformed_package_warning,
    purl_qualifiers,
)
from labels.utils.licenses.validation import validate_licenses


class AlpmFileRecord(BaseModel):
    path: str
    type: str | None = None
    uid: str | None = None
    gid: str | None = None
    time: datetime | None = None
    size: str | None = None
    link: str | None = None
    digests: list[Digest] | None = None


class AlpmDBEntry(BaseModel):
    licenses: str = ""
    base_package: str = ""
    package: str = ""
    version: str = ""
    description: str = ""
    architecture: str = ""
    size: int = 0
    packager: str = ""
    url: str = ""
    validation: str = ""
    reason: int = 0
    files: list[AlpmFileRecord] | None = None
    backup: list[AlpmFileRecord] | None = None


def package_url(entry: AlpmDBEntry, distro: Release | None = None) -> str:
    qualifiers = {"arch": entry.architecture}
    if entry.base_package:
        qualifiers["upstream"] = entry.base_package
    return PackageURL(
        type="alpm",
        name=entry.package,
        version=entry.version,
        qualifiers=purl_qualifiers(qualifiers, distro),  # type: ignore  # noqa: PGH003
        subpath="",
    ).to_string()


def new_package(
    entry: AlpmDBEntry,
    release: Release | None,
    db_location: Location,
) -> Package | None:
    name = entry.package
    version = entry.version

    if not name or not version:
        return None

    new_location = get_enriched_location(db_location)

    licenses_candidates = entry.licenses.split("\n")

    try:
        return Package(
            name=name,
            version=version,
            locations=[new_location],
            licenses=validate_licenses(licenses_candidates),
            type=PackageType.AlpmPkg,
            metadata=entry,
            p_url=package_url(entry, release),
            language=Language.UNKNOWN_LANGUAGE,
        )
    except ValidationError as ex:
        log_malformed_package_warning(new_location, ex)
        return None
