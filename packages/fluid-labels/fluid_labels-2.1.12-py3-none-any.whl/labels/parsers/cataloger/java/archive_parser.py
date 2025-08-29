import hashlib
import logging
import shutil
import tempfile
from collections.abc import Callable
from io import BufferedReader
from pathlib import Path
from typing import TextIO, cast
from zipfile import ZipInfo

from pydantic import BaseModel, ConfigDict, ValidationError

from labels.model.file import Location, LocationReadCloser
from labels.model.package import Digest, Language, Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.java.archive_filename import ArchiveFilename, parse_filename
from labels.parsers.cataloger.java.model import (
    JavaArchive,
    JavaManifest,
    JavaPomProject,
    JavaPomProperties,
)
from labels.parsers.cataloger.java.package import group_id_from_java_metadata, package_url
from labels.parsers.cataloger.java.parse_java_manifest import (
    parse_java_manifest,
    select_licenses,
    select_name,
    select_version,
)
from labels.parsers.cataloger.java.parse_pom_properties import parse_pom_properties
from labels.parsers.cataloger.java.parse_pom_xml import ParsedPomProject, parse_pom_xml_project
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning
from labels.utils.licenses import parser
from labels.utils.zip import contents_from_zip, new_zip_file_manifest, zip_glob_match

LOGGER = logging.getLogger(__name__)


def new_digests_from_file(file_object: BufferedReader, hashes: list[str]) -> list[Digest]:
    hash_objects = [hashlib.new(hash_key, usedforsecurity=False) for hash_key in hashes]

    while chunk := file_object.read(4096):
        for hasher in hash_objects:
            hasher.update(chunk)

    if file_object.tell() == 0:
        return []

    return [
        Digest(
            algorithm=hash_name,
            value=hasher.hexdigest(),
        )
        for hash_name, hasher in zip(hashes, hash_objects, strict=False)
    ]


def get_digests_from_archive(archive_path: str) -> list[Digest]:
    with Path(archive_path).open("rb") as reader:
        return new_digests_from_file(reader, ["sha1"])


def pom_properties_by_parent(
    archive_path: str,
    extract_paths: list[str],
) -> dict[str, JavaPomProperties]:
    properties_by_parent_path = {}
    contents_of_maven_properties = contents_from_zip(archive_path, *extract_paths)

    for file_path, file_contents in contents_of_maven_properties.items():
        if not file_contents:
            continue
        pom_properties = parse_pom_properties(file_path, file_contents)
        if not pom_properties:
            continue
        if not pom_properties.group_id or not pom_properties.version:
            continue
        properties_by_parent_path[str(Path(file_path).parent)] = pom_properties

    return properties_by_parent_path


def pom_project_by_parent(
    archive_path: str,
    location: Location,
    extract_paths: list[str],
) -> dict[str, ParsedPomProject]:
    contents_of_maven_project = contents_from_zip(archive_path, *extract_paths)

    project_by_parent = {}

    for file_path, file_contents in contents_of_maven_project.items():
        pom_project = parse_pom_xml_project(file_path, file_contents, location)
        if not pom_project:
            continue
        if (
            not pom_project.java_pom_project.parent and not pom_project.java_pom_project.version
        ) or not pom_project.java_pom_project.artifact_id:
            continue

        project_by_parent[str(Path(file_path).parent)] = pom_project

    return project_by_parent


def artifact_id_matches_filename(artifact_id: str, filename: str) -> bool:
    if not artifact_id or not filename:
        return False

    return artifact_id.startswith(filename) or filename.startswith(artifact_id)


