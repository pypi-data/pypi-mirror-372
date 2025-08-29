import json
from fnmatch import fnmatch
from pathlib import Path
from typing import TextIO, cast

from pydantic import BaseModel

from labels.model.file import Location
from labels.model.indexables import ParsedValue
from labels.parsers.cataloger.python.model import PythonPackage


class ParsedData(BaseModel):
    licenses: str
    license_file: str | list[str]
    license_expresion: str
    license_location: Location | None
    python_package: PythonPackage


def determine_site_package_root_package(path: str) -> str:
    if any(fnmatch(path, pattern) for pattern in ("**/*.egg-info", "**/*.dist-info")):
        return str(Path(path).parent)
    return str(Path(path).parent.parent)


def _split_lines(data: str) -> list[str]:
    # Split the input data into lines
    return data.strip().split("\n")


def _handle_multiline_values(
    line: str,
    multi_line_key: str,
    parsed_data: dict[str, str | list[str]],
) -> str:
    # Append multiline values to the corresponding key
    if multi_line_key and isinstance(parsed_data[multi_line_key], str):
        parsed_data[multi_line_key] += "\n" + line.strip()  # type: ignore[operator]
    return multi_line_key


def _update_parsed_data(key: str, value: str, parsed_data: dict[str, str | list[str]]) -> None:
    # Update the parsed data dictionary with new or existing keys
    if key in parsed_data:
        if isinstance(parsed_data[key], list):
            parsed_data[key].append(value)  # type: ignore[union-attr]
        else:
            parsed_data[key] = [parsed_data[key], value]  # type: ignore[list-item]
    else:
        parsed_data[key] = value


def _process_line(line: str, parsed_data: dict[str, str | list[str]]) -> str:
    # Process each line, updating the parsed data and handling multiline values
    multi_line_key = None
    if ": " in line:
        key, value = line.split(": ", 1)
        _update_parsed_data(key, value, parsed_data)
        if key in ["Description", "Classifier"]:
            multi_line_key = key
    return multi_line_key or ""


def parse_metadata(data: str) -> dict[str, str | list[str]]:
    parsed_data: dict[str, str | list[str]] = {}
    lines = _split_lines(data)
    multi_line_key: str | None = None
    for line in lines:
        if not line:
            break
        if multi_line_key and line.startswith((" ", "\t")):
            multi_line_key = _handle_multiline_values(line, multi_line_key, parsed_data)
        else:
            multi_line_key = _process_line(line, parsed_data)
    return parsed_data


def required_dependencies(
    requires_dis: list[str] | str,
    provides_extra: list[str] | None = None,
) -> list[str]:
    if isinstance(requires_dis, str):
        requires_dis = [requires_dis]
    result: list[str] = []
    provides_extra = provides_extra or []
    for item in requires_dis:
        parts = item.split(";")
        if any(x in parts[-1] for x in provides_extra):
            continue
        result.append(parts[0].strip())
    return result


def _handle_platform(input_value: ParsedValue) -> str | None:
    if isinstance(input_value, list | dict):
        return json.dumps(input_value)
    if isinstance(input_value, str):
        return input_value
    return None


def parse_wheel_or_egg_metadata(path: str, reader: TextIO) -> ParsedData | None:
    metadata_dict: dict[str, str] = cast("dict[str, str]", parse_metadata(reader.read()))
    p_data = ParsedData(
        python_package=PythonPackage(
            name=metadata_dict.get("Name", ""),
            version=metadata_dict.get("Version", ""),
            author=metadata_dict.get("Author"),
            author_email=metadata_dict.get("Author-email"),
            platform=_handle_platform(metadata_dict.get("Platform")),
            site_package_root_path=determine_site_package_root_package(path),
            files=None,
            top_level_packages=None,
            direct_url_origin=None,
            dependencies=required_dependencies(
                cast("list[str]", metadata_dict["Requires-Dist"]),
                cast("list[str] | None", metadata_dict.get("Provides-Extra")),
            )
            if "Requires-Dist" in metadata_dict
            else None,
        ),
        licenses=metadata_dict.get("License", ""),
        license_expresion=metadata_dict.get("License-Expression", ""),
        license_file=metadata_dict.get("License-File", ""),
        license_location=None,
    )

    if p_data.license_expresion or p_data.licenses:
        p_data.license_file = path
        p_data.license_location = Location(
            access_path=path,
        )
    elif p_data.license_file and isinstance(p_data.license_file, str):
        p_data.license_location = Location(
            access_path=str(Path(path).parent / p_data.license_file),
        )
    return p_data
