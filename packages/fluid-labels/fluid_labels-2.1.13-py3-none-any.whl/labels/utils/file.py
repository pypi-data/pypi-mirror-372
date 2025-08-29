import tarfile
from contextlib import suppress
from io import TextIOWrapper

from labels.model.file import Coordinates, DependencyType, Location, LocationReadCloser, Scope

# IEC Sizes
BYTE = 1 << (0 * 10)
KIBYTE = 1 << (1 * 10)
MIBYTE = 1 << (2 * 10)
GIBYTE = 1 << (3 * 10)
TIBYTE = 1 << (4 * 10)
PIBYTE = 1 << (5 * 10)
EIBYTE = 1 << (6 * 10)

# SI Sizes
IBYTE = 1
KBYTE = IBYTE * 1000
MBYTE = KBYTE * 1000
GBYTE = MBYTE * 1000
TBYTE = GBYTE * 1000
PBYTE = TBYTE * 1000
EBYTE = PBYTE * 1000

bytes_size_table = {
    "b": BYTE,
    "kib": KIBYTE,
    "kb": KBYTE,
    "mib": MIBYTE,
    "mb": MBYTE,
    "gib": GIBYTE,
    "gb": GBYTE,
    "tib": TIBYTE,
    "tb": TBYTE,
    "pib": PIBYTE,
    "pb": PBYTE,
    "eib": EIBYTE,
    "eb": EBYTE,
    # Without suffix
    "": BYTE,
    "ki": KIBYTE,
    "k": KBYTE,
    "mi": MIBYTE,
    "m": MBYTE,
    "gi": GIBYTE,
    "g": GBYTE,
    "ti": TIBYTE,
    "t": TBYTE,
    "pi": PIBYTE,
    "p": PBYTE,
    "ei": EIBYTE,
    "e": EBYTE,
}


def parse_bytes(size_human: str) -> int:
    last_digit = 0
    has_comma = False

    for i, char in enumerate(size_human):
        if not (char.isdigit() or char in {".", ","}):
            break
        if char == ",":
            has_comma = True
        last_digit = i + 1

    num_str = size_human[:last_digit]
    if has_comma:
        num_str = num_str.replace(",", "")

    try:
        num = float(num_str)
    except ValueError as exc:
        error_message = f"Could not parse number: {num_str}"
        raise ValueError(error_message) from exc

    extra = size_human[last_digit:].strip().lower()
    if extra in bytes_size_table:
        num *= bytes_size_table[extra]
        return int(num)

    error_message = f"Unhandled size name: {extra}"
    raise ValueError(error_message)


def extract_tar_file(tar_path: str, out_path: str) -> None:
    with tarfile.open(tar_path, "r") as tar:
        for member in tar.getmembers():
            member.name = member.name.lstrip("/")
            with suppress(Exception):
                tar.extract(member, path=out_path)


def new_location_from_image(
    access_path: str | None,
    layer_id: str,
    real_path: str | None = None,
) -> Location:
    if access_path and not access_path.startswith("/"):
        access_path = f"/{access_path}"
    return Location(
        coordinates=Coordinates(real_path=real_path or "", file_system_id=layer_id),
        access_path=access_path,
        annotations={},
    )


def new_location(real_path: str) -> Location:
    return Location(
        coordinates=Coordinates(
            real_path=real_path,
        ),
        access_path=real_path,
        annotations={},
    )


def new_default_location_from_path(real_path: str, line: int | None = None) -> Location:
    return Location(
        coordinates=Coordinates(
            real_path=real_path,
            line=line,
        ),
        access_path=real_path,
        annotations={},
        scope=Scope.UNDETERMINABLE,
        dependency_type=DependencyType.UNDETERMINABLE,
        reachable_cves=[],
    )


def new_default_location_read_closer(
    str_path: str, read_closer: TextIOWrapper
) -> LocationReadCloser:
    location = new_default_location_from_path(str_path)
    return LocationReadCloser(location=location, read_closer=read_closer)
