import asyncio

from labels.integrations.docker import get_docker_image, get_image_context
from labels.integrations.ecr import ecr_connection, get_token
from labels.model.core import SbomConfig, SourceType
from labels.model.sources import AwsCredentials, AwsRole, ImageMetadata
from labels.resolvers.container_image import ContainerImage
from labels.resolvers.directory import Directory
from labels.utils.exceptions import (
    AwsCredentialsNotFoundError,
    AwsExternalIdNotDefinedError,
    AwsRoleNotDefinedError,
    UnexpectedSBOMSourceError,
)


def _get_async_ecr_connection(role: AwsRole, source: str) -> tuple[str, ImageMetadata]:
    return asyncio.run(ecr_connection(role, source))


def _handle_directory(sbom_config: SbomConfig) -> Directory:
    return Directory(
        root=sbom_config.source,
        include=sbom_config.include,
        exclude=sbom_config.exclude,
    )


def _handle_docker(*, sbom_config: SbomConfig, is_daemon: bool = False) -> ContainerImage:
    docker_image = get_docker_image(
        sbom_config.source,
        username=sbom_config.docker_user,
        password=sbom_config.docker_password,
        daemon=is_daemon,
    )

    context = get_image_context(
        image=docker_image,
        username=sbom_config.docker_user,
        password=sbom_config.docker_password,
        daemon=is_daemon,
    )

    return ContainerImage(img=docker_image, context=context)


def _handle_ecr(sbom_config: SbomConfig) -> ContainerImage:
    if not sbom_config.aws_role:
        raise AwsRoleNotDefinedError

    if not sbom_config.aws_external_id:
        raise AwsExternalIdNotDefinedError

    role = AwsRole(
        external_id=sbom_config.aws_external_id,
        role=sbom_config.aws_role,
    )

    token, image_metadata = _get_async_ecr_connection(
        role=role,
        source=sbom_config.source,
    )

    context = get_image_context(
        image=image_metadata,
        aws_creds=f"AWS:{token}",
    )

    return ContainerImage(img=image_metadata, context=context)


def handle_ecr_with_credentials(
    image_uri: str,
    aws_credentials: AwsCredentials,
) -> ContainerImage:
    token = asyncio.run(get_token(aws_credentials))
    aws_token = f"AWS:{token}"
    image_metadata = get_docker_image(image_ref=f"docker://{image_uri}", aws_creds=aws_token)
    context = get_image_context(image=image_metadata, aws_creds=aws_token)

    return ContainerImage(img=image_metadata, context=context)


def resolve_sbom_source(sbom_config: SbomConfig) -> Directory | ContainerImage:
    match sbom_config.source_type:
        case SourceType.DIRECTORY:
            return _handle_directory(sbom_config)
        case SourceType.DOCKER:
            return _handle_docker(sbom_config=sbom_config)
        case SourceType.DOCKER_DAEMON:
            return _handle_docker(sbom_config=sbom_config, is_daemon=True)
        case SourceType.ECR:
            return _handle_ecr(sbom_config)
        case SourceType.ECR_WITH_CREDENTIALS:
            if not sbom_config.aws_credentials:
                raise AwsCredentialsNotFoundError

            return handle_ecr_with_credentials(
                image_uri=sbom_config.source,
                aws_credentials=sbom_config.aws_credentials,
            )
        case _:
            raise UnexpectedSBOMSourceError(sbom_config.source_type)
