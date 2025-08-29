import logging
import re
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from typing import TextIO, cast

from pydantic import BaseModel, ConfigDict

from labels.model.file import LocationReadCloser
from labels.model.package import Package
from labels.model.relationship import Relationship, RelationshipType
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.debian.model import DpkgDBEntry
from labels.parsers.cataloger.debian.package import new_dpkg_package
from labels.parsers.cataloger.debian.parse_dpkg_info_files import parse_dpkg_conffile_info
from labels.utils.file import parse_bytes

LOGGER = logging.getLogger(__name__)


class DpkgField(BaseModel):
    name: str
    value: str
    model_config = ConfigDict(frozen=True)


def _split_deps(value: str) -> list[str]:
    fields = value.split(",")
    return [field.strip() for field in fields if field.strip()]


def extract_source_version(source: str) -> tuple[str, str | None]:
    if match_result := re.compile(r"(?P<name>\S+)( \((?P<version>.*)\))?").match(source):
        result = match_result.groupdict()
        return result["name"], result["version"] or ""
    return source, ""


def handle_new_key_value(line: str) -> tuple[str | None, str]:
    if ":" in line and not line.startswith(" "):
        key, value = line.split(":", 1)
        value = value.strip()
        match key:
            case "Installed-Size":
                value = str(parse_bytes(value))
        return key, value

    return None, line


def parse_dpkg_status(reader: TextIO) -> list[DpkgDBEntry]:
    content = reader.read()
    entries = []
    for package in content.strip().split("\n\n"):
        lines = package.split("\n")
        data = {}
        prev_key = ""
        for line in lines:
            try:
                key, value = handle_new_key_value(line)
            except ValueError:
                LOGGER.exception("Value error occurred")
                continue
            if key is not None:
                data[key] = value
                prev_key = key
            elif prev_key in data:
                data[prev_key] = f"{data[prev_key]}\n{value}"
        if all(not value for value in data.values()):
            continue
        source_name, source_version = extract_source_version(data.get("Source", ""))
        entry = DpkgDBEntry(
            package=data.get("Package", ""),
            source=source_name,
            version=data.get("Version", ""),
            source_version=source_version or "",
            architecture=data.get("Architecture", ""),
            maintainer=data.get("Maintainer", ""),
            installed_size=int(data.get("Installed-Size", "0")),
            description=data.get("Description", "").strip(),
            provides=_split_deps(data.get("Provides", "")),
            dependencies=_split_deps(data.get("Depends", "")),
            pre_dependencies=_split_deps(data.get("Pre-Depends", "")),
            files=parse_dpkg_conffile_info(data.get("Conffiles", "")),
        )
        entries.append(entry)

    return entries


def parse_dpkg_db(
    resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    entries: list[DpkgDBEntry] = parse_dpkg_status(reader.read_closer)
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        result = [
            pkg if isinstance(pkg, Package) else (pkg[0], pkg[1])
            for pkg in filter(
                None,
                executor.map(
                    lambda entry: new_dpkg_package(
                        entry,
                        reader.location,
                        resolver,
                        _env.linux_release if _env else None,
                    ),
                    entries,
                ),
            )
            if isinstance(pkg, Package | tuple)
        ]
        packages = [item for pkg in result for item in (pkg if isinstance(pkg, tuple) else [pkg])]
    return packages, associate_relationships(packages)


def associate_relationships(
    pkgs: list[Package],
) -> list[Relationship]:
    lookup: dict[str, list[Package]] = {}
    relationships: list[Relationship] = []
    for pkg in pkgs:
        lookup.setdefault(pkg.name, []).append(pkg)
    for pkg in pkgs:
        metadata = cast("DpkgDBEntry", pkg.metadata)
        for provides in metadata.provides or []:
            key = strip_version_specifier(provides)
            lookup.setdefault(key, []).append(pkg)

    for pkg in pkgs:
        metadata = cast("DpkgDBEntry", pkg.metadata)
        all_deps = [
            *(metadata.dependencies or []),
            *(metadata.pre_dependencies or []),
        ]
        for dep_specifier in all_deps:
            deps = split_package_choices(dep_specifier)
            for dep in deps:
                relationships.extend(
                    Relationship(
                        from_=dep_pkg.id_,
                        to_=pkg.id_,
                        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                    )
                    for dep_pkg in lookup.get(dep, [])
                )

    return relationships


def strip_version_specifier(item: str) -> str:
    # Define the characters that indicate the start of a version specifier
    specifiers = "[(<>="

    # Find the index of the first occurrence of any specifier character
    index = next((i for i, char in enumerate(item) if char in specifiers), None)

    # If no specifier character is found, return the original string
    if index is None:
        return item.strip()

    # Return the substring up to the first specifier character, stripped of
    # leading/trailing whitespace
    return item[:index].strip()


def split_package_choices(value: str) -> list[str]:
    fields = value.split("|")
    return [strip_version_specifier(field) for field in fields if field.strip()]
