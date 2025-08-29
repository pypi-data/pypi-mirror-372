import logging
from typing import NotRequired, TypedDict

from labels.config.cache import dual_cache
from labels.enrichers.api_interface import make_get

LOGGER = logging.getLogger(__name__)


class NPMPackageAuthor(TypedDict):
    email: str
    name: str


class NPMPackageDist(TypedDict):
    integrity: str
    tarball: str


class NPMPackageLicense(TypedDict):
    type: str
    url: str


class NPMPackageVersion(TypedDict):
    dist: NPMPackageDist
    name: str


class NPMPackageTimeUnpublished(TypedDict):
    time: str
    versions: list[str]


NPMPackage = TypedDict(
    "NPMPackage",
    {
        "author": NotRequired[str | NPMPackageAuthor],
        "dist-tags": NotRequired[dict[str, str]],
        "license": str | NPMPackageLicense,
        "name": str,
        "time": dict[str, str],
        "versions": dict[str, NPMPackageVersion],
    },
)


@dual_cache
def get_npm_package(package_name: str) -> NPMPackage | None:
    package: NPMPackage | None = make_get(f"https://registry.npmjs.org/{package_name}", timeout=30)

    if not package:
        return None

    if "unpublished" in package.get("time", {}):
        return None

    return package
