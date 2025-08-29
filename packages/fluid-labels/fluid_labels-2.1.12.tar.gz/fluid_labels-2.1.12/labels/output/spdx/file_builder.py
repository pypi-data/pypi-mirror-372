from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

from spdx_tools.spdx.model.document import Document
from spdx_tools.spdx.model.package import Package as SPDX_Package
from spdx_tools.spdx.model.package import PackagePurpose
from spdx_tools.spdx.model.relationship import Relationship as SPDXRelationship
from spdx_tools.spdx.model.relationship import RelationshipType as SPDXRelationshipType

from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.output.spdx.complete_file import (
    NOASSERTION,
    add_authors,
    add_external_refs,
    add_integrity,
    add_license,
    get_spdx_id,
)


def package_to_spdx_pkg(package: Package) -> SPDX_Package:
    spdx_id = get_spdx_id(package)
    license_declared = add_license(package.licenses)
    originator = add_authors(package.health_metadata)
    external_refs = add_external_refs(package)
    checksums = add_integrity(package.health_metadata)

    return SPDX_Package(
        spdx_id=spdx_id,
        name=package.name,
        download_location=NOASSERTION,
        version=package.version,
        license_declared=license_declared,
        originator=originator,
        primary_package_purpose=PackagePurpose.LIBRARY,
        external_references=external_refs,
        checksums=checksums,
    )


def create_package_cache(packages: list[Package]) -> dict[str, SPDX_Package]:
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        spdx_packages = list(executor.map(package_to_spdx_pkg, packages))
    return {pkg.id_: spdx_pkg for pkg, spdx_pkg in zip(packages, spdx_packages, strict=True)}


def create_document_relationships(
    document: Document,
    spdx_packages: list[SPDX_Package],
) -> list[SPDXRelationship]:
    doc_spdx_id = document.creation_info.spdx_id
    return [
        SPDXRelationship(doc_spdx_id, SPDXRelationshipType.DESCRIBES, pkg.spdx_id)
        for pkg in spdx_packages
    ]


def process_relationship(
    relationship: Relationship,
    spdx_id_cache: dict[str, str],
) -> SPDXRelationship | None:
    to_pkg_id = spdx_id_cache.get(relationship.to_)
    from_pkg_id = spdx_id_cache.get(relationship.from_)

    if to_pkg_id and from_pkg_id:
        return SPDXRelationship(to_pkg_id, SPDXRelationshipType.DEPENDENCY_OF, from_pkg_id)

    return None


def process_relationships(
    relationships: list[Relationship],
    spdx_id_cache: dict[str, str],
) -> list[SPDXRelationship]:
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        processed_relationships = list(
            executor.map(lambda r: process_relationship(r, spdx_id_cache), relationships),
        )

    return [relationship for relationship in processed_relationships if relationship is not None]


def add_packages_and_relationships(
    document: Document,
    packages: list[Package],
    relationships: list[Relationship],
) -> None:
    package_cache = create_package_cache(packages)
    spdx_packages = list(package_cache.values())
    spdx_id_cache = {pkg_id: spdx_pkg.spdx_id for pkg_id, spdx_pkg in package_cache.items()}

    document.packages = spdx_packages
    document.relationships.extend(
        [
            *create_document_relationships(document, document.packages),
            *process_relationships(relationships, spdx_id_cache),
        ],
    )
