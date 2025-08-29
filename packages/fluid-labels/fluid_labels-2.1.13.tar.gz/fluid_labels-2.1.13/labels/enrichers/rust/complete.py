from labels.enrichers.rust.get import CRATES_ENDPOINT, CargoPackage, Version, get_cargo_package
from labels.enrichers.utils import infer_algorithm
from labels.model.package import Artifact, Digest, HealthMetadata, Package
from labels.utils.licenses.validation import validate_licenses


def _get_artifact(
    current_package: Version | None,
) -> Artifact | None:
    if current_package:
        digest_value = current_package.get("checksum")
        return Artifact(
            url=f"{CRATES_ENDPOINT}{current_package['dl_path']}",
            integrity=Digest(
                algorithm=infer_algorithm(digest_value),
                value=digest_value,
            ),
        )
    return None


def _set_health_metadata(
    package: Package,
    current_package: Version | None,
    cargo_package: CargoPackage,
) -> None:
    crate_info = cargo_package.get("crate", {})
    max_stable_version = crate_info.get("max_stable_version")
    updated_at = crate_info.get("updated_at")
    published_by = cargo_package["versions"][0].get("published_by")
    artifact = _get_artifact(current_package)

    package.health_metadata = HealthMetadata(
        latest_version=max_stable_version,
        latest_version_created_at=updated_at,
        artifact=artifact,
        authors=published_by["name"] if published_by else None,
    )


def complete_package(package: Package) -> Package:
    cargo_package = get_cargo_package(package.name)
    if not cargo_package:
        return package

    versions = cargo_package["versions"]
    current_package = next(
        (version for version in versions if version["num"] == package.version),
        None,
    )

    _set_health_metadata(package, current_package, cargo_package)

    licenses = current_package.get("license") if current_package else None
    if isinstance(licenses, str):
        package.licenses = validate_licenses([licenses])

    return package
