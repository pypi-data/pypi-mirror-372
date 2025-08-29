import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

from labels.model.advisories import Advisory
from labels.model.indexables import IndexedDict, IndexedList
from labels.model.package import Package
from labels.model.relationship import Relationship

LOGGER = logging.getLogger(__name__)


class EnumEncoder(json.JSONEncoder):
    def default(self, item: Any) -> Any:  # noqa: ANN401
        if isinstance(item, Enum):
            return item.value
        if isinstance(item, IndexedList):
            return list(item.data)
        if isinstance(item, IndexedDict):
            return dict(item.data)
        if isinstance(item, BaseModel):
            return item.model_dump()
        if isinstance(item, datetime):
            return item.isoformat()
        return super().default(item)


def serialize_package(package: Package) -> dict[str, Any]:
    return {
        "id": package.id_,
        "name": package.name,
        "version": package.version,
        "locations": [
            {
                "path": loc.path(),
                "line": loc.coordinates.line if loc.coordinates and loc.coordinates.line else None,
                "layer": loc.coordinates.file_system_id
                if loc.coordinates and loc.coordinates.file_system_id
                else None,
                "dependency_type": loc.dependency_type,
                "scope": loc.scope.value,
                "reachable_cves": loc.reachable_cves,
            }
            for loc in package.locations
        ],
        "licenses": package.licenses,
        "type": package.type.value,
        "language": package.language.value,
        "platform": package.type.get_platform_value(),
        "package_url": package.p_url,
        "found_by": package.found_by,
        "health_metadata": package.health_metadata.model_dump()
        if package.health_metadata
        else None,
        "advisories": [serialize_advisory(adv) for adv in package.advisories or []],
    }


def serialize_advisory(advisory: Advisory) -> dict[str, Any]:
    return {
        "cpes": advisory.cpes,
        "description": advisory.details,
        "epss": advisory.epss,
        "id": advisory.id,
        "namespace": advisory.package_manager,
        "percentile": advisory.percentile,
        "severity": advisory.severity_level,
        "urls": [advisory.source],
        "version_constraint": advisory.vulnerable_version,
        "fixed_versions": advisory.fixed_versions,
        "fix_metadata": advisory.fix_metadata.model_dump() if advisory.fix_metadata else None,
        "cvss3": advisory.severity,
        "cvss4": advisory.severity_v4,
        "cwe_ids": advisory.cwe_ids,
        "cve_finding": advisory.cve_finding,
        "auto_approve": advisory.auto_approve,
        "upstream_package": advisory.upstream_package,
    }


def serialize_packages(packages: list[Package]) -> list[dict[str, Any]]:
    raw_pkgs = [serialize_package(pkg) for pkg in packages]
    return validate_pkgs(raw_pkgs)


def validate_pkgs(raw_sbom_pkgs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pkgs_to_remove = []
    for index, raw_pkg in enumerate(raw_sbom_pkgs):
        try:
            pkg = json.loads(json.dumps(raw_pkg, cls=EnumEncoder))
            raw_sbom_pkgs[index] = pkg
        except TypeError as err:
            LOGGER.warning(
                "Cannot serialize package at index %d: %s. Error: %s",
                index,
                raw_pkg,
                str(err),
            )
            pkgs_to_remove.append(index)

    for index in sorted(pkgs_to_remove, reverse=True):
        raw_sbom_pkgs.pop(index)
    return raw_sbom_pkgs


def build_relationship_map(relationships: list[Relationship]) -> list[dict[str, str | list[str]]]:
    dependency_map: dict[str, list[str]] = {}
    for rel in relationships:
        from_pkg = rel.from_
        to_pkg = rel.to_
        ref = to_pkg
        dep = from_pkg
        dependency_map.setdefault(ref, []).append(dep)
    return [{"from": ref, "to": deps} for ref, deps in dependency_map.items()]


def build_sbom_metadata(namespace: str, version: str | None, timestamp: str) -> dict[str, Any]:
    return {
        "name": namespace,
        "version": version,
        "timestamp": timestamp,
        "tool": "Fluid-Labels",
        "organization": "Fluid attacks",
    }
