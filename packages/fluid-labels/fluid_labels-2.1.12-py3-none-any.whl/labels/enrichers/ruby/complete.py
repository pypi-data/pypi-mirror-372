from labels.enrichers.ruby.get import RubyGemsPackage, get_gem_package
from labels.enrichers.utils import infer_algorithm
from labels.model.package import Artifact, Digest, HealthMetadata, Package
from labels.utils.licenses.validation import validate_licenses


def _get_artifact(current_package: RubyGemsPackage) -> Artifact | None:
    digest_value = current_package.get("sha") or None
    return Artifact(
        url=current_package["gem_uri"],
        integrity=Digest(
            algorithm=infer_algorithm(digest_value),
            value=digest_value,
        ),
    )


def _set_health_metadata(
    package: Package,
    gem_package: RubyGemsPackage,
    current_package: RubyGemsPackage | None,
) -> None:
    package.health_metadata = HealthMetadata(
        latest_version=gem_package["version"],
        latest_version_created_at=gem_package["version_created_at"],
        authors=gem_package["authors"],
        artifact=_get_artifact(current_package) if current_package else None,
    )


def complete_package(package: Package) -> Package:
    current_package = get_gem_package(package.name, package.version)
    gem_package = get_gem_package(package.name)
    if not gem_package:
        return package

    _set_health_metadata(package, gem_package, current_package)

    gem_licenses = gem_package["licenses"]
    if gem_licenses:
        package.licenses = validate_licenses(gem_licenses)
    return package
