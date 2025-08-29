from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.utils.strings import normalize_name


def get_relationships_from_declared_dependencies(
    packages: list[Package],
    declared_dependencies: dict[str, ParsedValue],
) -> list[Relationship]:
    results: list[Relationship] = []

    for package_name, dependencies in declared_dependencies.items():
        if not isinstance(dependencies, IndexedDict):
            continue

        dependency_packages_generator = (
            package
            for package in packages
            for dependency_name in dependencies
            if normalize_name(dependency_name, PackageType.DotnetPkg) == package.name
        )

        current_package = next((p for p in packages if p.name == package_name), None)

        if current_package is not None:
            results.extend(
                Relationship(
                    from_=dependency_package.id_,
                    to_=current_package.id_,
                    type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                )
                for dependency_package in dependency_packages_generator
            )
    return results
