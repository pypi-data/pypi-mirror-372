import unicodedata

from labels.parsers.cataloger.java.archive_filename import ArchiveFilename
from labels.parsers.cataloger.java.model import JavaManifest


def parse_line(
    line: str,
    last_key: str,
    current_section: int,
    sections: list[dict[str, str]],
) -> str:
    line = line.strip()

    # Handle new key-value pairs
    idx = line.find(":")
    if idx == -1:
        return last_key

    key = line[:idx].strip()
    value = line[idx + 1 :].strip()

    if not key:
        return last_key

    if last_key == "" or current_section == -1:
        sections.append({})
        current_section += 1

    sections[current_section][key] = value
    return key


def process_section(sections: list[dict[str, str]], reader: str) -> None:
    current_section = -1
    last_key = ""

    for line in reader.splitlines():
        if not line.strip():  # Empty lines denote section separators
            last_key = ""
            continue

        last_key = parse_line(line, last_key, current_section, sections)
        current_section = len(sections) - 1  # Update current section index after potential addition


def build_manifest(sections: list[dict[str, str]]) -> JavaManifest:
    if sections:
        main_section = sections[0]
        other_sections = sections[1:] if len(sections) > 1 else None
        return JavaManifest(main=main_section, sections=other_sections)
    return JavaManifest(main={}, sections=None)


def parse_java_manifest(reader: str) -> JavaManifest:
    sections: list[dict[str, str]] = []
    process_section(sections, reader)
    return build_manifest(sections)


def _field_value_from_manifest(manifest: JavaManifest, field: str) -> str:
    """Extract a field's value from a JavaManifest file.

    Args:
        manifest (JavaManifest): The JavaManifest file from where the field
            value has to be extracted.
        field (str): The specific field name which value is needed.

    Returns:
        str: The field value extracted from the Manifest file if it exists,
            else returns an empty string.

    """
    if (value := manifest.main.get(field, None)) and value:
        return value

    for section in manifest.sections or []:
        if (value := section.get(field, None)) and value:
            return value
    return ""


def select_licenses(manifest: JavaManifest) -> list[str]:
    """Select licenses from a JavaManifest.

    Args:
        manifest (JavaManifest): the JavaManifest containing licenses

    Returns:
        list[str]: A list of licenses extracted from the manifest

    """
    return [
        value
        for field in ("Bundle-License", "Plugin-License-Name")
        if (value := _field_value_from_manifest(manifest, field))
    ]


def extract_name_from_apache_maven_bundle_plugin(
    manifest: JavaManifest | None,
) -> str:
    """Extract the name from Apache Maven bundle plugin using manifest main information.

    If successful, the function tries to split the symbolic name
    according to convention `"${groupId}.${artifactId}"` and return the
    artifactId. If this process fails or the vendor id is equal to the
    symbolic name, an empty string is returned.

    Args:
        manifest (JavaManifest | None): The JavaManifest object containing the
        manifest main information or None.

    Returns:
        str: The extracted name from the Apache Maven bundle plugin, or an
        empty string if extraction fails.

    """
    if manifest and manifest.main:
        created_by = manifest.main.get("Created-By", "")
        if "Apache Maven Bundle Plugin" in created_by:
            symbolic_name = manifest.main.get("Bundle-SymbolicName", "")
            if symbolic_name:
                vendor_id = manifest.main.get("Implementation-Vendor-Id", "")
                if vendor_id and vendor_id == symbolic_name:
                    return ""

                # Assuming symbolicName convention "${groupId}.${artifactId}".
                fields = symbolic_name.split(".")
                # Potential issue with determining the actual artifactId based
                # on BND behavior.
                return fields[-1] if fields else ""

    return ""


def is_valid_java_identifier(field: str) -> bool:
    """Check if a string is a valid Java identifier.

    An identifier is a name assigned to elements in the Java program i.e.
    variable, method, class etc.

    Args:
        field (str): The string to be checked if it is a valid Java identifier.

    Returns:
        bool: True if the string is a valid Java identifier, False otherwise.

    """
    if not field:
        return False

    # Check the first character
    first_char = field[0]
    if first_char.isalpha() or unicodedata.category(first_char) in [
        "Sc",
        "Pc",
    ]:
        # If the first character is valid, check the remaining characters.
        # Note: Python's str.isidentifier() checks if the entire string is a
        # valid identifier.
        return field.isidentifier()

    return False


def extract_name_from_archive_filename(archive: ArchiveFilename) -> str:
    """Extract name from an ArchiveFilename.

    This function extracts the name from the provided ArchiveFilename.
    It handles special cases for `org.eclipse.*` group IDs. For valid Java
    identifiers, it returns the last part as the artifact ID.

    Args:
        archive (ArchiveFilename): Given archive filename from which the name
        needs to be extracted.

    Returns:
        str: The extracted name from the ArchiveFilename.

    """
    if "." in archive.name:
        # Handle the special case for 'org.eclipse.*' group IDs
        if archive.name.startswith("org.eclipse."):
            return archive.name

        # Split the name on dots and check if it looks like a
        # 'groupId.artifactId'
        fields = archive.name.split(".")
        if all(is_valid_java_identifier(f) for f in fields):
            # If all parts are valid Java identifiers, assume the last part
            # is the artifact ID
            return fields[-1]

    return archive.name


def select_name(manifest: JavaManifest | None, filename_obj: ArchiveFilename) -> str:
    """Select a name from various sources based on the manifest and filename object.

    Args:
        manifest (JavaManifest | None): The Java Manifest input from which to
        extract the name
        filename_obj (ArchiveFilename): The Archive Filename object

    Returns:
        str: Name extracted from the manifest or filename object. If no name
        is found in either of these sources, it tries to find a name from
        other attributes in the manifest. If no name is still found,
        returns an empty string.

    """
    name = extract_name_from_apache_maven_bundle_plugin(manifest)
    if name:
        return name

    # the filename tends to be the next-best reference for the package name
    name = extract_name_from_archive_filename(filename_obj)
    if name:
        return name

    # remaining fields in the manifest is a bit of a free-for-all depending on
    # the build tooling used and package maintainer preferences
    if manifest:
        main_attrs = manifest.main
        for key in [
            "Name",
            "Bundle-Name",
            "Short-Name",
            "Extension-Name",
            "Implementation-Title",
        ]:
            if main_attrs.get(key):
                return main_attrs[key]

    return ""


def select_version(manifest: JavaManifest | None, filename_obj: ArchiveFilename) -> str:
    """Select the version from the Java manifest or the archive file.

    Args:
        manifest (JavaManifest | None): The Java manifest file to extract
            version from, could be None
        filename_obj (ArchiveFilename): The archive file to extract version
            from

    Returns:
        str: The version extracted from either the manifest or the archive
            file, returns an empty string if no version can be found.

    """
    if version := filename_obj.version:
        return version

    if not manifest:
        return ""

    field_names = [
        "Implementation-Version",
        "Specification-Version",
        "Plugin-Version",
        "Bundle-Version",
    ]
    for field in field_names:
        if value := _field_value_from_manifest(manifest, field):
            return value

    return ""
