from labels.enrichers.php.get import PackagistPackageInfo, get_composer_package
from labels.enrichers.utils import infer_algorithm
from labels.model.package import Artifact, Digest, HealthMetadata, Package
from labels.utils.licenses.validation import validate_licenses


def _get_author(composer_package: PackagistPackageInfo) -> str | None:
    if not composer_package.get("authors"):
        return None

    authors: list[str] = []
    authors_dict = composer_package["authors"]
    for author_item in authors_dict:
        author: str = author_item["name"]
        if "email" in author_item:
            author_email = author_item["email"]
            author += f" <{author_email}>"
        authors.append(author)

    return ", ".join(authors)


def _set_health_metadata(
    package: Package,
    composer_package: PackagistPackageInfo,
    current_package: PackagistPackageInfo | None,
) -> None:
    package.health_metadata = HealthMetadata(
        latest_version=composer_package["version"],
        latest_version_created_at=composer_package["time"],
        artifact=_get_artifact_metadata(current_package),
        authors=_get_author(composer_package),
    )


def _get_artifact_metadata(
    current_package: PackagistPackageInfo | None,
) -> Artifact | None:
    if current_package:
        dist_info = current_package.get("dist")
        if isinstance(dist_info, dict) and isinstance(dist_info.get("url"), str):
            digest_value = dist_info.get("shasum") or None
            return Artifact(
                url=dist_info["url"],
                integrity=Digest(
                    algorithm=infer_algorithm(digest_value),
                    value=digest_value,
                ),
            )
    return None


def complete_package(package: Package) -> Package:
    current_package = get_composer_package(package.name, package.version)
    # The p2/$vendor/$package.json file contains only tagged releases, not development versions
    composer_package = get_composer_package(package.name)

    if not composer_package:
        return package

    _set_health_metadata(package, composer_package, current_package)

    package.licenses = validate_licenses(composer_package["license"])

    return package