class ArchiveParser(BaseModel):
    file_manifest: list[ZipInfo]
    location: Location
    archive_path: str | None
    content_path: str
    file_info: ArchiveFilename
    detect_nested: bool
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def parse(self) -> tuple[list[Package] | None, list[Relationship] | None]:
        packages = []
        parent_pkg = self.discover_main_package()
        if not parent_pkg:
            return None, None
        aux_pkgs = self.discover_pkgs_from_all_maven_files(parent_pkg)

        packages = [parent_pkg, *aux_pkgs]

        return packages, []

    def discover_pkgs_from_all_maven_files(self, parent_pkg: Package | None) -> list[Package]:
        if not parent_pkg or not self.archive_path:
            return []

        pkgs: list[Package] = []

        properties = pom_properties_by_parent(
            self.archive_path,
            zip_glob_match(self.file_manifest, case_sensitive=False, patterns=("*pom.properties",)),
        )

        projects = pom_project_by_parent(
            self.archive_path,
            self.location,
            zip_glob_match(self.file_manifest, case_sensitive=False, patterns=("*pom.xml",)),
        )

        for parent_path, properties_obj in properties.items():
            pom_project: ParsedPomProject | None = projects.get(parent_path, None)
            if pkg_from_pom := new_package_from_maven_data(
                properties_obj,
                pom_project,
                parent_pkg,
                self.location,
            ):
                pkgs.append(pkg_from_pom)
        return pkgs

    def discover_main_package(self) -> Package | None:
        manifest_matches = zip_glob_match(
            self.file_manifest,
            case_sensitive=False,
            patterns=("/META-INF/MANIFEST.MF",),
        )
        if not manifest_matches or not self.archive_path:
            return None
        contents = contents_from_zip(self.archive_path, *manifest_matches)
        if not contents:
            return None

        manifest_contents = contents[manifest_matches[0]]
        manifest = parse_java_manifest(manifest_contents)
        licenses_, name, version, group_id = self.parse_licenses(manifest)
        metadata = JavaArchive(
            virtual_path=self.location.path(),
            manifest=manifest,
            archive_digests=get_digests_from_archive(self.archive_path),
        )

        if not name or not version:
            return None

        new_location = get_enriched_location(self.location)

        try:
            return Package(
                name=f"{group_id}:{name}",
                version=version,
                licenses=licenses_,
                locations=[new_location],
                type=self.file_info.pkg_type(),
                language=Language.JAVA,
                metadata=metadata,
                p_url=package_url(name, version, metadata),
            )
        except ValidationError as ex:
            log_malformed_package_warning(new_location, ex)
            return None

    def get_license_from_file_in_archive(self) -> list[str]:
        file_licenses = []
        for filename in parser.LICENSES_FILE_NAMES:
            license_matches = zip_glob_match(
                self.file_manifest,
                case_sensitive=True,
                patterns=(f"/META-INF/{filename}",),
            )
            if not license_matches:
                license_matches = zip_glob_match(
                    self.file_manifest,
                    case_sensitive=True,
                    patterns=(f"/{filename}",),
                )

            if license_matches and self.archive_path:
                contents = contents_from_zip(self.archive_path, *license_matches)
                for license_match in license_matches:
                    license_contents = contents.get(license_match, "")

                    parsed = parser.parse_license(license_contents)
                    if parsed:
                        file_licenses.extend(parsed)

        return file_licenses

    def parse_licenses(self, manifest: JavaManifest) -> tuple[list[str], str, str, str]:
        licenses_ = select_licenses(manifest)
        (
            name,
            version,
            pom_licenses,
            group_id,
        ) = self.guess_main_package_name_and_version_from_pom()

        if not name:
            name = select_name(manifest, self.file_info)
        if not version:
            version = select_version(manifest, self.file_info)
        if not group_id:
            group_id = select_name(manifest, self.file_info)

        if not licenses_:
            licenses_.extend(pom_licenses or [])

        if not licenses_:
            file_licenses = self.get_license_from_file_in_archive()
            if file_licenses:
                licenses_.extend(file_licenses)
        return licenses_, name, version, group_id

    def extract_properties_and_projects(
        self,
    ) -> tuple[dict[str, JavaPomProperties], dict[str, ParsedPomProject]]:
        properties = {}
        projects = {}

        pom_property_matches = zip_glob_match(
            self.file_manifest,
            case_sensitive=False,
            patterns=("*pom.properties",),
        )
        pom_matches = zip_glob_match(
            self.file_manifest,
            case_sensitive=False,
            patterns=("*pom.xml",),
        )
        if self.archive_path:
            properties = pom_properties_by_parent(self.archive_path, pom_property_matches)
            projects = pom_project_by_parent(self.archive_path, self.location, pom_matches)

        return properties, projects

    def find_relevant_objects(
        self,
        properties: dict[str, JavaPomProperties],
        projects: dict[str, ParsedPomProject],
    ) -> tuple[JavaPomProperties | None, ParsedPomProject | None]:
        for parent_path, properties_obj in properties.items():
            if (
                properties_obj.artifact_id
                and artifact_id_matches_filename(properties_obj.artifact_id, self.file_info.name)
                and (proj := projects.get(parent_path))
            ):
                return properties_obj, proj
        return None, None

    def extract_name_version(
        self,
        properties_obj: JavaPomProperties,
        project_obj: ParsedPomProject,
    ) -> tuple[str | None, str | None, str | None]:
        name = properties_obj.artifact_id if properties_obj else None
        version = properties_obj.version if properties_obj else None
        group_id = properties_obj.group_id if properties_obj else None

        if not name and project_obj:
            name = project_obj.java_pom_project.artifact_id
        if not version and project_obj:
            version = project_obj.java_pom_project.version
        if not group_id and project_obj:
            group_id = project_obj.java_pom_project.group_id

        return name, version, group_id

    def guess_main_package_name_and_version_from_pom(
        self,
    ) -> tuple[str | None, str | None, list[str] | None, str | None]:
        properties, projects = self.extract_properties_and_projects()
        properties_obj, project_obj = self.find_relevant_objects(properties, projects)

        if not properties_obj or not project_obj:
            return None, None, None, None

        name, version, group_id = self.extract_name_version(properties_obj, project_obj)

        return name, version, [], group_id


