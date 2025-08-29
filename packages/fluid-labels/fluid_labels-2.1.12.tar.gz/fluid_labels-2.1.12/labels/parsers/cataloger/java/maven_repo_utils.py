from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

from labels.config.cache import dual_cache


def format_maven_pom_ulr(
    group_id: str,
    artifact_id: str,
    version: str,
    maven_base_url: str | None = None,
) -> str:
    maven_base_url = maven_base_url or "https://repo1.maven.org/maven2"
    artifact_pom = f"{artifact_id}-{version}.pom"
    path_components = [*group_id.split("."), artifact_id, version, artifact_pom]

    url = maven_base_url
    for component in path_components:
        url = urljoin(url + "/", component)

    return url


def get_pom_from_maven_repo(
    *,
    group_id: str,
    artifact_id: str,
    version: str,
    maven_base_url: str | None = None,
) -> BeautifulSoup | None:
    request_url = format_maven_pom_ulr(group_id, artifact_id, version, maven_base_url)
    request = dual_cache(requests.get)(request_url, timeout=30)
    if request.status_code != 200:
        return None

    pom_text = request.text
    return BeautifulSoup(pom_text, features="html.parser")


def get_dependency_version(
    dependency_management: Tag,
    group_id: str,
    artifact_id: str,
) -> str | None:
    """Retrieve specific dependency version from dependency management."""
    for dependency in dependency_management.find_all("dependency"):
        if (
            (dependency_groupid_node := dependency.find_next("groupid"))
            and (dependency_artifactid_node := dependency.find_next("artifactid"))
            and (dependency_version_node := dependency.find_next("version"))
            and dependency_groupid_node.get_text() == group_id
            and dependency_artifactid_node.get_text() == artifact_id
        ):
            return dependency_version_node.get_text()
    return None


def _get_text(parent: Tag | NavigableString, name: str) -> str | None:
    element = parent.find_next(name)
    if element:
        return element.get_text()
    return None


def get_parent_information(
    parent: Tag | NavigableString,
) -> tuple[str | None, str | None, str | None]:
    """Extract parent artifact information."""
    parent_group_id = _get_text(parent, "groupid")
    parent_artifact_id = _get_text(parent, "artifactid")
    parent_version = _get_text(parent, "version")
    return parent_group_id, parent_artifact_id, parent_version


def process_pom(
    parent_pom: Tag,
    group_id: str,
    artifact_id: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Process POM to either get the version or update parent details."""
    project = parent_pom.project
    if not project:
        return None, None, None, None

    dependency_management = project.find_next("dependencymanagement")
    if dependency_management and isinstance(dependency_management, Tag):
        version = get_dependency_version(dependency_management, group_id, artifact_id)
        if version:
            return version, None, None, None

    parent = project.find_next("parent")
    if parent:
        return None, *get_parent_information(parent)

    return None, None, None, None


def recursively_find_versions_from_parent_pom(  # noqa: PLR0913
    *,
    group_id: str,
    artifact_id: str,
    parent_group_id: str,
    parent_artifact_id: str,
    parent_version: str,
    maven_base_url: str | None = None,
) -> str | None:
    for _ in range(3):
        parent_pom = get_pom_from_maven_repo(
            group_id=parent_group_id,
            artifact_id=parent_artifact_id,
            version=parent_version,
            maven_base_url=maven_base_url,
        )
        if not parent_pom:
            break

        (
            version,
            new_parent_group_id,
            new_parent_artifact_id,
            new_parent_version,
        ) = process_pom(parent_pom, group_id, artifact_id)
        if version:
            return version
        if new_parent_group_id is None or not new_parent_artifact_id or not new_parent_version:
            break
        parent_group_id, parent_artifact_id, parent_version = (
            new_parent_group_id,
            new_parent_artifact_id,
            new_parent_version,
        )

    return None
