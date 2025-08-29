from decimal import Decimal

from cyclonedx.factory.license import LicenseFactory
from cyclonedx.model import HashType, Property, XsUri
from cyclonedx.model.contact import OrganizationalContact
from cyclonedx.model.license import License
from cyclonedx.model.vulnerability import (
    BomTarget,
    BomTargetVersionRange,
    Vulnerability,
    VulnerabilityAdvisory,
    VulnerabilityRating,
    VulnerabilitySeverity,
)

from labels.model.file import Location
from labels.model.package import HealthMetadata, Package
from labels.output.utils import get_author_info

NAMESPACE = "fluid-attacks"


def add_vulnerabilities(package: Package) -> list[Vulnerability]:
    vulnerabilities = []
    if package.advisories:
        for advisory in package.advisories:
            rating = VulnerabilityRating(
                severity=VulnerabilitySeverity(
                    advisory.severity_level.lower() if advisory.severity_level else None,
                ),
                score=Decimal(str(advisory.percentile)),
            )

            advisory_obj = (
                [VulnerabilityAdvisory(url=XsUri(advisory.source))] if advisory.source else None
            )

            bom_target = BomTarget(
                ref=f"{package.name}@{package.version}",
                versions=[
                    BomTargetVersionRange(
                        version=package.version if not advisory.vulnerable_version else None,
                        range=advisory.vulnerable_version,
                    ),
                ],
            )

            additional_properties = [
                Property(name=f"{NAMESPACE}:advisory:epss", value=str(advisory.epss)),
            ]

            vulnerability = Vulnerability(
                bom_ref=f"{package.name}@{advisory.id}",
                id=advisory.id,
                description=advisory.details,
                advisories=advisory_obj,
                ratings=[rating],
                affects=[bom_target],
                properties=additional_properties,
            )

            vulnerabilities.append(vulnerability)

    return vulnerabilities


def add_health_metadata_properties(
    health_metadata: HealthMetadata,
) -> list[Property]:
    properties = []
    if health_metadata.latest_version:
        properties.append(
            Property(
                name=f"{NAMESPACE}:health_metadata:latest_version",
                value=health_metadata.latest_version,
            ),
        )

    if health_metadata.latest_version_created_at:
        properties.append(
            Property(
                name=f"{NAMESPACE}:health_metadata:latest_version_created_at",
                value=str(health_metadata.latest_version_created_at),
            ),
        )

    return properties


def add_locations_properties(locations: list[Location]) -> list[Property]:
    properties = []
    for idx, location in enumerate(locations):
        path = location.path()

        line = (
            location.coordinates.line
            if location.coordinates and location.coordinates.line
            else None
        )
        layer = (
            location.coordinates.file_system_id
            if location.coordinates and location.coordinates.file_system_id
            else None
        )

        properties.append(Property(name=f"{NAMESPACE}:locations:{idx}:path", value=path))

        if line:
            properties.append(Property(name=f"{NAMESPACE}:locations:{idx}:line", value=str(line)))

        if layer:
            properties.append(Property(name=f"{NAMESPACE}:locations:{idx}:layer", value=layer))

    return properties


def add_language_property(package_language: str) -> Property:
    return Property(name=f"{NAMESPACE}:language", value=package_language)


def add_integrity(health_metadata: HealthMetadata) -> list[HashType] | None:
    integrity = health_metadata.artifact.integrity if health_metadata.artifact else None
    if integrity and integrity.algorithm and integrity.value:
        return [HashType.from_hashlib_alg(integrity.algorithm, integrity.value)]
    return None


def add_authors(health_metadata: HealthMetadata) -> list[OrganizationalContact]:
    authors_info = get_author_info(health_metadata)
    return [
        OrganizationalContact(name=name, email=email)
        for name, email in authors_info
        if name or email
    ]


def get_licenses(package_licenses: list[str]) -> list[License]:
    lc_factory = LicenseFactory()
    return [lc_factory.make_from_string(lic) for lic in package_licenses]


def add_component_properties(package: Package) -> list[Property]:
    properties = []

    properties.append(add_language_property(package.language))
    properties.extend(add_locations_properties(package.locations))

    if package.health_metadata:
        properties.extend(add_health_metadata_properties(package.health_metadata))

    return properties
