import logging
import zipfile
from collections.abc import Callable
from contextlib import suppress
from fnmatch import fnmatch
from zipfile import BadZipFile, ZipFile, ZipInfo

LOGGER = logging.getLogger(__name__)


def normalize_zip_entry_name(entry: str, *, case_insensitive: bool) -> str:
    if case_insensitive:
        entry = entry.lower()
    if not entry.startswith("/"):
        entry = "/" + entry

    return entry


def new_zip_file_manifest(archive_path: str) -> list[ZipInfo]:
    try:
        with ZipFile(archive_path, "r") as myzip:
            return myzip.infolist()
    except BadZipFile:
        return []


def zip_glob_match(
    manifest: list[ZipInfo],
    *,
    case_sensitive: bool,
    patterns: tuple[str, ...],
) -> list[str]:
    result = []

    for pattern in patterns:
        for entry in manifest:
            normalized_entry = normalize_zip_entry_name(
                entry.filename,
                case_insensitive=case_sensitive,
            )
            if entry.filename.endswith(pattern):
                result.append(entry.filename)
            lower_pattern = pattern.lower() if case_sensitive else pattern
            if fnmatch(normalized_entry, lower_pattern):
                result.append(entry.filename)
    return result


def traverse_files_in_zip(
    archive_path: str,
    visitor: Callable[[zipfile.ZipInfo], None],
    *paths: str,
) -> None:
    """Traverse files in a zip file applying a visitor function to each file."""
    with zipfile.ZipFile(archive_path, "r") as zip_reader:
        for path in paths:
            try:
                visitor(zip_reader.getinfo(path))
            except KeyError:
                LOGGER.exception("Unable to find file: %s", path)


def contents_from_zip(archive_path: str, *paths: str) -> dict[str, str]:
    """Extract specified files from a zip archive and return their contents."""
    results: dict[str, str] = {}

    if not paths:
        return results

    def visitor(file: zipfile.ZipInfo) -> None:
        """Visitor function to read the contents of a file in the zip."""
        if file.is_dir():
            LOGGER.error("Unable to extract directories, only files: %s", file.filename)
            return
        with zipfile.ZipFile(archive_path, "r") as zip_reader, zip_reader.open(file) as file_data:
            content = file_data.read()
            with suppress(UnicodeDecodeError):
                results[file.filename] = content.decode(
                    "utf-8",
                )

    traverse_files_in_zip(archive_path, visitor, *paths)
    return results
