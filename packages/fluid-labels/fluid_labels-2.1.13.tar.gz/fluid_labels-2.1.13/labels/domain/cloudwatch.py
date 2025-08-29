import logging
import os
from typing import NamedTuple

import boto3

from labels.model.core import SourceType

LOGGER = logging.getLogger(__name__)


class BaseMetrics(NamedTuple):
    files_amount: int
    files_size: int


class ExecutionMetrics(NamedTuple):
    """Metrics collected during execution.

    Attributes:
       group: Group identifier for the metrics
       root: Root path identifier
       technique_time: Execution time in seconds
       analyzed_files_amount: Number of files analyzed
       analyzed_files_size: Total size of analyzed files in KB

    """

    group: str
    root: str
    technique_time: float
    analyzed_files_amount: int
    analyzed_files_size: int


def is_fluid_batch_env() -> bool:
    return "FLUIDATTACKS_EXECUTION" in os.environ


def process_sbom_metrics(
    execution_id: str | None,
    technique_time: float,
    base_metrics: BaseMetrics,
    source_type: SourceType,
) -> None:
    try:
        if (
            source_type == SourceType.DIRECTORY
            and execution_id is not None
            and is_fluid_batch_env()
            and (execution_id_parts := execution_id.split("_"))
            and len(execution_id_parts) >= 3
        ):
            group, *root, _ = execution_id_parts
            metrics = ExecutionMetrics(
                group=group,
                # In case root contained underscores
                root=("_").join(root),
                technique_time=round(technique_time, 2),
                analyzed_files_amount=int(base_metrics.files_amount),
                analyzed_files_size=int(base_metrics.files_size // 1024),
            )
            send_metrics_to_cloudwatch(metrics)
    except Exception as exc:
        LOGGER.exception(
            "Unable to send metrics to cloudwatch",
            extra={
                "extra": {
                    "exception": str(exc),
                },
            },
        )


def send_metrics_to_cloudwatch(execution_metrics: ExecutionMetrics) -> None:
    try:
        dimensions = [
            {"Name": "Group", "Value": execution_metrics.group},
            {"Name": "Root", "Value": execution_metrics.root},
        ]

        metric_data = [
            {
                "MetricName": "ExecutionTime",
                "Dimensions": dimensions,
                "Value": execution_metrics.technique_time,
                "Unit": "Seconds",
            },
            {
                "MetricName": "AnalyzedFiles",
                "Dimensions": dimensions,
                "Value": execution_metrics.analyzed_files_amount,
                "Unit": "Count",
            },
            {
                "MetricName": "AnalyzedFilesSize",
                "Dimensions": dimensions,
                "Value": execution_metrics.analyzed_files_size,
                "Unit": "Kilobytes",
            },
        ]

        cloudwatch_client = boto3.client("cloudwatch", "us-east-1")  # type: ignore[misc]
        cloudwatch_client.put_metric_data(  # type: ignore[misc]
            Namespace="LabelsMetrics",
            MetricData=metric_data,
        )
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Unable to send metrics to cloudwatch: %s", exc)
