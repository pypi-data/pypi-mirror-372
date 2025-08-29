from typing import NotRequired, TypedDict

import requests

from labels.config.cache import dual_cache


class Author(TypedDict):
    name: str
    homepage: str
    email: NotRequired[str]


class Source(TypedDict):
    url: str
    type: str
    reference: str


class Dist(TypedDict):
    url: str
    type: str
    shasum: str
    reference: str


class PackagistPackageInfo(TypedDict, total=False):
    name: str
    description: str
    keywords: list[str]
    homepage: str
    version: str
    version_normalized: str
    license: list[str]
    authors: list[Author]
    source: Source
    dist: Dist
    type: str
    support: dict[str, str]
    funding: list[str]
    time: str
    autoload: dict[str, list[str]]
    extra: dict[str, dict[str, str]]
    require: dict[str, str]
    require_dev: dict[str, str]
    suggest: dict[str, str]
    conflict: dict[str, str]


class PackagistResponse(TypedDict, total=False):
    minified: str
    packages: dict[str, list[PackagistPackageInfo]]


def get_package_data(
    package_name: str,
    base_url: str = "https://repo.packagist.org",
) -> PackagistResponse | None:
    url = f"{base_url}/p2/{package_name}.json"
    response = requests.get(url, timeout=30)

    if response.status_code == 200:
        return response.json()
    return None


def find_version(
    package_versions: list[PackagistPackageInfo],
    version: str | None,
) -> PackagistPackageInfo | None:
    if not version:
        return package_versions[0] if package_versions else None

    return next(
        (
            version_data
            for version_data in package_versions
            if version_data.get("version") == version
        ),
        None,
    )


@dual_cache
def get_composer_package(
    package_name: str,
    version: str | None = None,
) -> PackagistPackageInfo | None:
    response_data = get_package_data(package_name)
    if not response_data:
        return None

    package_versions = response_data.get("packages", {}).get(package_name, [])
    return find_version(package_versions, version)
