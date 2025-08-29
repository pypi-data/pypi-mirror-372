import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

from labels.advisories.images import DATABASE as IMAGES_DATABASE
from labels.advisories.roots import DATABASE as ROOTS_DATABASE
from labels.config.bugsnag import initialize_bugsnag
from labels.config.logger import configure_logger, modify_logger_level
from labels.config.utils import guess_environment
from labels.core.source_dispatcher import resolve_sbom_source
from labels.domain.cloudwatch import BaseMetrics, process_sbom_metrics
from labels.domain.tracks import send_event_to_tracks
from labels.enrichers.dispatcher import complete_package, complete_package_advisories_only
from labels.model.core import SbomConfig, SourceType
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.output.dispatcher import dispatch_sbom_output
from labels.parsers.operations.package_operation import package_operations_factory
from labels.resolvers.container_image import ContainerImage
from labels.resolvers.directory import Directory
from labels.utils.tracks import count_vulns_by_severity

LOGGER = logging.getLogger(__name__)


def initialize_scan_environment(sbom_config: SbomConfig) -> None:
    configure_logger(log_to_remote=True)
    initialize_bugsnag()

    if sbom_config.debug:
        modify_logger_level()
    if sbom_config.source_type == SourceType.DIRECTORY:
        ROOTS_DATABASE.initialize()
    else:
        ROOTS_DATABASE.initialize()
        IMAGES_DATABASE.initialize()


def execute_labels_scan(sbom_config: SbomConfig) -> None:
    def check_restricted_licenses(packages: list[Package]) -> None:
        class RestrictedLicenseError(Exception):
            """Raised when a restricted license is found in direct dependencies."""

        if sbom_config.restricted_licenses:
            restricted_found: list[tuple[str, str, str]] = [
                (pkg.name, pkg.version, pkg_license)
                for pkg in packages
                for pkg_license in pkg.licenses
                if pkg_license in sbom_config.restricted_licenses
            ]
            if restricted_found:
                msg = "Restricted license(s) found in direct dependencies:\n" + "\n".join(
                    f"- {name} {version}: {pkg_license}"
                    for name, version, pkg_license in restricted_found
                )
                LOGGER.error(msg)
                raise RestrictedLicenseError(msg)

    try:
        initialize_scan_environment(sbom_config)
        main_sbom_resolver = resolve_sbom_source(sbom_config)
        LOGGER.info(
            "📦 Generating SBOM from %s: %s",
            sbom_config.source_type.value,
            sbom_config.source,
        )
        start_time = time.perf_counter()
        packages, relationships, base_metrics = gather_packages_and_relationships(
            main_sbom_resolver,
            include_package_metadata=sbom_config.include_package_metadata,
        )
        check_restricted_licenses(packages)
        end_time = time.perf_counter()
        process_sbom_metrics(
            sbom_config.execution_id,
            end_time - start_time,
            base_metrics,
            sbom_config.source_type,
        )
        LOGGER.info("📦 Preparing %s report", sbom_config.output_format.value)
        dispatch_sbom_output(
            packages=packages,
            relationships=relationships,
            config=sbom_config,
            resolver=main_sbom_resolver,
        )
        send_event_to_tracks(
            sbom_config=sbom_config,
            packages_amount=len(packages),
            relationships_amount=len(relationships),
            vulns_summary=count_vulns_by_severity(packages),
        )
    except Exception:
        if guess_environment() == "production":
            LOGGER.exception(
                "Error executing labels scan. Output SBOM was not generated.",
                extra={"execution_id": sbom_config.execution_id},
            )
            return
        raise


def gather_packages_and_relationships(
    resolver: Directory | ContainerImage,
    max_workers: int = 32,
    *,
    include_package_metadata: bool = True,
) -> tuple[list[Package], list[Relationship], BaseMetrics]:
    packages, relationships, metrics = package_operations_factory(resolver)

    worker_count = min(
        max_workers,
        (os.cpu_count() or 1) * 5 if os.cpu_count() is not None else max_workers,
    )
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        LOGGER.info("📦 Gathering additional package information")
        if include_package_metadata:
            packages = list(filter(None, executor.map(complete_package, packages)))
        else:
            packages = list(executor.map(complete_package_advisories_only, packages))

    return packages, relationships, metrics
