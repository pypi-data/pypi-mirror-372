import base64
from contextlib import suppress

from labels.enrichers.javascript.get import NPMPackage, NPMPackageLicense, get_npm_package
from labels.enrichers.utils import infer_algorithm
from labels.model.package import Artifact, Digest, HealthMetadata, Package
from labels.utils.licenses.validation import validate_licenses


def _get_author(npm_package: NPMPackage) -> str | None:
    author: str | None = None
    if "author" in npm_package:
        package_author = npm_package["author"]
        if isinstance(package_author, dict) and "name" in package_author:
            author = package_author["name"]
            if "email" in package_author:
                author = f"{author} <{package_author['email']}>"
        elif package_author and isinstance(package_author, str):
            author = str(package_author)
        return author
    return None


def _get_latest_version_info(
    npm_package: NPMPackage,
) -> tuple[str | None, str | None]:
    latest_version = None
    latest_version_created_at = None

    if npm_package.get("dist-tags"):
        latest_version = npm_package["dist-tags"]["latest"]
        latest_version_created_at = npm_package["time"][latest_version]

    return latest_version, latest_version_created_at


def _get_artifact_info(
    npm_package: NPMPackage,
    current_version: str,
) -> Artifact | None:
    current_package = npm_package["versions"].get(current_version)
    artifact = None

    if current_package:
        with suppress(KeyError):
            digest_value = current_package.get("dist", {}).get("integrity") or None

            if digest_value:
                algorithm, digest_hash = digest_value.split("-", 1)
                if algorithm == "sha512":
                    binary_hash = base64.b64decode(digest_hash)
                    digest_hash = binary_hash.hex()

                artifact = Artifact(
                    url=current_package["dist"]["tarball"],
                    integrity=Digest(
                        algorithm=infer_algorithm(digest_hash),
                        value=digest_hash,
                    ),
                )

    return artifact


def _set_health_metadata(package: Package, npm_package: NPMPackage) -> None:
    latest_version, latest_version_created_at = _get_latest_version_info(
        npm_package,
    )
    package.health_metadata = HealthMetadata(
        latest_version=latest_version,
        latest_version_created_at=latest_version_created_at,
        artifact=_get_artifact_info(npm_package, package.version),
        authors=_get_author(npm_package),
    )


def complete_package(package: Package) -> Package:
    npm_package = get_npm_package(package.name)
    if not npm_package:
        return package

    _set_health_metadata(package, npm_package)

    licenses = npm_package.get("license")
    if licenses and isinstance(licenses, (str | list | dict)):
        package.licenses = validate_licenses(handle_licenses(licenses))

    return package


def handle_licenses(
    licenses: str | list[str | dict[str, str]] | NPMPackageLicense,
) -> list[str]:
    if isinstance(licenses, dict):
        return [licenses["type"]] if "type" in licenses else []
    if isinstance(licenses, list):
        licenses_list = []
        for license_item in licenses:
            if isinstance(license_item, str):
                licenses_list.append(license_item)
            if isinstance(license_item, dict) and license_item["type"]:
                licenses_list.append(license_item["type"])
        return licenses_list
    return [licenses]
