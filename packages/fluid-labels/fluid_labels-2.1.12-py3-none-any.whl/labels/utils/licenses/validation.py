import re

from labels.utils.licenses.licenses_index import (
    COMMON_LICENSES,
    INVERSE_LICENSES,
    sanitization_pattern,
)


def sanitize_license_string(license_str: str) -> str:
    sanitized = re.sub(r"\s+", " ", license_str.strip())
    sanitized = re.sub(r"[,\s]+", " ", sanitized)
    sanitized = re.sub(sanitization_pattern, "", sanitized)
    return re.sub(r"\s+", " ", sanitized).strip()


def find_license_by_pattern(sanitized_license: str) -> str | None:
    for identifier, (pattern, _) in COMMON_LICENSES.items():
        if re.search(pattern, sanitized_license, re.IGNORECASE):
            return identifier
    return None


def _validate_license_with_operator(declared_license: str, operator: str) -> str:
    has_outer_parentheses = declared_license.strip().startswith(
        "(",
    ) and declared_license.strip().endswith(")")

    inner_license = declared_license.strip()[1:-1] if has_outer_parentheses else declared_license

    parts = inner_license.split(operator)
    validated_parts = []
    for part in parts:
        sanitized_license = sanitize_license_string(part.strip())
        identifier = find_license_by_pattern(sanitized_license)
        if identifier:
            validated_parts.append(identifier)
        else:
            full_name = INVERSE_LICENSES.get(sanitized_license)
            if full_name:
                validated_parts.append(full_name)
            else:
                validated_parts.append(part.strip())

    result = operator.join(validated_parts)
    if has_outer_parentheses:
        result = f"({result})"

    return result


def _handle_operators_in_long_text(declared_license: str) -> str | None:
    if " OR " in declared_license:
        return _validate_license_with_operator(declared_license, " OR ")
    if " AND " in declared_license:
        return _validate_license_with_operator(declared_license, " AND ")
    if " WITH " in declared_license:
        return _validate_license_with_operator(declared_license, " WITH ")
    return None


def _extract_licenses_from_mixed_text(declared_license: str) -> set[str]:
    found_licenses = set()
    processed_text = (
        declared_license.replace(" OR ", ",").replace(" AND ", ",").replace(" WITH ", ",")
    )
    license_parts = [part.strip() for part in processed_text.split(",")]

    for license_part in license_parts:
        if not license_part:
            continue

        sanitized_license = sanitize_license_string(license_part)
        identifier = find_license_by_pattern(sanitized_license)
        if identifier:
            found_licenses.add(identifier)

    return {lic for lic in found_licenses if lic is not None}


def _process_long_text_license(declared_license: str) -> set[str]:
    found_licenses = set()

    license_patterns = [
        r"([A-Za-z0-9.-]+(?:\+)?(?:\s+(?:OR|AND|WITH)\s+[A-Za-z0-9.-]+(?:\+)?)+)\s*$",
        r"([A-Za-z0-9.-]+(?:\+)?(?:\s+(?:OR|AND|WITH)\s+[A-Za-z0-9.-]+(?:\+)?)+)\s*$",
    ]

    has_clear_expression = False
    for pattern in license_patterns:
        match = re.search(pattern, declared_license)
        if match is not None:
            expression = str(match.group(1)).strip()
            if not any(
                word in expression.lower()
                for word in ["copyright", "redistribution", "permission", "warranty", "liability"]
            ):
                has_clear_expression = True
                break

    if has_clear_expression:
        result = _handle_operators_in_long_text(declared_license)
        found_licenses.add(result)

    found_licenses.update(_extract_licenses_from_mixed_text(declared_license))

    return {lic for lic in found_licenses if lic is not None}


def _process_short_license(declared_license: str) -> set[str]:
    found_licenses = set()

    if " OR " in declared_license:
        result = _validate_license_with_operator(declared_license, " OR ")
        found_licenses.add(result)
    elif " AND " in declared_license:
        result = _validate_license_with_operator(declared_license, " AND ")
        found_licenses.add(result)
    elif " WITH " in declared_license:
        result = _validate_license_with_operator(declared_license, " WITH ")
        found_licenses.add(result)
    else:
        sanitized_license = sanitize_license_string(declared_license)
        identifier = find_license_by_pattern(sanitized_license)
        if identifier:
            found_licenses.add(identifier)
        else:
            full_name = INVERSE_LICENSES.get(sanitized_license)
            if full_name:
                found_licenses.add(full_name)

    return found_licenses


def validate_licenses(licenses: list[str]) -> list[str]:
    found_licenses = set()

    for declared_license in licenses:
        is_long_text = (
            len(declared_license) > 100
            or "copyright" in declared_license.lower()
            or "redistribution" in declared_license.lower()
            or "permission" in declared_license.lower()
        )

        if is_long_text:
            found_licenses.update(_process_long_text_license(declared_license))
        else:
            found_licenses.update(_process_short_license(declared_license))
    return sorted(found_licenses)
