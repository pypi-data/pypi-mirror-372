from labels.model.package import Package


def count_vulns_by_severity(packages: list[Package]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for pkg in packages:
        advisories = pkg.advisories or []
        for adv in advisories:
            sev_lower = adv.severity_level.lower()
            if sev_lower in counts:
                counts[sev_lower] += 1
    return counts
