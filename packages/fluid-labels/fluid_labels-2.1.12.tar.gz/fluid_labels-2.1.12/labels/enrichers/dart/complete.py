from labels.enrichers.dart.get import PubPackage, PubPackageVersion, get_pub_package
from labels.enrichers.utils import infer_algorithm
from labels.model.package import Artifact, Digest, HealthMetadata, Package


def _get_current_package(pub_package: PubPackage, version: str) -> PubPackageVersion | None:
    return next((v for v in pub_package["versions"] if v["version"] == version), None)


def _get_authors(pub_package: PubPackage) -> str | None:
    return next(
        (
            version["pubspec"]["author"]
            for version in reversed(pub_package["versions"])
            if "author" in version["pubspec"]
        ),
        None,
    )


def _get_artifact(current_package: PubPackageVersion) -> Artifact:
    digest_value = current_package["archive_sha256"]
    return Artifact(
        url=current_package["archive_url"],
        integrity=Digest(
            value=digest_value,
            algorithm=infer_algorithm(digest_value),
        ),
    )


def _set_health_metadata(
    package: Package,
    pub_package: PubPackage,
    current_package: PubPackageVersion | None,
) -> None:
    package.health_metadata = HealthMetadata(
        latest_version=pub_package["latest"]["version"],
        latest_version_created_at=pub_package["latest"]["published"],
        authors=_get_authors(pub_package),
        artifact=_get_artifact(current_package) if current_package else None,
    )


def complete_package(package: Package) -> Package:
    pub_package = get_pub_package(package.name)
    if not pub_package:
        return package

    current_package = _get_current_package(pub_package, package.version)

    _set_health_metadata(package, pub_package, current_package)

    return package
