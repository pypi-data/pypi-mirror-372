import re

from bs4 import BeautifulSoup, Tag
from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning
from labels.utils.strings import normalize_name

PACKAGE = re.compile(r".+\\packages\\(?P<package_info>[^\s\\]*)\\.+")
DEP_INFO = re.compile(r"(?P<package_name>.*?)\.(?P<version>\d+[^\s]*)$")


def _get_version(include_info: list[str]) -> str | None:
    return next(
        (
            pkg_info.lstrip("Version=")
            for pkg_info in include_info
            if pkg_info.startswith("Version=")
        ),
        None,
    )


def format_package(
    name: str,
    version: str,
    line: int,
    reader: LocationReadCloser,
    *,
    is_dev: bool | None = None,
) -> Package | None:
    new_location = get_enriched_location(
        reader.location, line=line, is_transitive=False, is_dev=is_dev
    )

    normalized_package_name = normalize_name(name, PackageType.DotnetPkg)
    p_url = PackageURL(
        type="nuget",
        namespace="",
        name=normalized_package_name,
        version=version,
        qualifiers={},
        subpath="",
    ).to_string()

    try:
        return Package(
            name=normalized_package_name,
            version=version,
            locations=[new_location],
            language=Language.DOTNET,
            licenses=[],
            type=PackageType.DotnetPkg,
            metadata=None,
            p_url=p_url,
        )
    except ValidationError as ex:
        log_malformed_package_warning(new_location, ex)

    return None


def _format_csproj_reference_deps(root: BeautifulSoup, reader: LocationReadCloser) -> list[Package]:
    packages = []
    for pkg in root.find_all("reference", recursive=True):
        if dll_path := pkg.find("hintpath"):
            package = PACKAGE.match(dll_path.text)
            if (
                package
                and (pkg_info := DEP_INFO.match(package.group("package_info")))
                and (
                    pkg := format_package(
                        str(pkg_info.group("package_name").lower()),
                        str(pkg_info.group("version")),
                        dll_path.sourceline,
                        reader,
                    )
                )
            ):
                packages.append(pkg)
        elif (include := pkg.get("include")) and (
            include_info := include.replace(" ", "").split(",")
        ):
            version = _get_version(include_info)
            if version and (
                pkg := format_package(
                    str(include_info[0]).strip(),
                    str(version),
                    pkg.sourceline,
                    reader,
                )
            ):
                packages.append(pkg)

    return packages


def _is_dev_dependency(pkg: BeautifulSoup) -> bool:
    checking_attr = "all"

    element = pkg.find("privateassets")
    if isinstance(element, Tag):
        return element.get_text(strip=True).lower() == checking_attr

    attr = pkg.get("privateassets")
    if isinstance(attr, str):
        return attr.strip().lower() == checking_attr

    return False


def parse_csproj(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    root = BeautifulSoup(reader.read_closer.read(), features="html.parser")

    for pkg in root.find_all("packagereference", recursive=True):
        package_name = pkg.get("include")
        version = pkg.get("version")

        if not package_name or not version:
            continue

        is_dev = _is_dev_dependency(pkg)

        package = format_package(package_name, version, pkg.sourceline, reader, is_dev=is_dev)
        if package:
            packages.append(package)

    packages.extend(_format_csproj_reference_deps(root, reader))

    return packages, []
