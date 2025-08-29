from typing import TypedDict, cast

import requests

from labels.config.cache import dual_cache


class NugetCatalogEntry(TypedDict, total=False):
    authors: str
    created: str
    description: str
    id: str
    isPrerelease: bool
    lastEdited: str
    licenseExpression: str
    listed: bool
    packageHash: str
    packageHashAlgorithm: str
    packageSize: int
    projectUrl: str
    published: str
    requireLicenseAcceptance: bool
    title: str
    verbatimVersion: str
    version: str
    tags: list[str]


def _fetch_nuget_data(url: str) -> dict | None:
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        return None
    return response.json()


def _get_catalog_entry_from_items(items_list: list) -> dict | None:
    try:
        return next(x["catalogEntry"] for x in reversed(items_list) if "catalogEntry" in x)
    except StopIteration:
        try:
            return next(
                y["catalogEntry"]
                for x in reversed(items_list)
                for y in reversed(x.get("items", []))
                if "catalogEntry" in y and "pre" not in y["catalogEntry"].get("version", "")
            )
        except StopIteration:
            return None


def _get_package_data_for_version(package_name: str, version: str) -> dict | None:
    base_url = f"https://api.nuget.org/v3/registration5-gz-semver2/{package_name}/{version}.json"
    package_data = _fetch_nuget_data(base_url)
    if not package_data:
        return None

    catalog_url = package_data.get("catalogEntry")
    if not isinstance(catalog_url, str):
        return None

    return _fetch_nuget_data(catalog_url)


def _get_package_index(package_name: str) -> dict | None:
    base_url = f"https://api.nuget.org/v3/registration5-gz-semver2/{package_name}/index.json"
    return _fetch_nuget_data(base_url)


def _get_latest_version_group_url(package_index: dict) -> str | None:
    items = package_index.get("items")
    if not isinstance(items, list) or not items:
        return None

    last_item = items[-1]
    return last_item.get("@id") if isinstance(last_item.get("@id"), str) else None


def _get_version_group_items(items_url: str) -> list:
    items_response = _fetch_nuget_data(items_url)
    if not items_response:
        return []
    return items_response.get("items", [])


def _get_latest_package_data(package_name: str) -> dict | None:
    package_index = _get_package_index(package_name)
    if not package_index:
        return None

    items_url = _get_latest_version_group_url(package_index)
    if not items_url:
        return None

    items_list = _get_version_group_items(items_url)
    return _get_catalog_entry_from_items(items_list)


@dual_cache
def get_nuget_package(package_name: str, version: str | None = None) -> NugetCatalogEntry | None:
    if version:
        package_data = _get_package_data_for_version(package_name, version)
    else:
        package_data = _get_latest_package_data(package_name)

    if package_data is None:
        return None

    return cast("NugetCatalogEntry", package_data)
