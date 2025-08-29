from typing import TextIO

from labels.model.package import Digest
from labels.parsers.cataloger.debian.model import DpkgFileRecord


def parse_dpkg_md5_info(reader: TextIO) -> list[DpkgFileRecord]:
    result: list[DpkgFileRecord] = []
    for raw_line in reader:
        line = raw_line.rstrip("\n")

        fields = line.split("  ", 2)
        if len(fields) != 2:
            continue
        path = fields[1].strip()
        if not path.startswith("/"):
            path = f"/{path}"
        result.append(
            DpkgFileRecord(
                path=path,
                digest=Digest(algorithm="md5", value=fields[0].strip()),
            ),
        )
    return result


def _split_lines(reader: TextIO | str) -> list[str]:
    # Convert the input reader to a list of lines
    return reader.splitlines() if isinstance(reader, str) else reader.readlines()


def _process_line(line: str) -> tuple[str, Digest | None]:
    # Process a single line to extract the file path and digest
    line = line.rstrip("\n").strip()
    if not line:
        return "", None

    fields = line.split(" ", 2)
    path = fields[0].strip() if len(fields) >= 1 else ""
    if path and not path.startswith("/"):
        path = f"/{path}"

    digest = Digest(algorithm="md5", value=fields[1].strip()) if len(fields) >= 2 else None
    return path, digest


def _create_record(path: str, digest: Digest | None) -> DpkgFileRecord | None:
    # Create a DpkgFileRecord object if the path is valid
    if not path:
        return None
    record = DpkgFileRecord(path=path, is_config_file=True)
    if digest:
        record.digest = digest
    return record


def parse_dpkg_conffile_info(
    reader: TextIO | str,
) -> list[DpkgFileRecord]:
    # Parse the dpkg conffile information from the reader
    result: list[DpkgFileRecord] = []
    for line in _split_lines(reader):
        path, digest = _process_line(line)
        record = _create_record(path, digest)
        if record:
            result.append(record)
    return result
