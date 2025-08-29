from typing import TypedDict

from labels.enrichers.api_interface import make_get


class Release(TypedDict):
    version: str
    url: str
    inserted_at: str
    has_docs: bool


class Owner(TypedDict):
    url: str
    email: str
    username: str


class Downloads(TypedDict):
    all: int
    day: int
    recent: int
    week: int


class Meta(TypedDict):
    links: dict[str, str]
    description: str
    licenses: list[str]
    maintainers: list[str]


class Configs(TypedDict):
    erlang_mk: str
    mix_exs: str
    rebar_config: str


class PackageData(TypedDict):
    meta: Meta
    name: str
    url: str
    owners: list[Owner]
    inserted_at: str
    updated_at: str
    repository: str
    releases: list[Release]
    downloads: Downloads
    latest_version: str
    docs_html_url: str
    retirements: dict[str, str]
    configs: Configs
    html_url: str
    latest_stable_version: str


def get_hex_package(package_name: str) -> PackageData | None:
    url = f"https://hex.pm/api/packages/{package_name}"
    return make_get(url, timeout=30, headers={"Accept": "application/json"})
