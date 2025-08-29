from labels.enrichers.elixir.get import get_hex_package
from labels.model.package import HealthMetadata, Package
from labels.utils.licenses.validation import validate_licenses


def complete_package(package: Package) -> Package:
    response = get_hex_package(package.name)
    if not response:
        return package
    package.health_metadata = HealthMetadata(
        latest_version=response["latest_stable_version"],
        latest_version_created_at=next(
            (
                x["inserted_at"]
                for x in response["releases"]
                if x["version"] == response["latest_stable_version"]
            ),
            None,
        ),
    )

    package.licenses = validate_licenses(response["meta"]["licenses"])

    if response["owners"]:
        package.health_metadata.authors = ", ".join([x["username"] for x in response["owners"]])
    return package
