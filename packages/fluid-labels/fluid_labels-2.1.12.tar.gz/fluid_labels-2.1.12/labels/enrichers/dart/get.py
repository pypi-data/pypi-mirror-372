from typing import NotRequired, TypedDict

from labels.enrichers.api_interface import make_get


class PubSpec(TypedDict):
    author: NotRequired[str]


class PubPackageVersion(TypedDict):
    archive_sha256: str
    archive_url: str
    published: str
    pubspec: PubSpec
    version: str


class PubPackage(TypedDict):
    latest: PubPackageVersion
    name: str
    versions: list[PubPackageVersion]


def get_pub_package(package_name: str) -> PubPackage | None:
    url = f"https://pub.dev/api/packages/{package_name}"
    return make_get(url, timeout=30, headers={"Accept": "gzip"})
