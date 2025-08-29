import logging
from collections.abc import Callable
from typing import cast

from pydantic import ValidationError

import labels.enrichers.alpine.complete as enrich_alpine
import labels.enrichers.dart.complete as enrich_dart
import labels.enrichers.debian.complete as enrich_debian
import labels.enrichers.dotnet.complete as enrich_dotnet
import labels.enrichers.elixir.complete as enrich_elixir
import labels.enrichers.golang.complete as enrich_go
import labels.enrichers.java.complete as enrich_java
import labels.enrichers.javascript.complete as enrich_js
import labels.enrichers.php.complete as enrich_php
import labels.enrichers.python.complete as enrich_python
import labels.enrichers.ruby.complete as enrich_ruby
import labels.enrichers.rust.complete as enrich_rust
from labels.advisories import images as images_advisories
from labels.advisories import roots as roots_advisories
from labels.model.advisories import Advisory
from labels.model.file import Location
from labels.model.package import HealthMetadata, Language, Package, PackageType
from labels.parsers.cataloger.utils import extract_distro_info
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)


ROOT_TYPES: set[PackageType] = {
    PackageType.NpmPkg,
    PackageType.DartPubPkg,
    PackageType.DotnetPkg,
    PackageType.JavaPkg,
    PackageType.PhpComposerPkg,
    PackageType.PythonPkg,
    PackageType.GemPkg,
    PackageType.RustPkg,
    PackageType.GoModulePkg,
    PackageType.HexPkg,
    PackageType.ConanPkg,
    PackageType.GithubActionPkg,
    PackageType.SwiftPkg,
}

IMAGES_TYPES: set[PackageType] = {
    PackageType.DebPkg,
    PackageType.ApkPkg,
}

COMPLETION_MAP: dict[PackageType, Callable[[Package], Package]] = {
    PackageType.NpmPkg: enrich_js.complete_package,
    PackageType.DartPubPkg: enrich_dart.complete_package,
    PackageType.DotnetPkg: enrich_dotnet.complete_package,
    PackageType.JavaPkg: enrich_java.complete_package,
    PackageType.PhpComposerPkg: enrich_php.complete_package,
    PackageType.PythonPkg: enrich_python.complete_package,
    PackageType.GemPkg: enrich_ruby.complete_package,
    PackageType.RustPkg: enrich_rust.complete_package,
    PackageType.GoModulePkg: enrich_go.complete_package,
    PackageType.HexPkg: enrich_elixir.complete_package,
    PackageType.DebPkg: enrich_debian.complete_package,
    PackageType.ApkPkg: enrich_alpine.complete_package,
}

ALLOWED_TYPE = dict[
    str,
    str
    | Language
    | list[str]
    | list[Location]
    | PackageType
    | list[Advisory]
    | list[Package]
    | HealthMetadata
    | bool
    | object
    | None,
]


def update_root_advisories(package: Package) -> list[Advisory]:
    if pkg_platform := package.type.get_platform_value():
        return roots_advisories.get_vulnerabilities(
            pkg_platform.lower(),
            package.name,
            package.version,
        )
    return []


def _get_upstream_info(package: Package) -> tuple[str | None, str | None]:
    if (
        package.type == PackageType.ApkPkg
        and package.metadata
        and hasattr(package.metadata, "origin_package")
        and package.metadata.origin_package
    ):
        return package.metadata.origin_package, package.version

    if (
        package.type == PackageType.DebPkg
        and package.metadata
        and hasattr(package.metadata, "source")
        and hasattr(package.metadata, "source_version")
        and package.metadata.source
    ):
        return package.metadata.source, package.metadata.source_version or package.version

    if (
        package.type == PackageType.AlpmPkg
        and package.metadata
        and hasattr(package.metadata, "base_package")
        and package.metadata.base_package
    ):
        return package.metadata.base_package, package.version

    if (
        package.type == PackageType.RpmPkg
        and package.metadata
        and hasattr(package.metadata, "source_rpm")
        and package.metadata.source_rpm
    ):
        source_name = package.metadata.source_rpm.replace(".src.rpm", "").split("-")[0]
        return source_name, package.version

    return None, None


def update_image_advisories(package: Package) -> list[Advisory]:
    distro_id, distro_version, _ = extract_distro_info(package.p_url)
    distro_version = (
        "v" + ".".join(str(distro_version).split(".")[0:2])
        if package.type == PackageType.ApkPkg
        else str(distro_version)
    )

    upstream_package, upstream_version = _get_upstream_info(package)

    return images_advisories.get_vulnerabilities(
        str(distro_id),
        package.name,
        package.version,
        distro_version,
        (upstream_package, upstream_version),
    )


def add_package_advisories(package: Package) -> list[Advisory] | None:
    try:
        pkg_advisories = []
        if package.type in ROOT_TYPES:
            pkg_advisories = update_root_advisories(package)
        if package.type in IMAGES_TYPES:
            pkg_advisories = update_image_advisories(package)
    except ValidationError as ex:
        LOGGER.exception(
            "Unable to complete package advisories",
            extra={
                "extra": {
                    "exception": format_exception(str(ex)),
                    "location": package.locations,
                    "package_type": package.type,
                },
            },
        )
        return None
    return pkg_advisories


def complete_package_advisories_only(package: Package) -> Package:
    if pkg_advisories := add_package_advisories(package):
        package.advisories = pkg_advisories
    return package


def complete_package(package: Package) -> Package:
    try:
        if pkg_advisories := add_package_advisories(package):
            package.advisories = pkg_advisories

        completed_package = None
        if package.type in COMPLETION_MAP:
            try:
                completed_package = COMPLETION_MAP[package.type](package)

            except Exception as ex:
                LOGGER.exception(
                    "Unable to complete package",
                    extra={
                        "extra": {
                            "exception": format_exception(str(ex)),
                            "location": package.locations,
                            "package_type": package.type,
                        },
                    },
                )
                return package
        if completed_package:
            completed_package.model_validate(
                cast("ALLOWED_TYPE", package.__dict__),
            )
    except ValidationError:
        LOGGER.warning(
            "Malformed package metadata completion. "
            "Required fields are missing or data types are incorrect.",
        )
        return package

    return completed_package if completed_package is not None else package
