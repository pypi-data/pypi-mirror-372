import logging
from datetime import datetime
from typing import Any
from xml.etree import ElementTree as ET

from defusedxml import ElementTree
from pydantic import BaseModel, ConfigDict

from labels.enrichers.api_interface import make_get

LOGGER = logging.getLogger(__name__)


class MavenSearchDocResponse(BaseModel):
    id_: str
    group: str
    artifact: str
    version: str
    timestamp: int
    extra_classifiers: list[str]
    packaging: str | None = None
    tags: list[str] | None = None
    model_config = ConfigDict(frozen=True)


class AuthorsLicenses(BaseModel):
    authors: list[str]
    licenses: list[str]
    model_config = ConfigDict(frozen=True)


class MavenPackageInfo(BaseModel):
    group_id: str
    artifact_id: str
    latest_version: str | None = None
    release_date: int | None = None
    authors: list[str] | None = None
    licenses: list[str] | None = None
    version: str | None = None
    jar_url: str | None = None
    hash: str | None = None
    model_config = ConfigDict(frozen=True)


def build_maven_search_url(
    artifact_id: str,
    version: str | None,
) -> tuple[str, dict[str, str | int]]:
    base_url = "https://central.sonatype.com/solrsearch/select"
    query = f"a:{artifact_id} AND v:{version}" if version else f"a:{artifact_id}"
    params: dict[str, str | int] = {"q": query, "rows": 5, "wt": "json"}
    return base_url, params


def parse_maven_search_response(
    docs: list[dict[str, Any]],
    artifact_id: str,
    version: str,
) -> MavenSearchDocResponse | None:
    try:
        return MavenSearchDocResponse(
            id_=docs[0]["id"],
            group=docs[0]["g"],
            artifact=docs[0]["a"],
            version=docs[0]["v"] if "v" in docs[0] else docs[0]["latestVersion"],
            packaging=docs[0].get("p", None),
            timestamp=int(docs[0]["timestamp"] // 1000),
            extra_classifiers=docs[0]["ec"],
            tags=docs[0].get("tags", None),
        )
    except KeyError as exc:
        LOGGER.exception(
            "Error parsing Maven search response",
            extra={
                "extra": {
                    "artifact_id": artifact_id,
                    "version": version,
                    "doc": docs[0],
                    "key": exc.args[0],
                },
            },
        )
        return None


def search_maven_package(artifact_id: str, version: str) -> MavenSearchDocResponse | None:
    base_url, params = build_maven_search_url(artifact_id, version)
    package_data = make_get(base_url, params=params, timeout=30)
    if not package_data:
        return None

    docs = package_data["response"].get("docs", [])
    if not docs or len(docs) > 1:
        return None

    return parse_maven_search_response(docs, artifact_id, version)


def build_maven_urls(group_id: str, artifact_id: str, version: str) -> tuple[str, str, str]:
    group_id_path = group_id.replace(".", "/")
    base_path = f"https://repo1.maven.org/maven2/{group_id_path}/{artifact_id}/{version}"
    pom_url = f"{base_path}/{artifact_id}-{version}.pom"
    jar_url = f"{base_path}/{artifact_id}-{version}.jar"
    hash_url = f"{base_path}/{artifact_id}-{version}.jar.sha1"
    return pom_url, jar_url, hash_url


def get_package_hash(hash_url: str) -> str:
    hash_response: str | None = make_get(hash_url, content=True, timeout=30)
    return hash_response.strip() if hash_response else "Hash not available"


def parse_pom_xml(pom_content: str) -> ET.Element:
    return ElementTree.fromstring(pom_content)


def extract_authors_licenses(pom_xml: ET.Element) -> AuthorsLicenses:
    namespace = {"m": "http://maven.apache.org/POM/4.0.0"}
    authors = [
        author.text
        for author in pom_xml.findall("m:developers/m:developer/m:name", namespace)
        if author.text
    ]
    licenses = [
        getattr(package_license.find("m:name", namespace), "text", "")
        for package_license in pom_xml.findall("m:licenses/m:license", namespace)
    ]
    return AuthorsLicenses(authors=authors, licenses=licenses)


def get_authors_licenses(group_id: str, artifact_id: str, version: str) -> AuthorsLicenses | None:
    pom_url, _, _ = build_maven_urls(group_id, artifact_id, version)
    response = make_get(pom_url, content=True, timeout=30)
    if not response:
        return None

    pom_xml = parse_pom_xml(response)
    return extract_authors_licenses(pom_xml)


def parse_metadata_xml(metadata_content: str) -> tuple[str | None, int | None]:
    metadata_xml = ElementTree.fromstring(metadata_content)
    latest_stable_version = metadata_xml.find("versioning/release")
    release_date_tag = metadata_xml.find("versioning/lastUpdated")

    release_date: int | None = None
    if release_date_tag is not None and release_date_tag.text:
        release_date = int(
            datetime.strptime(release_date_tag.text + "+0000", "%Y%m%d%H%M%S%z").timestamp(),
        )

    return (
        latest_stable_version.text if latest_stable_version is not None else None,
        release_date,
    )


def build_metadata_url(group_id: str, artifact_id: str) -> str:
    group_id_path = group_id.replace(".", "/")
    return f"https://repo1.maven.org/maven2/{group_id_path}/{artifact_id}/maven-metadata.xml"


def get_maven_metadata(group_id: str, artifact_id: str) -> tuple[str | None, int | None]:
    metadata_url = build_metadata_url(group_id, artifact_id)
    response = make_get(metadata_url, content=True, timeout=30)
    if not response:
        return None, None

    return parse_metadata_xml(response)


def get_specific_version_info(
    group_id: str,
    artifact_id: str,
    version: str,
) -> MavenPackageInfo | None:
    pom_url, jar_url, hash_url = build_maven_urls(group_id, artifact_id, version)
    response = make_get(pom_url, timeout=30, content=True)
    if not response:
        return None

    package_hash = get_package_hash(hash_url)

    return MavenPackageInfo(
        group_id=group_id,
        artifact_id=artifact_id,
        version=version,
        jar_url=jar_url,
        hash=package_hash,
    )


def get_latest_version_info(group_id: str, artifact_id: str) -> MavenPackageInfo | None:
    latest_version, release_date = get_maven_metadata(group_id, artifact_id)
    if not latest_version:
        return None

    authors_licenses = get_authors_licenses(group_id, artifact_id, latest_version)

    return MavenPackageInfo(
        group_id=group_id,
        artifact_id=artifact_id,
        latest_version=latest_version,
        release_date=release_date,
        authors=authors_licenses.authors if authors_licenses else None,
        licenses=authors_licenses.licenses if authors_licenses else None,
    )


def get_maven_package_info(
    group_id: str,
    artifact_id: str,
    version: str | None = None,
) -> MavenPackageInfo | None:
    if version:
        return get_specific_version_info(group_id, artifact_id, version)
    return get_latest_version_info(group_id, artifact_id)
