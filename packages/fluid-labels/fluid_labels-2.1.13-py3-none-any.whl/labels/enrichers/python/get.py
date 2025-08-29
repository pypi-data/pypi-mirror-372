from typing import NotRequired, TypedDict, cast

import requests

from labels.config.cache import dual_cache


class PyPIInfo(TypedDict):
    author: str
    author_email: str
    bugtrack_url: NotRequired[str]
    classifiers: list[str]
    description: str
    description_content_type: NotRequired[str]
    docs_url: NotRequired[str]
    download_url: NotRequired[str]
    downloads: dict[str, int]
    dynamic: NotRequired[str]
    home_page: NotRequired[str]
    keywords: NotRequired[str]
    license: str
    license_expression: NotRequired[str]
    license_files: NotRequired[str]
    maintainer: NotRequired[str]
    maintainer_email: NotRequired[str]
    name: str
    package_url: str
    platform: NotRequired[str]
    project_url: str
    project_urls: NotRequired[dict[str, str]]
    provides_extra: NotRequired[list[str]]
    release_url: str
    requires_dist: list[str]
    requires_python: str
    summary: str
    version: str
    yanked: bool
    yanked_reason: NotRequired[str]


class PyPIUrl(TypedDict):
    comment_text: str
    digests: dict[str, str]
    downloads: int
    filename: str
    has_sig: bool
    md5_digest: str
    packagetype: str
    python_version: str
    requires_python: str
    size: int
    upload_time: str
    upload_time_iso_8601: str
    url: str
    yanked: bool
    yanked_reason: NotRequired[str]


class PyPIResponse(TypedDict):
    info: PyPIInfo
    last_serial: int
    releases: dict[str, list[dict[str, object]]]
    urls: list[PyPIUrl]


@dual_cache
def get_pypi_package(package_name: str, version: str | None = None) -> PyPIResponse | None:
    url = f"https://pypi.org/pypi/{package_name}{'/' + version if version else ''}/json"
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        return cast("PyPIResponse", response.json())
    return None
