from enum import Enum
from typing import TypedDict

from pydantic import BaseModel

from labels.model.sources import AwsCredentials


class OutputFormat(Enum):
    FLUID_JSON = "fluid-json"
    CYCLONEDX_JSON = "cyclonedx-json"
    CYCLONEDX_XML = "cyclonedx-xml"
    SPDX_JSON = "spdx-json"
    SPDX_XML = "spdx-xml"

    @classmethod
    def from_string(cls: type["OutputFormat"], value: str) -> "OutputFormat":
        for member in cls:
            if member.value == value.lower():
                return member

        error_msg = f"{value} is not a valid {cls.__name__}"
        raise ValueError(error_msg)


class SourceType(Enum):
    DIRECTORY = "dir"
    DOCKER = "docker"
    DOCKER_DAEMON = "docker-daemon"
    ECR = "ecr"
    ECR_WITH_CREDENTIALS = "ecr-with-credentials"

    @classmethod
    def from_string(cls: type["SourceType"], value: str) -> "SourceType":
        for member in cls:
            if member.value == value.lower():
                return member

        error_msg = f"{value} is not a valid {cls.__name__}"
        raise ValueError(error_msg)


class ScanArgs(TypedDict):
    source: str
    format: str
    output: str
    docker_user: str | None
    docker_password: str | None
    aws_external_id: str | None
    aws_role: str | None
    config: bool
    debug: bool


class DockerCredentialsConfig(TypedDict):
    username: str
    password: str


class AwsCredentialsConfig(TypedDict):
    external_id: str | None
    role: str | None
    access_key_id: str | None
    secret_access_key: str | None
    session_token: str | None


class OutputConfig(TypedDict):
    name: str
    format: str


class LoadedConfig(TypedDict):
    source: str
    source_type: str
    execution_id: str
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    docker_credentials: DockerCredentialsConfig | None
    aws_credentials: AwsCredentialsConfig | None
    output: OutputConfig
    debug: bool
    include_package_metadata: bool


class SbomConfig(BaseModel):
    source: str
    source_type: SourceType
    output_format: OutputFormat
    output: str
    execution_id: str | None = None
    include: tuple[str, ...] = (".",)
    exclude: tuple[str, ...] = ()
    docker_user: str | None = None
    docker_password: str | None = None
    aws_external_id: str | None = None
    aws_role: str | None = None
    aws_credentials: AwsCredentials | None = None
    debug: bool = False
    include_package_metadata: bool = True
    restricted_licenses: list[str] = []
