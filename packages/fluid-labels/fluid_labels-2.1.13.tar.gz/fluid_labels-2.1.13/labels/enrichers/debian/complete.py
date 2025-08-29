import logging

from bs4 import BeautifulSoup, Tag

from labels.enrichers.debian.get import (
    DebianVersionInfo,
    get_deb_package_version_list,
    get_deb_snapshot,
)
from labels.enrichers.utils import infer_algorithm
from labels.model.package import Artifact, Digest, HealthMetadata, Package
from labels.parsers.cataloger.utils import extract_distro_info

LOGGER = logging.getLogger(__name__)


def is_stable_debian_version(version: str) -> bool:
    unstable_indicators = (
        "~rc",
        "~beta",
        "~alpha",
        "~dev",
        "~exp",  # Pre-release versions
        "+exp",  # Pre-release versions
        "+git",
        "~bpo",
        "~sid",  # Backports and sid/unstable
        "+nmu",  # Non-maintainer uploads
        "+next",
        "experimental",
        "testing",  # Explicit unstable/testing markers
    )

    return not any(indicator in version.lower() for indicator in unstable_indicators)


def get_tag_values(tag: Tag) -> tuple[str | list[str] | None, str | None]:
    tag_href: str | list[str] | None = None
    sha1_hash: str | None = None

    tag_href = tag.get("href")
    code_tag = tag.find_previous("code")
    if code_tag is not None:
        sha1_hash = code_tag.text
    return tag_href, sha1_hash


def _search_download_url(
    package: Package,
    arch: str | None = None,
) -> tuple[str, str | None] | None:
    html_download = get_deb_snapshot(package.name, package.version)
    if not html_download:
        return None
    parsed = BeautifulSoup(html_download, features="html.parser")
    tags: list[Tag] = parsed.find_all("a", href=True)
    tag_href: str | list[str] | None = None
    for tag in tags:
        if (
            tag.text.endswith(".deb")
            and package.name in tag.text
            and package.version in tag.text
            and (arch in tag.text if arch else True)
        ):
            tag_href, sha1_hash = get_tag_values(tag)
            break
    else:
        for tag in tags:
            if (
                tag.text.endswith(".deb")
                and package.name in tag.text
                and package.version in tag.text
            ):
                tag_href, sha1_hash = get_tag_values(tag)
                break
    if not tag_href:
        return None

    return f"https://snapshot.debian.org{tag_href}", sha1_hash


def _get_artifact(package: Package, arch: str | None) -> Artifact | None:
    download_url_item = _search_download_url(package, arch)
    if download_url_item:
        digest_value = download_url_item[1] or None
        return Artifact(
            url=download_url_item[0],
            integrity=Digest(
                algorithm=infer_algorithm(digest_value),
                value=digest_value,
            ),
        )
    return None


def _set_health_metadata(
    package: Package,
    versions_list: list[DebianVersionInfo] | None,
    arch: str | None,
) -> None:
    latest_version = None
    if versions_list:
        latest_version = next(
            (
                release["version"]
                for release in versions_list
                if is_stable_debian_version(release["version"])
            ),
            versions_list[0]["version"],
        )
    authors = package.metadata if hasattr(package.metadata, "maintainer") else None
    artifact = _get_artifact(package, arch)

    if not any([latest_version, authors, artifact]):
        return

    package.health_metadata = HealthMetadata(
        latest_version=latest_version,
        authors=authors.maintainer if authors else None,
        artifact=artifact,
    )


def complete_package(
    package: Package,
) -> Package:
    _, _, arch = extract_distro_info(package.p_url)
    versions_list = get_deb_package_version_list(package.name)
    _set_health_metadata(package, versions_list, arch)

    return package