def save_archive_to_tmp(
    archive_virtual_path: str,
    _reader: TextIO,
) -> tuple[str | None, str | None, Callable[[], None]]:
    name = Path(archive_virtual_path).name
    temp_dir = tempfile.mkdtemp(prefix="sbom-archive-contents-")

    def cleanup_fn() -> None:
        shutil.rmtree(temp_dir)

    content_dir = Path(temp_dir, "contents")
    content_dir.mkdir()

    archive_path = Path(temp_dir, f"archive-{name}")
    shutil.copy(archive_virtual_path, archive_path)

    return str(content_dir), str(archive_path), cleanup_fn


def new_java_archive_parser(
    reader: LocationReadCloser,
    *,
    detect_nested: bool,
) -> tuple[ArchiveParser | None, Callable[[], None] | None]:
    if not reader.location.coordinates:
        return None, None
    current_file_path = reader.location.coordinates.real_path
    content_path, archive_path, cleanup_fn = save_archive_to_tmp(
        current_file_path,
        reader.read_closer,
    )
    if not archive_path or not content_path:
        LOGGER.error("unable to read files from java archive")
        return None, None

    file_info = parse_filename(current_file_path)
    file_manifest = new_zip_file_manifest(archive_path)
    return (
        ArchiveParser(
            file_manifest=file_manifest,
            location=reader.location,
            archive_path=archive_path,
            content_path=content_path,
            file_info=file_info,
            detect_nested=detect_nested,
        ),
        cleanup_fn,
    )


def parse_java_archive(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    parser, _file_cleanup_fn = new_java_archive_parser(reader, detect_nested=True)
    if parser is None:
        return [], []

    pkgs, relations = parser.parse()
    return pkgs or [], relations or []


def new_package_from_maven_data(
    pom_properties: JavaPomProperties,
    _parsed_pom_project: ParsedPomProject | None,
    parent_pkg: Package,
    location: Location,
) -> Package | None:
    artifact_id = pom_properties.artifact_id
    version = pom_properties.version

    if not artifact_id or not version:
        return None
    full_name = f"{pom_properties.group_id}:{artifact_id}"
    v_path_suffix = ""

    parent_metadata: JavaArchive = cast("JavaArchive", parent_pkg.metadata)
    group_id = group_id_from_java_metadata(parent_pkg.name, parent_metadata)
    parent_key = f"{group_id}:{parent_pkg.name}:{parent_pkg.version}"
    pom_project_key = f"{full_name}:{version}"

    if parent_key != pom_project_key:
        v_path_suffix += f":{full_name}"

    virtual_path = f"{location.path()}{v_path_suffix}"
    pkg_pom_project: JavaPomProject | None = None

    metadata = JavaArchive(
        virtual_path=virtual_path,
        pom_properties=pom_properties,
        pom_project=pkg_pom_project,
        parent=parent_pkg,
    )

    new_location = get_enriched_location(location)

    try:
        return Package(
            name=full_name,
            version=version,
            licenses=[],
            locations=[new_location],
            type=pom_properties.pkg_type_indicated(),
            language=Language.JAVA,
            metadata=metadata,
            p_url=package_url(artifact_id, version, metadata),
        )
    except ValidationError as ex:
        log_malformed_package_warning(new_location, ex)
        return None
