import re

from pydantic import BaseModel, ValidationError

from labels.model.file import Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.java.model import JavaArchive, JavaPomProject
from labels.parsers.cataloger.java.package import package_url
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning

# Constants
QUOTE = r'["\']'
NL = r"(\n?\s*)?"
TEXT = r"[a-zA-Z0-9._-]+"
CONFIG_TO_DEV_STATUS = {
    "testRuntimeOnly": True,
    "testCompileOnly": True,
    "testImplementation": True,
    "compileOnly": True,
    "testCompile": True,
    "androidTestImplementation": True,
    "compile": False,
    "runtime": False,
    "implementation": False,
    "api": False,
    "runtimeOnly": False,
}


def is_comment(line: str) -> bool:
    return (
        line.strip().startswith("//")
        or line.strip().startswith("/*")
        or line.strip().endswith("*/")
    )


class LockFileDependency(BaseModel):
    group: str
    name: str
    version: str
    config: str
    line: int | None = None


def _build_regex_with_configs() -> re.Pattern[str]:
    configs = {
        "runtimeOnly",
        "api",
        "compile",
        "compileOnly",
        "implementation",
        "testRuntimeOnly",
        "testCompileOnly",
        "testImplementation",
        "runtime",
        "androidTestImplementation",
    }

    config_pattern = "|".join(configs)

    return re.compile(
        rf"(?P<config_name>{config_pattern})\({QUOTE}"
        rf"(?P<group>{TEXT}):(?P<name>{TEXT}):"
        rf"(?P<version>{TEXT})"
        rf"(?::(?P<classifier>{TEXT}))?"
        rf"{QUOTE}\)",
    )


def parse_gradle_lockfile_kts(
    _resolver: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    dependencies = parse_dependencies(reader)
    packages = create_packages(dependencies, reader.location)
    return packages, []


def parse_dependencies(reader: LocationReadCloser) -> list[LockFileDependency]:
    dependencies: list[LockFileDependency] = []
    is_block_comment = False

    for line_no, raw_line in enumerate(reader.read_closer.readlines(), start=1):
        line = raw_line.strip()
        is_block_comment = update_block_comment_status(line, is_block_comment=is_block_comment)

        if is_block_comment or is_comment(line):
            continue

        dependency = extract_dependency(line, line_no)
        if dependency:
            dependencies.append(dependency)

    return dependencies


def update_block_comment_status(line: str, *, is_block_comment: bool) -> bool:
    if "/*" in line:
        return True
    if "*/" in line:
        return False
    return is_block_comment


def extract_dependency(line: str, line_no: int) -> LockFileDependency | None:
    regex = _build_regex_with_configs()
    if match := regex.match(line):
        version = match.group("version")
        config = match.group("config_name")
        if version:
            return LockFileDependency(
                group=match.group("group"),
                name=match.group("name"),
                version=version,
                config=config,
                line=line_no,
            )

    return None


def create_packages(
    dependencies: list[LockFileDependency],
    reader_location: Location,
) -> list[Package]:
    packages: list[Package] = []

    for dependency in dependencies:
        name = dependency.name
        version = dependency.version

        if not name or not version:
            continue

        is_dev = CONFIG_TO_DEV_STATUS.get(dependency.config, None)

        new_location = get_enriched_location(reader_location, line=dependency.line, is_dev=is_dev)

        archive = create_java_archive(dependency, name, version)

        package = create_package(name, version, new_location, archive, dependency.group)
        if package:
            packages.append(package)

    return packages


def create_java_archive(
    dependency: LockFileDependency,
    name: str,
    version: str,
) -> JavaArchive:
    return JavaArchive(
        pom_project=JavaPomProject(
            group_id=dependency.group,
            name=name,
            artifact_id=name,
            version=version,
        ),
    )


def create_package(
    name: str,
    version: str,
    location: Location,
    archive: JavaArchive,
    group: str,
) -> Package | None:
    try:
        return Package(
            name=f"{group}:{name}",
            version=version,
            locations=[location],
            language=Language.JAVA,
            type=PackageType.JavaPkg,
            metadata=archive,
            p_url=package_url(name, version, archive),
            licenses=[],
        )
    except ValidationError as ex:
        log_malformed_package_warning(location, ex)
        return None
