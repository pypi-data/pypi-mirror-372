import logging
import re

import pefile  # type: ignore  # noqa: PGH003
import semver
from packageurl import PackageURL
from pydantic import BaseModel

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.utils import get_enriched_location
from labels.utils.strings import normalize_name

LOGGER = logging.getLogger(__name__)


class DotnetPortableExecutableEntry(BaseModel):
    assembly_version: str | None = None
    legal_copyright: str | None = None
    company_name: str | None = None
    product_name: str | None = None
    product_version: str | None = None
    comments: str | None = None
    internal_name: str | None = None


# Define the regular expressions
space_regex = re.compile(r"[\s]+")
number_regex = re.compile(r"\d")
version_punctuation_regex = re.compile(r"[.,]+")


def parse_version_resource(potable: pefile.PE) -> dict[str, str] | None:
    if not hasattr(potable, "VS_VERSIONINFO"):
        return None

    for idx, _ in enumerate(potable.VS_VERSIONINFO):
        if not hasattr(potable, "FileInfo") or len(potable.FileInfo) <= idx:
            continue

        stringtable_dict = process_file_info(
            potable.FileInfo[idx],
        )
        if stringtable_dict:
            return stringtable_dict

    return None


def process_file_info(
    file_info: list[pefile.Structure],
) -> dict[str, str] | None:
    for entry in file_info:
        if not hasattr(entry, "StringTable"):
            continue

        stringtable_dict = process_string_table(entry.StringTable)
        if stringtable_dict:
            return stringtable_dict

    return None


def process_string_table(
    string_table: list[pefile.Structure],
) -> dict[str, str]:
    stringtable_dict = {}
    for st_entry in string_table:
        stringtable_dict["LangID"] = st_entry.LangID
        for key, value in st_entry.entries.items():
            stringtable_dict[key.decode("utf-8")] = value.decode("utf-8")
    return stringtable_dict


def is_microsoft(version_resources: dict[str, str]) -> bool:
    company_name = version_resources.get("CompanyName", "").lower()
    product_name = version_resources.get("ProductName", "").lower()

    return "microsoft" in company_name or "microsoft" in product_name


def space_normalize(value: str) -> str:
    # Trim leading and trailing whitespace
    value = value.strip()

    if value == "":
        return ""

    # Ensure valid UTF-8 text
    value = value.encode("utf-8", "replace").decode("utf-8")

    value = space_regex.sub(" ", value)

    # Remove other non-space, non-printable characters
    value = re.sub(r"[\x00-\x1f]", "", value)

    # Consolidate all space characters again
    value = space_regex.sub(" ", value)

    # Finally, remove any remaining surrounding whitespace
    return value.strip()


def find_name(version_resources: dict[str, str]) -> str:
    # Define the order of fields to check for the name
    name_fields = [
        "ProductName",
        "FileDescription",
        "InternalName",
        "OriginalFilename",
    ]

    # Check if the version resources are from Microsoft
    if is_microsoft(version_resources):
        # Adjust the order of fields for Microsoft-authored files
        name_fields = [
            "FileDescription",
            "InternalName",
            "OriginalFilename",
            "ProductName",
        ]

    # Iterate over the fields to find a non-empty, normalized name
    for field in name_fields:
        value = space_normalize(version_resources.get(field, ""))
        if value:
            return value

    # Return an empty string if no valid name is found
    return ""


def contains_number(string: str) -> bool:
    return any(char.isdigit() for char in string)


def extract_version(version: str) -> str:
    # Trim leading and trailing whitespace
    version = version.strip()

    out = ""

    # Split the version string into fields and iterate over them
    for index, char in enumerate(version.split()):
        # If the output already has a number but the current segment does not,
        # return the output
        if contains_number(out) and not contains_number(char):
            return out

        # Append the current field to the output
        if index == 0:
            out = char
        else:
            out += " " + char

    return out


def keep_greater_semantic_version(product_version: str, file_version: str) -> str:
    try:
        semantic_product_version = semver.VersionInfo.parse(product_version)
    except ValueError:
        LOGGER.debug(
            ("Unable to create semantic version from portable executable product version %s"),
            product_version,
        )
        return ""

    try:
        semantic_file_version = semver.VersionInfo.parse(file_version)
    except ValueError:
        LOGGER.debug(
            ("Unable to create semantic version from portable executable file version %s"),
            file_version,
        )
        return product_version

    # Make no choice when they are semantically equal
    if semantic_product_version == semantic_file_version:
        return ""

    if semantic_file_version > semantic_product_version:
        return file_version

    return product_version


def punctuation_count(string: str) -> int:
    # Find all matches of the punctuation regex and return their count
    return len(version_punctuation_regex.findall(string))


def find_version(version_resources: dict[str, str]) -> str:
    product_version = extract_version(version_resources.get("ProductVersion", ""))
    file_version = extract_version(version_resources.get("FileVersion", ""))

    semantic_version_compare_result = keep_greater_semantic_version(product_version, file_version)

    if semantic_version_compare_result:
        return semantic_version_compare_result

    product_version_detail = punctuation_count(product_version)
    file_version_detail = punctuation_count(file_version)

    if contains_number(product_version) and product_version_detail >= file_version_detail:
        return product_version

    if contains_number(file_version) and file_version_detail > 0:
        return file_version

    if contains_number(product_version):
        return product_version

    if contains_number(file_version):
        return file_version

    return product_version


def build_dot_net_package(
    version_resource: dict[str, str],
    reader: LocationReadCloser,
) -> Package | None:
    name = find_name(version_resource)
    if not name:
        LOGGER.debug(
            "Unable to find name for portable executable in file %s",
            reader.location.path(),
        )
        return None
    version = find_version(version_resource)
    if not version:
        LOGGER.debug(
            "Unable to find version for portable executable in file %s",
            reader.location.path(),
        )
        return None
    metadata = DotnetPortableExecutableEntry(
        assembly_version=version_resource.get("Assembly Version"),
        legal_copyright=version_resource.get("LegalCopyright"),
        comments=version_resource.get("Comments"),
        internal_name=version_resource.get("InternalName"),
        company_name=version_resource.get("CompanyName"),
        product_name=version_resource.get("ProductName"),
        product_version=version_resource.get("ProductVersion"),
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

    new_location = get_enriched_location(reader.location)

    return Package(
        name=normalized_package_name,
        version=version,
        locations=[new_location],
        type=PackageType.DotnetPkg,
        language=Language.DOTNET,
        p_url=p_url,
        metadata=metadata,
        licenses=[],
    )


def parse_dotnet_portable_executable(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    if not reader.location.coordinates:
        return [], []
    try:
        pe_representation = pefile.PE(reader.location.coordinates.real_path, fast_load=False)
    except pefile.PEFormatError:
        return [], []

    version_resource = parse_version_resource(pe_representation)
    if not version_resource:
        LOGGER.debug(
            ("Unable to find version resource for portable executable in file %s"),
            reader.location.path(),
        )
        return [], []
    dotnet_package = build_dot_net_package(version_resource, reader)
    if not dotnet_package:
        LOGGER.debug(
            "Unable to build package for portable executable in file %s",
            reader.location.path(),
        )
        return [], []
    return [dotnet_package], []
