from typing import TypedDict

from labels.enrichers.api_interface import make_get


class OriginInfo(TypedDict):
    VCS: str
    URL: str
    Ref: str
    Hash: str


class VersionInfo(TypedDict):
    Version: str
    Time: str
    Origin: OriginInfo | None


class LicenseLinks(TypedDict):
    self: str
    git: str
    html: str


class LicenseInfo(TypedDict):
    key: str
    name: str
    spdx_id: str
    url: str | None
    node_id: str


class LicenseData(TypedDict):
    name: str
    path: str
    sha: str
    size: int
    url: str
    html_url: str
    git_url: str
    download_url: str
    type: str
    content: str
    encoding: str
    _links: LicenseLinks
    license: LicenseInfo


def fetch_license_info(repo_path: str) -> LicenseData | None:
    base_url = "https://api.github.com/repos"
    url = f"{base_url}/{repo_path}/license"

    response: LicenseData | None = make_get(url)
    return response


def fetch_latest_version_info(module_path: str) -> VersionInfo | None:
    # https://go.dev/ref/mod#version-queries
    base_url = "https://proxy.golang.org"
    url = f"{base_url}/{module_path.lower()}/@latest"

    response: VersionInfo | None = make_get(url)
    return response
