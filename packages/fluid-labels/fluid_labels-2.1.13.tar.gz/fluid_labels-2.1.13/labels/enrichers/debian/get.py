from typing import TypedDict

from labels.enrichers.api_interface import make_get


class DebianVersionInfo(TypedDict):
    area: str
    suites: list[str]
    version: str


class DebianPackageInfo(TypedDict):
    package: str
    path: str
    pathl: list[tuple[str, str]]
    suite: str
    type: str
    versions: list[DebianVersionInfo]


class StatInfo(TypedDict):
    perms: str
    size: int
    symlink_dest: str | None
    type: str


class ContentItem(TypedDict):
    hidden: bool
    name: str
    percent_encoded_name: str
    stat: StatInfo
    type: str


class MetricInfo(TypedDict):
    size: int


class PkgInfos(TypedDict):
    area: str
    copyright: bool
    ctags_count: int
    license: str
    metric: MetricInfo
    pts_link: str
    sloc: list[tuple[str, int]]
    suites: list[str]
    vcs_browser: str
    vcs_type: str


class DebianDirectoryInfo(TypedDict):
    content: list[ContentItem]
    directory: str
    package: str
    path: str
    pkg_infos: PkgInfos
    type: str
    version: str


def get_deb_package_version_list(
    package_name: str,
) -> list[DebianVersionInfo] | None:
    package_info: DebianPackageInfo | None = make_get(
        f"https://sources.debian.org/api/src/{package_name}/",
    )
    if not package_info or "error" in package_info:
        return None
    return package_info["versions"]


def get_deb_package(package_name: str, version: str) -> DebianDirectoryInfo | None:
    package_info: DebianDirectoryInfo | None = make_get(
        f"https://sources.debian.org/api/src/{package_name}/{version}/",
    )
    if not package_info:
        return None

    return package_info


def get_deb_snapshot(package_name: str, version: str) -> str | None:
    url = f"https://snapshot.debian.org/package/{package_name}/{version}/"
    result = make_get(
        url,
        content=True,
    )
    if not result or not isinstance(result, str):
        return None
    return result
