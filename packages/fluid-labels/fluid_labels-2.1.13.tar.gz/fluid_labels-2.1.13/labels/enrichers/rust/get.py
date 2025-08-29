from typing import TypedDict

import requests

from labels.config.cache import dual_cache

CRATES_ENDPOINT = "https://crates.io"


class Crate(TypedDict):
    max_stable_version: str
    updated_at: str


class Publisher(TypedDict):
    name: str


class Version(TypedDict):
    checksum: str
    dl_path: str
    license: str
    num: str
    published_by: Publisher


class CargoPackage(TypedDict):
    crate: Crate
    versions: list[Version]


@dual_cache
def get_cargo_package(package_name: str) -> CargoPackage | None:
    url = f"{CRATES_ENDPOINT}/api/v1/crates/{package_name}"
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        result: CargoPackage = response.json()
        return result

    return None
