import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from spdx_tools.spdx.model.actor import Actor, ActorType
from spdx_tools.spdx.model.document import CreationInfo, Document
from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document
from spdx_tools.spdx.writer.write_anything import write_file

from labels.model.core import OutputFormat, SbomConfig
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.resolver import Resolver
from labels.output.spdx.complete_file import add_empty_package
from labels.output.spdx.file_builder import add_packages_and_relationships
from labels.output.utils import get_document_namespace, set_namespace_version
from labels.utils.exceptions import SPDXValidationError

if TYPE_CHECKING:  # pragma: no cover
    from spdx_tools.spdx.validation.validation_message import ValidationMessage

LOGGER = logging.getLogger(__name__)

_FORMAT_EXTENSION_MAP = {
    OutputFormat.SPDX_XML: "xml",
    OutputFormat.SPDX_JSON: "json",
}


def validate_spdx_sbom(file_format: str, file_name: str, document: Document) -> None:
    validation_errors: list[ValidationMessage] = validate_full_spdx_document(document)

    if validation_errors:
        raise SPDXValidationError(validation_errors)

    LOGGER.info(
        "🆗 Valid SPDX %s format, generating output file at %s.%s",
        file_format.upper(),
        file_name,
        file_format,
    )


def format_spdx_sbom(
    *,
    packages: list[Package],
    relationships: list[Relationship],
    config: SbomConfig,
    resolver: Resolver,
) -> None:
    now_utc = datetime.now(UTC)
    namespace, _ = set_namespace_version(config=config, resolver=resolver)
    creation_info = CreationInfo(
        spdx_version="SPDX-2.3",
        spdx_id="SPDXRef-DOCUMENT",
        name=namespace,
        data_license="CC0-1.0",
        document_namespace=get_document_namespace(namespace),
        creators=[Actor(ActorType.TOOL, "Fluid-Labels", None)],
        created=now_utc,
    )

    document = Document(creation_info)

    if not packages and not relationships:
        add_empty_package(document)
    else:
        add_packages_and_relationships(document, packages, relationships)

    file_format = _FORMAT_EXTENSION_MAP[config.output_format]

    validate_spdx_sbom(file_format, config.output, document)

    write_file(document, f"{config.output}.{file_format}")
    LOGGER.info("✅ Output file successfully generated")
