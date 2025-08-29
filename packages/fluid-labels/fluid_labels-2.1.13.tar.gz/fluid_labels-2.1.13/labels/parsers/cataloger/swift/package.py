import logging

from packageurl import PackageURL
from pydantic import BaseModel, ConfigDict, ValidationError

from labels.model.file import Location
from labels.model.indexables import ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.utils import log_malformed_package_warning

LOGGER = logging.getLogger(__name__)


class SwiftPackageManagerResolvedEntry(BaseModel):
    revision: str
    model_config = ConfigDict(frozen=True)


class CocoaPodfileLockEntry(BaseModel):
    checksum: str
    model_config = ConfigDict(frozen=True)


def is_stable_package_version(version: str) -> bool:
    unstable_identifiers = (
        "alpha",
        "beta",
        "rc",
        "next",
        "preview",
        "pre",
        "dev",
        "snapshot",
        "canary",
        "nightly",
    )

    return not any(identifier in version for identifier in unstable_identifiers)


def new_cocoa_pods_package(
    name: str,
    version: str,
    hash_: ParsedValue,
    location: Location,
) -> Package | None:
    if not isinstance(hash_, str):
        return None
    try:
        return Package(
            name=name,
            version=version,
            p_url=cocoapods_package_url(name, version),
            locations=[location],
            type=PackageType.CocoapodsPkg,
            language=Language.SWIFT,
            metadata=CocoaPodfileLockEntry(checksum=hash_),
            licenses=[],
        )
    except ValidationError as ex:
        log_malformed_package_warning(location, ex)
        return None


def new_swift_package_manager_package(
    *,
    name: str,
    version: str,
    source_url: ParsedValue | None,
    revision: ParsedValue | None,
    location: Location,
) -> Package | None:
    try:
        return Package(
            name=name,
            version=version,
            p_url=swift_package_manager_package_url(name, version, source_url),
            locations=[location],
            type=PackageType.SwiftPkg,
            language=Language.SWIFT,
            metadata=SwiftPackageManagerResolvedEntry(revision=revision)
            if revision and isinstance(revision, str)
            else None,
            licenses=[],
        )
    except ValidationError as ex:
        log_malformed_package_warning(location, ex)
        return None


def cocoapods_package_url(
    name: str,
    version: str,
) -> str:
    return PackageURL("cocoapods", "", name, version, None, "").to_string()  # type: ignore[misc]


def swift_package_manager_package_url(
    name: str,
    version: str,
    source_url: ParsedValue | None,
) -> str:
    return PackageURL(  # type: ignore[misc]
        "swift",
        source_url.replace("https://", "", 1) if source_url and isinstance(source_url, str) else "",
        name,
        version,
        None,
        "",
    ).to_string()
