import base64

from labels.enrichers.dotnet.get import NugetCatalogEntry, get_nuget_package
from labels.enrichers.utils import infer_algorithm
from labels.model.package import Artifact, Digest, HealthMetadata, Package
from labels.utils.licenses.validation import validate_licenses


def _get_artifact(current_package: NugetCatalogEntry | None) -> Artifact | None:
    if current_package:
        # {LOWER_ID}/{LOWER_VERSION}/{LOWER_ID}.{LOWER_VERSION}.nupkg
        lower_id: str | None = current_package["id"].lower()
        lower_version: str | None = current_package["version"].lower()

        digest_value: str | None = current_package.get("packageHash") or None
        algorithm: str | None = current_package.get("packageHashAlgorithm") or None

        if algorithm:
            algorithm = algorithm.lower()
            if algorithm == "sha512" and digest_value:
                digest_value = base64.b64decode(digest_value).hex()

        return Artifact(
            url=(
                f"https://api.nuget.org/v3-flatcontainer/{lower_id}"
                f"/{lower_version}/{lower_id}.{lower_version}.nupkg"
            ),
            integrity=Digest(
                algorithm=infer_algorithm(digest_value),
                value=digest_value,
            ),
        )
    return None


def _set_health_metadata(
    package: Package,
    nuget_package: NugetCatalogEntry,
    current_package: NugetCatalogEntry | None,
) -> None:
    package.health_metadata = HealthMetadata(
        latest_version=nuget_package.get("version"),
        latest_version_created_at=nuget_package.get("published"),
        authors=nuget_package.get("authors"),
        artifact=_get_artifact(current_package) if current_package else None,
    )


def complete_package(package: Package) -> Package:
    current_package = get_nuget_package(package.name, package.version)
    nuget_package = get_nuget_package(package.name)

    if not nuget_package:
        return package

    _set_health_metadata(package, nuget_package, current_package)

    nuget_licenses = nuget_package["licenseExpression"]
    package.licenses = validate_licenses([nuget_licenses]) if nuget_licenses else []

    return package
