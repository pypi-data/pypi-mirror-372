import logging
import os
import stat
import tempfile
import zipfile
from pathlib import Path

from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.java.model import JavaArchive, JavaPomProperties
from labels.parsers.cataloger.java.package import package_url
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning

LOGGER = logging.getLogger(__name__)


def is_safe_path(base_path: str, target_path: str) -> bool:
    base_path = os.path.normpath(base_path)
    target_path = os.path.normpath(target_path)
    return os.path.commonpath([base_path]) == os.path.commonpath([base_path, target_path])


def safe_extract(apk_file: zipfile.ZipFile, destination: str) -> None:
    for file_info in apk_file.infolist():
        file_name = file_info.filename
        if Path(file_name).is_absolute() or file_name.startswith(("..", "./")):
            continue

        target_path = Path(destination, file_name)

        if not is_safe_path(destination, str(target_path)):
            continue

        if (file_info.external_attr >> 16) & stat.S_IFLNK:
            continue

        try:
            apk_file.extract(file_name, destination)
        except Exception:
            LOGGER.exception("Error extracting %s", file_name)


def parse_apk(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    with tempfile.TemporaryDirectory() as output_folder:
        try:
            with zipfile.ZipFile(reader.read_closer.name, "r") as apk_file:
                safe_extract(apk_file, output_folder)
        except zipfile.BadZipFile:
            return packages, []
        files_paths: list[Path] = []
        meta_dir_path = Path(output_folder) / "META-INF"
        if meta_dir_path.exists():
            files_paths = [
                file_path
                for file_path in meta_dir_path.iterdir()
                if file_path.name.endswith(".version")
            ]
        for file_path in files_paths:
            with file_path.open(encoding="utf-8") as version_reader:
                version = version_reader.read().strip()
            parts = file_path.name.replace(".version", "").split("_", 1)
            group_id = parts[0]
            artifact_id = parts[1]

            if any(not value for value in (artifact_id, version, group_id)):
                continue

            java_archive = JavaArchive(
                pom_properties=JavaPomProperties(
                    group_id=group_id,
                    artifact_id=artifact_id,
                    version=version,
                ),
            )

            new_location = get_enriched_location(reader.location)

            try:
                packages.append(
                    Package(
                        name=f"{group_id}:{artifact_id}",
                        version=version,
                        licenses=[],
                        locations=[new_location],
                        language=Language.JAVA,
                        type=PackageType.JavaPkg,
                        metadata=java_archive,
                        p_url=package_url(artifact_id, version, java_archive),
                    ),
                )
            except ValidationError as ex:
                log_malformed_package_warning(new_location, ex)
                continue

    return packages, []
