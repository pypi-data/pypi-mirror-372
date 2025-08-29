FLUID_SBOM_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "sbom_details": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "tool": {"type": "string"},
                "organization": {"type": "string"},
                "version": {"type": ["string", "null"]},
            },
            "required": [
                "name",
                "version",
                "timestamp",
                "tool",
                "organization",
            ],
        },
        "packages": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "version": {"type": "string"},
                    "locations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "path": {"type": "string"},
                                "line": {"type": ["integer", "null"]},
                                "layer": {"type": ["string", "null"]},
                                "dependency_type": {"type": "string"},
                                "scope": {"type": "string"},
                                "reachable_cves": {"type": "array", "items": {"type": ["string"]}},
                            },
                            "required": ["path", "line", "layer"],
                        },
                    },
                    "language": {"type": "string"},
                    "licenses": {"type": "array", "items": {"type": "string"}},
                    "type": {"type": "string"},
                    "found_by": {"type": "string"},
                    "package_url": {"type": "string"},
                    "platform": {"type": ["string", "null"]},
                    "health_metadata": {
                        "type": ["object", "null"],
                        "additionalProperties": False,
                        "properties": {
                            "latest_version": {"type": ["string", "null"]},
                            "latest_version_created_at": {
                                "type": ["string", "null"],
                                "format": "date-time",
                            },
                            "artifact": {
                                "type": ["object", "null"],
                                "properties": {
                                    "integrity": {
                                        "type": ["object", "null"],
                                        "additionalProperties": False,
                                        "properties": {
                                            "algorithm": {"type": ["string", "null"]},
                                            "value": {"type": ["string", "null"]},
                                        },
                                        "required": ["algorithm", "value"],
                                    },
                                    "url": {"type": "string"},
                                },
                                "required": ["url"],
                            },
                            "authors": {"type": ["string", "null"]},
                        },
                    },
                    "advisories": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "cpes": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "description": {"type": ["string", "null"]},
                                "epss": {"type": "number"},
                                "id": {"type": "string"},
                                "namespace": {"type": "string"},
                                "percentile": {"type": "number"},
                                "severity": {"type": "string"},
                                "urls": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "version_constraint": {"type": "string"},
                                "cvss3": {"type": ["string", "null"]},
                                "cvss4": {"type": ["string", "null"]},
                                "cwe_ids": {
                                    "type": ["array", "null"],
                                    "items": {"type": "string"},
                                },
                                "fixed_versions": {
                                    "type": ["array", "null"],
                                    "items": {"type": "string"},
                                },
                                "fix_metadata": {
                                    "type": ["object", "null"],
                                    "additionalProperties": False,
                                    "properties": {
                                        "closest_fix_version": {"type": ["string", "null"]},
                                        "upgrade_type": {
                                            "type": ["string", "null"],
                                            "enum": ["unknown", "major", "minor", "patch"],
                                        },
                                        "breaking_change": {"type": "boolean"},
                                    },
                                    "required": [
                                        "closest_fix_version",
                                        "upgrade_type",
                                        "breaking_change",
                                    ],
                                },
                                "cve_finding": {"type": ["string", "null"]},
                                "auto_approve": {"type": "boolean"},
                                "upstream_package": {"type": ["string", "null"]},
                            },
                            "required": [
                                "cpes",
                                "description",
                                "id",
                                "namespace",
                                "severity",
                                "urls",
                                "version_constraint",
                            ],
                        },
                    },
                },
                "required": [
                    "id",
                    "name",
                    "version",
                    "locations",
                    "licenses",
                    "type",
                    "language",
                    "platform",
                    "package_url",
                    "found_by",
                    "health_metadata",
                    "advisories",
                ],
            },
        },
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "from": {"type": "string"},
                    "to": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["from", "to"],
            },
        },
    },
    "required": ["sbom_details", "packages", "relationships"],
}
