from contextlib import suppress
from datetime import datetime

from bs4 import BeautifulSoup, Tag

from labels.enrichers.alpine.get import get_package_versions_html
from labels.model.package import HealthMetadata, Package
from labels.parsers.cataloger.utils import extract_distro_info


def _get_latest_version_and_latest_version_created_at(
    package: Package,
    distro_version: str | None,
    arch: str | None,
) -> tuple[str, datetime | None] | tuple[None, None]:
    html_content = get_package_versions_html(package.name, distro_version, arch)
    if not html_content:
        return None, None

    parsed_content = BeautifulSoup(html_content, features="html.parser")
    version_items: list[Tag] = list(parsed_content.find_all("td", {"class": "version"}))

    if version_items:
        latest_version = version_items[0].text.strip()
        latest_version_created_at = None
        with suppress(IndexError):
            parent_tr = version_items[0].find_parent("tr")
            if parent_tr and (build_date_tag := parent_tr.find_next("td", {"class": "bdate"})):
                with suppress(ValueError):
                    latest_version_created_at = datetime.fromisoformat(build_date_tag.text.strip())
        return latest_version, latest_version_created_at

    return None, None


def _set_health_metadata(package: Package, arch: str | None, distro_version: str | None) -> None:
    authors = (
        package.metadata if package.metadata and hasattr(package.metadata, "maintainer") else None
    )
    (
        latest_version,
        latest_version_created_at,
    ) = _get_latest_version_and_latest_version_created_at(package, distro_version, arch)

    if not any([latest_version, latest_version_created_at, authors]):
        return

    package.health_metadata = HealthMetadata(
        latest_version=latest_version,
        latest_version_created_at=latest_version_created_at,
        authors=authors.maintainer if authors else None,
    )


def complete_package(
    package: Package,
) -> Package:
    _, distro_version, arch = extract_distro_info(package.p_url)
    _set_health_metadata(package, arch, distro_version)

    return package
