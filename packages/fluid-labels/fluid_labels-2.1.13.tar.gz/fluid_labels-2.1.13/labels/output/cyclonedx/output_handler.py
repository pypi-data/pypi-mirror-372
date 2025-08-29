import logging
from typing import TYPE_CHECKING

from cyclonedx.model.bom import Bom
from cyclonedx.output import make_outputter
from cyclonedx.schema import OutputFormat as CyclonedxOutputFormat
from cyclonedx.schema import SchemaVersion
from cyclonedx.validation import make_schemabased_validator
from cyclonedx.validation.json import JsonStrictValidator

from labels.model.core import OutputFormat, SbomConfig
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.resolver import Resolver
from labels.output.cyclonedx.file_builder import (
    add_advisories_to_bom,
    add_components_to_bom,
    add_relationships_to_bom,
    create_bom,
    pkg_to_component,
)
from labels.output.utils import set_namespace_version
from labels.utils.exceptions import CycloneDXValidationError

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from cyclonedx.output.json import Json as JsonOutputter
    from cyclonedx.output.xml import Xml as XmlOutputter
    from cyclonedx.validation.xml import XmlValidator


def validate_sbom_xml(serialized_xml: str, file_path: str) -> None:
    xml_validator: XmlValidator = make_schemabased_validator(
        output_format=CyclonedxOutputFormat.XML,
        schema_version=SchemaVersion.V1_6,
    )
    validation_error = xml_validator.validate_str(serialized_xml)

    if validation_error:
        raise CycloneDXValidationError(validation_error)

    LOGGER.info("🆗 Valid CYCLONEDX XML format, generating output file at %s", file_path)


def validate_sbom_json(serialized_json: str, file_path: str) -> None:
    json_validator = JsonStrictValidator(SchemaVersion.V1_6)
    validation_error = json_validator.validate_str(serialized_json)

    if validation_error:
        raise CycloneDXValidationError(validation_error)

    LOGGER.info(
        "🆗 Valid CYCLONEDX JSON format, generating output file at %s",
        file_path,
    )


def format_cyclone_json(bom: Bom, output: str) -> None:
    file_path = f"{output}.json"
    json_output: JsonOutputter = make_outputter(
        bom=bom,
        output_format=CyclonedxOutputFormat.JSON,
        schema_version=SchemaVersion.V1_6,
    )
    serialized_json = json_output.output_as_string()

    validate_sbom_json(serialized_json, file_path)

    json_output.output_to_file(file_path, allow_overwrite=True, indent=2)
    LOGGER.info("✅ Output file successfully generated")


def format_cyclone_xml(bom: Bom, output: str) -> None:
    file_path = f"{output}.xml"
    xml_outputter: XmlOutputter = make_outputter(
        bom=bom,
        output_format=CyclonedxOutputFormat.XML,
        schema_version=SchemaVersion.V1_6,
    )
    serialized_xml = xml_outputter.output_as_string()

    validate_sbom_xml(serialized_xml, file_path)

    xml_outputter.output_to_file(file_path, allow_overwrite=True, indent=2)
    LOGGER.info("✅ Output file successfully generated")


def format_bom_output(bom: Bom, config: SbomConfig) -> None:
    format_handlers = {
        OutputFormat.CYCLONEDX_JSON: format_cyclone_json,
        OutputFormat.CYCLONEDX_XML: format_cyclone_xml,
    }
    handler = format_handlers[config.output_format]
    handler(bom, config.output)


def format_cyclonedx_sbom(
    *,
    packages: list[Package],
    relationships: list[Relationship],
    config: SbomConfig,
    resolver: Resolver,
) -> None:
    namespace, version = set_namespace_version(config=config, resolver=resolver)
    bom = create_bom(namespace, version)
    component_cache = {pkg.id_: pkg_to_component(pkg) for pkg in packages}
    add_components_to_bom(bom, component_cache)
    add_advisories_to_bom(bom, packages)
    add_relationships_to_bom(bom, relationships, component_cache)
    format_bom_output(bom, config)
