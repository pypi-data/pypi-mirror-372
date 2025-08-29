import logging
from urllib.parse import parse_qs

from labels.model.file import DependencyType, Location, Scope
from labels.model.release import Release
from labels.utils.strings import format_exception

LOGGER = logging.getLogger(__name__)

PURL_QUALIFIER_DISTRO = "distro"


def purl_qualifiers(
    qualifiers: dict[str, str | None],
    release: Release | None = None,
) -> dict[str, str]:
    if release:
        distro_qualifiers = []
        if release.id_:
            distro_qualifiers.append(release.id_)
        if release.version_id:
            distro_qualifiers.append(release.version_id)
        elif release.build_id:
            distro_qualifiers.append(release.build_id)

        if distro_qualifiers:
            qualifiers[PURL_QUALIFIER_DISTRO] = "-".join(distro_qualifiers)

    return {
        key: qualifiers.get(key, "") or ""
        for key in sorted(qualifiers.keys())
        if qualifiers.get(key)
    }


def extract_distro_info(pkg_str: str) -> tuple[str | None, str | None, str | None]:
    parts = pkg_str.split("?", 1)
    if len(parts) != 2:
        return None, None, None

    query = parts[1]
    params = parse_qs(query)
    distro_id = params.get("distro_id", [None])[0]
    distro_version = params.get("distro_version_id", [None])[0]
    arch = params.get("arch", [None])[0]
    return distro_id, distro_version, arch


def get_enriched_location(
    base: Location,
    *,
    line: int | None = None,
    is_transitive: bool | None = None,
    is_dev: bool | None = None,
) -> Location:
    update_data: dict[str, object] = {}

    if is_dev is not None:
        scope: Scope = Scope.BUILD if is_dev else Scope.RUN
        update_data["scope"] = scope

    if is_transitive is not None:
        dependency_type: DependencyType = (
            DependencyType.TRANSITIVE if is_transitive else DependencyType.DIRECT
        )
        update_data["dependency_type"] = dependency_type

    if line is not None and base.coordinates:
        line_update = {"line": line}
        coordinates = base.coordinates.model_copy(update=line_update)
        update_data["coordinates"] = coordinates

    if not update_data:
        return base

    return base.model_copy(deep=True, update=update_data)


def log_malformed_package_warning(
    location: Location,
    exception: Exception,
) -> None:
    LOGGER.warning(
        "Malformed package. Required fields are missing or data types are incorrect.",
        extra={
            "extra": {
                "exception": format_exception(str(exception)),
                "location": location.path(),
            },
        },
    )
