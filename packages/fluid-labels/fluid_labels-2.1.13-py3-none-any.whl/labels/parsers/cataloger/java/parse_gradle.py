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
TEXT = r'[^"\']+'
RE_LINE_COMMENT: re.Pattern[str] = re.compile(rf"^.*{NL}//.*$")
CONFIG_TO_DEV_STATUS = {
    "testRuntimeOnly": True,
    "testCompileOnly": True,
    "testImplementation": True,
    "compileOnly": True,
    "testCompile": True,
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
) -> Package:
    return Package(
        name=name,
        version=version,
        locations=[location],
        language=Language.JAVA,
        type=PackageType.JavaPkg,
        metadata=archive,
        p_url=package_url(name.rsplit(":", 1)[-1], version, archive),
        licenses=[],
    )


def avoid_cmt(line: str, *, is_block_cmt: bool) -> tuple[str, bool]:
    if RE_LINE_COMMENT.match(line):
        line = line.split("//", 1)[0]
    if is_block_cmt:
        if "*/" in line:
            is_block_cmt = False
            line = line.split("*/", 1).pop()
        else:
            return "", is_block_cmt
    if "/*" in line:
        line_cmt_open = line.split("/*", 1)[0]
        if "*/" in line:
            line = line_cmt_open + line.split("*/", 1).pop()
        else:
            line = line_cmt_open
            is_block_cmt = True
    return line, is_block_cmt


def get_line_number(content: str, match_start: int) -> int:
    return content[:match_start].count("\n") + 2


def extract_gradle_configs(content: str) -> set[str]:
    config_pattern = re.compile(r"configurations\s*\{([^}]+)\}", re.DOTALL)
    custom_config_pattern = re.compile(r"\s*(\w+)\s*")
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
    }

    config_blocks = config_pattern.findall(content)
    for block in config_blocks:
        custom_configs = custom_config_pattern.findall(block)
        configs.update(custom_configs)

    return configs


def build_regex_with_configs(configs: set[str]) -> dict[str, re.Pattern[str]]:
    config_pattern = "|".join(configs)

    return {
        "RE_GRADLE_A": re.compile(
            rf"^{NL}(?P<config_name>{config_pattern}){NL}[(]?{NL}"
            rf"group{NL}:{NL}{QUOTE}(?P<group>{TEXT}){QUOTE}{NL},"
            rf"{NL}name{NL}:{NL}{QUOTE}(?P<name>{TEXT}){QUOTE}{NL}"
            rf"(?:,{NL}version{NL}:{NL}{QUOTE}(?P<version>{TEXT}){QUOTE}{NL})"
            rf"?.*$",
        ),
        "RE_GRADLE_B": re.compile(
            rf"^.*{NL}(?P<config_name>{config_pattern}){NL}[(]?{NL}{QUOTE}(?P<statement>{TEXT}){QUOTE}",
        ),
        "RE_GRADLE_C": re.compile(
            rf"{NL}(?P<config_name>{config_pattern}){NL}\("
            rf"{NL}{QUOTE}(?P<statement>{TEXT}){QUOTE}{NL}\)"
            rf"{NL}{{({NL})version{NL}{{({NL})strictly{NL}\({NL}"
            rf"{QUOTE}(?P<version>{TEXT}){QUOTE}{NL}\){NL}}}{NL}}}",
            re.DOTALL,
        ),
        "BLOCK": re.compile(
            rf"{NL}(?P<config_name>{config_pattern}){NL}\("
            rf"{NL}{QUOTE}(?P<statement>{TEXT}){QUOTE}{NL}\)"
            rf"{NL}\{{(.*?version{NL}\{{.*?\}}){NL}\}}",
            re.DOTALL,
        ),
        "VERSION": re.compile(
            rf"version{NL}{{({NL})strictly{NL}\("
            rf"{NL}{QUOTE}(?P<version>{TEXT}){QUOTE}{NL}\){NL}}}",
            re.DOTALL,
        ),
    }


def get_block_deps(content: str, regexes: dict[str, re.Pattern[str]]) -> list[LockFileDependency]:
    dependencies = []

    for block in regexes["BLOCK"].finditer(content):
        product = block.group("statement")
        hit = regexes["VERSION"].search(block.group())
        if not hit:
            continue

        version = hit.group("version")
        if version == "":
            continue

        config = block.group("config_name")

        line_no = get_line_number(content, block.start())

        dependencies.append(
            LockFileDependency(
                group=product.split(":")[0],
                name=product,
                version=version,
                line=line_no,
                config=config,
            ),
        )
    return dependencies


def parse_dependencies(reader: LocationReadCloser) -> list[LockFileDependency]:
    content = reader.read_closer.read()
    configs = extract_gradle_configs(content)
    maven_regexes = build_regex_with_configs(configs)
    dependencies: list[LockFileDependency] = get_block_deps(content, maven_regexes)

    is_block_cmt = False
    for line_no, raw_line in enumerate(content.splitlines(), start=1):
        line, is_block_cmt = avoid_cmt(raw_line, is_block_cmt=is_block_cmt)

        if match := maven_regexes["RE_GRADLE_A"].match(line):
            config = match.group("config_name")
            group = match.group("group")
            product = group + ":" + match.group("name")
            version = match.group("version") or ""
        elif match := maven_regexes["RE_GRADLE_B"].match(line):
            config = match.group("config_name")
            statement = match.group("statement")
            product, version = (
                statement.rsplit(":", maxsplit=1) if statement.count(":") >= 2 else (statement, "")
            )
            group = product.split(":")[0]
        else:
            continue

        # Assuming a wildcard in Maven if the version is not found can
        # result in issues.
        # https://gitlab.com/fluidattacks/universe/-/issues/5635
        if version == "" or re.match(r"\${.*}", version):
            continue

        dependencies.append(
            LockFileDependency(
                group=group, name=product, version=version, line=line_no, config=config
            ),
        )

    return dependencies


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

        try:
            package = create_package(name, version, new_location, archive)
            packages.append(package)
        except ValidationError as ex:
            log_malformed_package_warning(new_location, ex)

    return packages


def parse_gradle(
    _resolver: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    dependencies = parse_dependencies(reader)
    packages = create_packages(dependencies, reader.location)
    return packages, []
