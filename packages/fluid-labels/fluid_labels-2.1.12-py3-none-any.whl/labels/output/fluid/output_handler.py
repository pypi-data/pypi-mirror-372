import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from labels.model.core import SbomConfig
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.resolver import Resolver
from labels.output.fluid.file_builder import (
    EnumEncoder,
    build_relationship_map,
    build_sbom_metadata,
    serialize_packages,
)
from labels.output.fluid.schema import FLUID_SBOM_JSON_SCHEMA
from labels.output.utils import set_namespace_version
from labels.utils.exceptions import FluidJSONValidationError

LOGGER = logging.getLogger(__name__)


def write_json_to_file(path: Path, content: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(content, f, indent=4, cls=EnumEncoder)
    LOGGER.info("✅ Output file successfully generated")


def validate_fluid_json(result: dict[str, Any], file_path: Path) -> None:
    try:
        validate(result, FLUID_SBOM_JSON_SCHEMA)

    except ValidationError as ex:
        raise FluidJSONValidationError(ex) from None

    LOGGER.info("🆗 Valid Fluid JSON format, generating output file at %s", file_path)


def format_fluid_sbom(
    *,
    packages: list[Package],
    relationships: list[Relationship],
    config: SbomConfig,
    resolver: Resolver,
) -> None:
    now_utc = datetime.now(UTC).isoformat()
    namespace, version = set_namespace_version(config=config, resolver=resolver)
    file_path = Path(f"{config.output}.json")

    sbom_pkgs = serialize_packages(packages)
    sbom_relationships = build_relationship_map(relationships)
    sbom_metadata = build_sbom_metadata(namespace, version, now_utc)

    result = {
        "sbom_details": sbom_metadata,
        "packages": sbom_pkgs,
        "relationships": sbom_relationships,
    }

    validate_fluid_json(result, file_path)
    write_json_to_file(file_path, result)
