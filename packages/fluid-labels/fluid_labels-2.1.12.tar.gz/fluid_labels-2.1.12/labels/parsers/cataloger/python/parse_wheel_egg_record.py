from pathlib import Path
from typing import TextIO

from labels.parsers.cataloger.python.model import PythonFileDigest, PythonFileRecord


def parse_wheel_or_egg_record(reader: TextIO) -> list[PythonFileRecord]:
    file_records = []
    lines = reader.read().strip().split("\n")
    for line in lines:
        parts = line.split(",")
        if len(parts) != 3:
            continue  # Skip invalid lines

        path = parts[0]
        digest_part = parts[1].split("=")
        if len(digest_part) != 2:
            continue  # Skip invalid digest format

        algorithm = digest_part[0]
        value = digest_part[1]
        size = int(parts[2])

        digest = PythonFileDigest(algorithm=algorithm, value=value)
        record = PythonFileRecord(path=path, digest=digest, size=str(size))
        file_records.append(record)

    return file_records


def parse_installed_files(
    reader: TextIO,
    location: str,
    site_packages_root_path: str,
) -> list[PythonFileRecord]:
    installed_files = []
    for raw_line in reader:
        line = raw_line.rstrip("\n")
        if location and site_packages_root_path:
            joined_path = Path(location).parent / line
            line = str(Path(site_packages_root_path, joined_path).resolve())
        installed_record = PythonFileRecord(path=line)
        installed_files.append(installed_record)

    return installed_files
