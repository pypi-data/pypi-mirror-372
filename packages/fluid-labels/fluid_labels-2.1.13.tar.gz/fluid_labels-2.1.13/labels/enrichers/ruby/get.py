from typing import NotRequired, TypedDict, cast

import requests

from labels.config.cache import dual_cache


class RubyGemsMetadata(TypedDict, total=False):
    homepage_uri: str
    changelog_uri: str
    bug_tracker_uri: str
    source_code_uri: str
    documentation_uri: str


class RubyGemsDependencies(TypedDict):
    development: list[str]
    runtime: list[str]


class RubyGemsPackage(TypedDict, total=False):
    name: str
    downloads: int
    version: str
    version_created_at: str
    version_downloads: int
    platform: str
    authors: str
    info: str
    licenses: list[str]
    metadata: RubyGemsMetadata
    yanked: bool
    sha: str
    spec_sha: str
    project_uri: str
    gem_uri: str
    homepage_uri: str
    wiki_uri: NotRequired[str]
    documentation_uri: str
    mailing_list_uri: NotRequired[str]
    source_code_uri: str
    bug_tracker_uri: str
    changelog_uri: str
    funding_uri: NotRequired[str]
    dependencies: RubyGemsDependencies
    built_at: NotRequired[str]
    created_at: NotRequired[str]
    description: NotRequired[str]
    downloads_count: NotRequired[int]
    number: NotRequired[str]
    summary: NotRequired[str]
    rubygems_version: NotRequired[str]
    ruby_version: NotRequired[str]
    prerelease: NotRequired[bool]
    requirements: NotRequired[list[str]]


@dual_cache
def get_gem_package(package_name: str, version: str | None = None) -> RubyGemsPackage | None:
    if version:
        url = f"https://rubygems.org/api/v2/rubygems/{package_name}/versions/{version}.json"
    else:
        url = f"https://rubygems.org/api/v1/gems/{package_name}.json"

    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        return cast("RubyGemsPackage", response.json())
    return None
