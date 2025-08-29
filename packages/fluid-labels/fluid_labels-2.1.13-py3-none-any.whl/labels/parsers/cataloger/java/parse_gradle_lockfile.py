from pydantic import BaseModel, ValidationError

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.java.model import JavaArchive, JavaPomProject
from labels.parsers.cataloger.java.package import package_url
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning


class LockFileDependency(BaseModel):
    group: str
    name: str
    version: str
    line: int | None = None


def parse_gradle_lockfile(
    _resolver: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    dependencies: list[LockFileDependency] = []
    packages: list[Package] = []
    for line_number, line in enumerate(reader.read_closer.readlines(), 1):
        if "=" in line and ":" in line:  # To ensure it's a dependency line
            dependency_part = line.split("=")[0]
            group, name, version = dependency_part.split(":")
            dependencies.append(
                LockFileDependency(group=group, name=name, version=version, line=line_number),
            )

    for dependency in dependencies:
        name = dependency.name
        version = dependency.version

        if not name or not version:
            continue

        new_location = get_enriched_location(reader.location, line=dependency.line)

        archive = JavaArchive(
            pom_project=JavaPomProject(
                group_id=dependency.group,
                name=name,
                artifact_id=name,
                version=version,
            ),
        )

        try:
            packages.append(
                Package(
                    name=f"{dependency.group}:{name}",
                    version=version,
                    locations=[new_location],
                    language=Language.JAVA,
                    type=PackageType.JavaPkg,
                    metadata=archive,
                    p_url=package_url(name, version, archive),
                    licenses=[],
                ),
            )
        except ValidationError as ex:
            log_malformed_package_warning(new_location, ex)
            continue

    return packages, []
