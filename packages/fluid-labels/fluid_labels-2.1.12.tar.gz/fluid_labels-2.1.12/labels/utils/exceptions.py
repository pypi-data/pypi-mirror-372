from cyclonedx.validation import ValidationError as CycloneDXError
from jsonschema import ValidationError as JSONSchemaError
from spdx_tools.spdx.validation.validation_message import ValidationMessage
from tree_sitter import Node

from labels.model.core import SourceType


class CustomBaseError(Exception):
    """Base exception class for custom exceptions."""


class AwsRoleNotDefinedError(CustomBaseError):
    """Exception raised when the AWS role is not defined."""

    def __init__(self) -> None:
        error_msg = "The AWS role wasn't defined in the configuration"
        super().__init__(error_msg)


class AwsExternalIdNotDefinedError(CustomBaseError):
    """Exception raised when the AWS External ID is not defined."""

    def __init__(self) -> None:
        error_msg = "The AWS External ID wasn't defined in the configuration"
        super().__init__(error_msg)


class AwsCredentialsNotFoundError(CustomBaseError):
    """Exception raised when AWS credentials are not found."""

    def __init__(self) -> None:
        error_msg = "The AWS credentials were not found or could not be retrieved."
        super().__init__(error_msg)


class CycloneDXValidationError(CustomBaseError):
    """Exception for CycloneDX validation errors."""

    def __init__(self, error: CycloneDXError) -> None:
        """Initialize the constructor."""
        header = "Exception - CycloneDx validation error\n"
        msg = f"❌ {header}{error}"
        super().__init__(msg)


class DockerImageNotFoundError(CustomBaseError):
    """Exception raised when a Docker image is not found."""

    def __init__(self, image: str, extra_msg: str | None = None) -> None:
        error_msg = f"Docker image not found: {image}"
        if extra_msg:
            error_msg += f"\nError details: {extra_msg}"
        super().__init__(error_msg)


class DuplicatedKeyError(CustomBaseError):
    """Exception raised for duplicated keys."""

    def __init__(self, key: str) -> None:
        """Initialize the constructor."""
        super().__init__(f"Defining a key multiple times is invalid: {key}")


class FluidJSONValidationError(CustomBaseError):
    """Exception for Fluid JSON validation errors."""

    def __init__(self, error: JSONSchemaError) -> None:
        """Initialize the constructor."""
        header = "Exception - Fluid JSON validation error\n"
        msg = f"❌ {header}{error}"
        super().__init__(msg)


class ForbiddenModuleImportedError(CustomBaseError):
    """Exception raised when a forbidden module is imported."""


class InvalidConfigFileError(CustomBaseError):
    """Exception raised for when the sbom config file is invalid."""

    def __init__(self, file_path: str, extra_msg: str | None = None) -> None:
        message = f"The configuration file is not a valid file: {file_path}"
        if extra_msg:
            message += f"\n{extra_msg}"
        super().__init__(message)


class InvalidDBFormatError(CustomBaseError):
    """Exception raised for invalid DB format."""


class InvalidImageReferenceError(CustomBaseError):
    """Exception raised when the image reference is invalid."""

    def __init__(self, image_ref: str) -> None:
        error_msg = f"The image reference '{image_ref}' is invalid."
        super().__init__(error_msg)


class InvalidMetadataError(CustomBaseError):
    """Exception raised for when metadata is invalid."""

    def __init__(self, error_message: str) -> None:
        message = error_message
        super().__init__(message)


class InvalidTypeError(CustomBaseError):
    """Exception raised for invalid types."""


class SkopeoNotFoundError(CustomBaseError):
    """Exception raised when the Skopeo binary is not found."""

    def __init__(self) -> None:
        error_msg = "The 'skopeo' binary was not found in the system."
        super().__init__(error_msg)


class SPDXValidationError(CustomBaseError):
    """Exception for SPDX validation errors."""

    def __init__(self, error_messages: list[ValidationMessage]) -> None:
        """Initialize the constructor."""
        header = "Exception - SPDX validation error\n"
        error_details = "\n".join(
            (f"Validation error: {message.validation_message}\nContext: {message.context}")
            for message in error_messages
        )
        msg = f"❌ {header}{error_details}"
        super().__init__(msg)


class UnexpectedChildrenLengthError(CustomBaseError):
    """Exception raised for nodes with unexpected number of children."""

    def __init__(self, node: Node | str, expected_length: int) -> None:
        type_name = node.type if isinstance(node, Node) else node
        super().__init__(f"Unexpected node type {type_name} for {expected_length} children")


class UnexpectedExceptionError(CustomBaseError):
    """Exception for unexpected errors encountered during SBOM execution."""

    def __init__(self, error: Exception) -> None:
        """Initialize the constructor."""
        header = (
            "Exception - An unexpected exception was encountered "
            "during SBOM execution. The process will be terminated to prevent "
            "potential inconsistencies.\n"
        )
        msg = f"❌ {header}{error}"
        super().__init__(msg)


class UnexpectedNodeError(CustomBaseError):
    """Exception raised for unexpected nodes."""

    def __init__(self, node: Node | str) -> None:
        type_name = node.type if isinstance(node, Node) else node
        if isinstance(node, Node) and node.text:
            value = node.text.decode("utf-8")
            super().__init__(
                f"Unexpected node type {type_name} with value {value}",
            )
        else:
            super().__init__(f"Unexpected node type {type_name}")


class UnexpectedNodeTypeError(CustomBaseError):
    """Exception raised for unexpected node types."""

    def __init__(self, node: Node | str, expected_type: str | None = None) -> None:
        type_name = node.type if isinstance(node, Node) else node
        if expected_type:
            super().__init__(f"Unexpected node type {type_name} for {expected_type}")
        else:
            super().__init__(f"Unexpected node type {type_name}")


class UnexpectedSBOMSourceError(CustomBaseError):
    """Exception raised when the SBOM source in the configuration is not recognized."""

    def __init__(self, source: SourceType) -> None:
        error_msg = f"Unrecognized SBOM source: {source}"
        super().__init__(error_msg)


class UnexpectedValueTypeError(CustomBaseError):
    """Exception raised for unexpected value types."""
