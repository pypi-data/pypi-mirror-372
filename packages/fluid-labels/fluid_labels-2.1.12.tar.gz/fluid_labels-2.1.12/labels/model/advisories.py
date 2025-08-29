from enum import Enum

from pydantic import BaseModel

AdvisoryRecord = tuple[
    str,  # id
    str,  # source
    str,  # vulnerable_version
    str | None,  # severity_level
    str | None,  # severity
    str | None,  # severity_v4
    str | None,  # epss
    str | None,  # details
    str | None,  # percentile
    str | None,  # cwe_ids
    str | None,  # cve_finding
    int,  # auto_approve
    str | None,  # fixed_versions
]


class UpgradeType(str, Enum):
    UNKNOWN = "unknown"
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


class AdvisoryFixMetadata(BaseModel):
    closest_fix_version: str
    upgrade_type: UpgradeType
    breaking_change: bool


class Advisory(BaseModel):
    id: str
    vulnerable_version: str
    source: str
    package_manager: str
    cpes: list[str]
    severity_level: str = "Low"
    fixed_versions: list[str] | None = None
    fix_metadata: AdvisoryFixMetadata | None = None
    details: str | None = None
    epss: float = 0.0
    percentile: float = 0.0
    severity: str | None = None
    severity_v4: str | None = None
    cwe_ids: list[str] | None = None
    cve_finding: str | None = None
    auto_approve: bool = False
    upstream_package: str | None = None
