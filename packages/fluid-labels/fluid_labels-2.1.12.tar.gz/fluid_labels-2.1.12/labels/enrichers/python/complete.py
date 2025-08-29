from labels.enrichers.python.get import PyPIResponse, get_pypi_package
from labels.enrichers.utils import infer_algorithm
from labels.model.package import Artifact, Digest, HealthMetadata, Package
from labels.utils.licenses.validation import validate_licenses


def _get_artifact(package: Package, current_package: PyPIResponse) -> Artifact | None:
    url = next(
        (x for x in current_package["urls"] if x["url"].endswith(".tar.gz")),
        None,
    )

    digest_value: str | None = url.get("digests", {}).get("sha256") or None if url else None

    return Artifact(
        url=url["url"] if url else f"https://pypi.org/pypi/{package.name}",
        integrity=Digest(
            algorithm=infer_algorithm(digest_value),
            value=digest_value,
        ),
    )


def _get_authors(pypi_package: PyPIResponse) -> str | None:
    package_info = pypi_package["info"]
    author: str | None = None
    package_author = package_info["author"]
    author_email = package_info.get("author_email")
    if package_author:
        author = package_author
    if not author and author_email:
        author = author_email
    if author and author_email and author_email not in author:
        author = f"{author} <{author_email}>"
    return author


def _set_health_metadata(
    package: Package,
    pypi_package: PyPIResponse,
    current_package: PyPIResponse | None,
) -> None:
    info = pypi_package.get("info")
    if not isinstance(info, dict):
        return
    pypi_package_version = info.get("version")
    releases = pypi_package.get("releases")
    if not isinstance(releases, dict):
        releases = {}

    upload_time = releases.get(pypi_package_version) if pypi_package_version else []
    if not isinstance(upload_time, list):
        upload_time = []

    latest_version_created_at: str | None = None
    if upload_time:
        first_release = upload_time[0]
        time_value = first_release.get("upload_time_iso_8601")
        if isinstance(time_value, str):
            latest_version_created_at = time_value

    package.health_metadata = HealthMetadata(
        latest_version=pypi_package_version,
        latest_version_created_at=latest_version_created_at,
        authors=_get_authors(pypi_package),
        artifact=_get_artifact(package, current_package) if current_package else None,
    )


def _update_licenses(pypi_package: PyPIResponse, package: Package) -> None:
    info = pypi_package.get("info")
    if not isinstance(info, dict):
        return
    licenses = info.get("license")
    if licenses:
        package.licenses = validate_licenses([licenses])


def complete_package(package: Package) -> Package:
    pypi_package = get_pypi_package(package.name)
    if not pypi_package:
        return package

    current_package = get_pypi_package(package.name, package.version)

    _set_health_metadata(package, pypi_package, current_package)

    _update_licenses(pypi_package, package)

    return package
