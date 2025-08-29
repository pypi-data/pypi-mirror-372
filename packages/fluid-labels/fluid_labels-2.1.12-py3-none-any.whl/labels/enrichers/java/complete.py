import logging
import threading
from datetime import UTC, datetime

from requests import exceptions
from urllib3.exceptions import MaxRetryError

from labels.enrichers.java.get import MavenPackageInfo, get_maven_package_info, search_maven_package
from labels.enrichers.utils import infer_algorithm
from labels.model.package import Artifact, Digest, HealthMetadata, Package
from labels.parsers.cataloger.java.model import JavaArchive
from labels.parsers.cataloger.java.package import group_id_from_java_metadata
from labels.utils.licenses.validation import validate_licenses
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)
stop_event = threading.Event()


def parse_package_name(combined: str) -> tuple[str | None, str | None]:
    parts = combined.split(":")
    if len(parts) == 1:
        return None, parts[0]
    return parts[0], parts[1]


def _get_health_metadata_artifact(
    current_package: MavenPackageInfo | None,
) -> Artifact | None:
    if current_package and current_package.jar_url:
        digest_value = current_package.hash or None
        return Artifact(
            url=current_package.jar_url,
            integrity=Digest(
                algorithm=infer_algorithm(digest_value),
                value=digest_value,
            ),
        )
    return None


def get_group_id(package: Package) -> str | None:
    if isinstance(package.metadata, JavaArchive) and (
        g_id := group_id_from_java_metadata(package.name, package.metadata)
    ):
        return g_id
    if package_candidate := search_maven_package(package.name, package.version):
        return package_candidate.group
    return None


def _set_health_metadata(
    package: Package,
    maven_package: MavenPackageInfo,
    current_package: MavenPackageInfo | None,
) -> None:
    authors = maven_package.authors or []
    package.health_metadata = HealthMetadata(
        latest_version=maven_package.latest_version,
        latest_version_created_at=datetime.fromtimestamp(maven_package.release_date, tz=UTC)
        if maven_package.release_date
        else None,
        authors=", ".join(authors) if authors else None,
        artifact=_get_health_metadata_artifact(current_package),
    )


def _set_licenses(package: Package, maven_package: MavenPackageInfo) -> None:
    maven_package_licenses = maven_package.licenses or []
    if maven_package_licenses:
        package.licenses = validate_licenses(
            [package_license for package_license in maven_package_licenses if package_license],
        )


def get_complete_package(
    package: Package,
    group_id: str,
    artifact_id: str,
) -> MavenPackageInfo | None:
    maven_package = get_maven_package_info(group_id, artifact_id)
    if not maven_package:
        if package_candidate := search_maven_package(package.name, package.version):
            maven_package = get_maven_package_info(package_candidate.group, artifact_id)
        if not maven_package:
            return None
    return maven_package


def complete_package(package: Package) -> Package:
    if stop_event.is_set():
        return package

    group_id, artifact_id = parse_package_name(package.name)

    try:
        group_id = group_id or get_group_id(package)
        if not group_id or not artifact_id:
            return package

        maven_package = get_complete_package(package, group_id, artifact_id)
        if not maven_package:
            return package

        current_package = get_maven_package_info(group_id, artifact_id, package.version)

        _set_health_metadata(package, maven_package, current_package)
        _set_licenses(package, maven_package)

    except (exceptions.ConnectionError, TimeoutError, MaxRetryError, exceptions.RetryError) as ex:
        LOGGER.warning(
            "Failed to connect to the package manager.",
            extra={"extra": {"exception": format_exception(str(ex))}},
        )
        stop_event.set()
    return package
