import uuid
from datetime import UTC, datetime

from fluidattacks_tracks import Tracks
from fluidattacks_tracks.resources.event import Event

from labels.model.core import SbomConfig

client = Tracks()


def send_event_to_tracks(
    *,
    sbom_config: SbomConfig,
    packages_amount: int,
    relationships_amount: int,
    vulns_summary: dict[str, int],
) -> None:
    client.event.create(
        Event(
            action="CREATE",
            author="unknown",
            date=datetime.now(UTC),
            mechanism="TASK",
            metadata={
                "status": "success",
                "source": sbom_config.source,
                "exclude": sbom_config.exclude,
                "include": sbom_config.include,
                "aws_role": sbom_config.aws_role,
                "docker_user": sbom_config.docker_user,
                "aws_external_id": sbom_config.aws_external_id,
                "include_package_metadata": str(sbom_config.include_package_metadata),
                "source_type": sbom_config.source_type.value,
                "output_format": sbom_config.output_format.value,
                "packages_count": str(packages_amount),
                "relationships_count": str(relationships_amount),
                "vulns_summary": vulns_summary,
            },
            object="LabelsExecution",
            object_id=sbom_config.execution_id or str(uuid.uuid4()).replace("-", ""),
        ),
    )
