import logging

from license_expression import ExpressionError, LicenseExpression, get_spdx_licensing
from spdx_tools.spdx.model.actor import Actor, ActorType
from spdx_tools.spdx.model.checksum import Checksum, ChecksumAlgorithm
from spdx_tools.spdx.model.document import Document
from spdx_tools.spdx.model.package import (
    ExternalPackageRef,
    ExternalPackageRefCategory,
    PackagePurpose,
)
from spdx_tools.spdx.model.package import Package as SPDX_Package
from spdx_tools.spdx.model.spdx_no_assertion import SpdxNoAssertion
from spdx_tools.spdx.validation.uri_validators import validate_url

from labels.model.file import Location
from labels.model.package import HealthMetadata, Package
from labels.output.utils import get_author_info, sanitize_name

NOASSERTION = SpdxNoAssertion()
NAMESPACE = "fluid-attacks"

LOGGER = logging.getLogger(__name__)


def is_valid_url(url: str) -> bool:
    return not validate_url(url)


def get_valid_advisory_urls(url: str) -> str:
    if url and url != "MANUAL":
        if is_valid_url(url):
            return url
        LOGGER.warning("Invalid advisory URL found and skipped: %s", url)

    return "https://fluidattacks.com"


def add_vulnerabilities_spdx(package: Package) -> list[ExternalPackageRef]:
    vulnerabilities_refs = []
    if package.advisories:
        for advisory in package.advisories:
            combined_urls = get_valid_advisory_urls(advisory.source)

            comment_parts = [
                f"Severity: {advisory.severity_level}",
                f"EPSs: {advisory.epss}",
                f"Score: {advisory.percentile}",
                f"Affected Version: {package.version}",
                f"Affected Version Range: {advisory.vulnerable_version}"
                if advisory.vulnerable_version
                else None,
                f"Description: {advisory.details}" if advisory.details else None,
            ]
            comment_text = "; ".join(filter(None, comment_parts))

            vulnerabilities_refs.append(
                ExternalPackageRef(
                    category=ExternalPackageRefCategory.SECURITY,
                    reference_type="advisory",
                    locator=combined_urls,
                    comment=comment_text,
                ),
            )

    return vulnerabilities_refs


def add_authors(
    health_metadata: HealthMetadata | None,
) -> Actor | SpdxNoAssertion:
    if health_metadata is None:
        return NOASSERTION

    authors_info = get_author_info(health_metadata)

    names = []
    emails = []

    for name, email in authors_info:
        if name:
            names.append(name)
        if email:
            emails.append(email)

    concatenated_names = ", ".join(names)
    concatenated_emails = ", ".join(emails) or None

    return Actor(
        actor_type=ActorType.PERSON,
        name=concatenated_names,
        email=concatenated_emails,
    )


def add_locations_external_refs(
    locations: list[Location],
) -> list[ExternalPackageRef]:
    locations_external_refs = []
    for idx, location in enumerate(locations):
        path = location.path()
        coordinates = location.coordinates
        line = coordinates.line if coordinates else None
        layer = coordinates.file_system_id if coordinates else None

        locations_external_refs.append(
            ExternalPackageRef(
                category=ExternalPackageRefCategory.OTHER,
                reference_type=f"{NAMESPACE}:locations:{idx}:path",
                locator=path,
            ),
        )

        if line:
            locations_external_refs.append(
                ExternalPackageRef(
                    category=ExternalPackageRefCategory.OTHER,
                    reference_type=f"{NAMESPACE}:locations:{idx}:line",
                    locator=str(line),
                ),
            )

        if layer:
            locations_external_refs.append(
                ExternalPackageRef(
                    category=ExternalPackageRefCategory.OTHER,
                    reference_type=f"{NAMESPACE}:locations:{idx}:layer",
                    locator=layer,
                ),
            )

    return locations_external_refs


def add_health_metadata_external_refs(
    health_metadata: HealthMetadata,
) -> list[ExternalPackageRef]:
    health_metadata_external_refs = []

    if health_metadata.latest_version:
        health_metadata_external_refs.append(
            ExternalPackageRef(
                category=ExternalPackageRefCategory.OTHER,
                reference_type=(f"{NAMESPACE}:health_metadata:latest_version"),
                locator=health_metadata.latest_version,
            ),
        )

    if health_metadata.latest_version_created_at:
        health_metadata_external_refs.append(
            ExternalPackageRef(
                category=ExternalPackageRefCategory.OTHER,
                reference_type=(f"{NAMESPACE}:health_metadata:latest_version_created_at"),
                locator=str(health_metadata.latest_version_created_at).replace(" ", ""),
            ),
        )

    return health_metadata_external_refs


def add_purl_external_ref(
    package_purl: str,
) -> ExternalPackageRef:
    return ExternalPackageRef(
        category=ExternalPackageRefCategory.PACKAGE_MANAGER,
        reference_type="purl",
        locator=package_purl,
    )


def add_language_external_ref(language: str) -> ExternalPackageRef:
    return ExternalPackageRef(
        category=ExternalPackageRefCategory.OTHER,
        reference_type=f"{NAMESPACE}:language",
        locator=language,
    )


def add_external_refs(package: Package) -> list[ExternalPackageRef]:
    external_refs = []
    health_metadata = package.health_metadata

    external_refs.append(add_language_external_ref(package.language))

    if health_metadata:
        external_refs.extend(add_health_metadata_external_refs(health_metadata))

    external_refs.append(add_purl_external_ref(package.p_url))
    external_refs.extend(add_locations_external_refs(package.locations))
    external_refs.extend(add_vulnerabilities_spdx(package))

    return external_refs


def add_integrity(health_metadata: HealthMetadata | None) -> list[Checksum]:
    if health_metadata:
        integrity = health_metadata.artifact.integrity if health_metadata.artifact else None
        if integrity and integrity.algorithm and integrity.value:
            return [
                Checksum(
                    algorithm=ChecksumAlgorithm[integrity.algorithm.upper()],
                    value=integrity.value,
                ),
            ]
    return []


def add_empty_package(document: Document) -> None:
    document.creation_info.document_comment = (
        "No packages or relationships were found in the resource."
    )

    empty_package = SPDX_Package(
        name="NONE",
        spdx_id="SPDXRef-Package-NONE",
        download_location=NOASSERTION,
        license_concluded=NOASSERTION,
        primary_package_purpose=PackagePurpose.LIBRARY,
    )

    document.packages = [empty_package]
    document.relationships = []


def get_spdx_id(package: Package) -> str:
    name = sanitize_name(package.name)
    pkg_platform = sanitize_name(package.type.value.lower())
    pkg_id = package.id_
    return f"SPDXRef-Package-{pkg_platform}-{name}-{pkg_id}"


def add_license(licenses: list[str]) -> LicenseExpression | SpdxNoAssertion:
    licensing = get_spdx_licensing()
    parsed = NOASSERTION
    try:
        parsed = licensing.parse(" , ".join(licenses), validate=True)
    except ExpressionError:
        return NOASSERTION

    return parsed
