import logging
from collections.abc import Callable
from pathlib import Path

import reactivex
from reactivex import Observable
from reactivex.abc import ObserverBase
from reactivex.scheduler import ThreadPoolScheduler

from labels.model.file import Location, LocationReadCloser
from labels.model.package import Package
from labels.model.parser import Task
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver

LOGGER = logging.getLogger(__name__)


def get_file_size(location: Location) -> int:
    try:
        if not location.coordinates:
            return 0
        return Path(location.coordinates.real_path).stat().st_size
    except Exception:
        LOGGER.exception("Error getting file size for %s", location.access_path)
        return 0


def execute_parsers(
    resolver: Resolver,
    environment: Environment,
) -> Callable[[Observable[Task]], Observable]:
    def _handle(source: Observable[Task]) -> Observable:
        def subscribe(
            observer: ObserverBase[tuple[list[Package], list[Relationship], int]],
            scheduler: ThreadPoolScheduler | None = None,
        ) -> reactivex.abc.DisposableBase:
            def on_next(value: Task) -> None:
                LOGGER.debug("Working on %s", value.location.access_path)
                content_reader = resolver.file_contents_by_location(value.location)

                try:
                    if content_reader is not None and (
                        result := value.parser(
                            resolver,
                            environment,
                            LocationReadCloser(location=value.location, read_closer=content_reader),
                        )
                    ):
                        file_size = get_file_size(value.location)
                        discover_packages, relationships = result
                        for pkg in discover_packages:
                            pkg.found_by = value.parser_name
                        observer.on_next((discover_packages, relationships, file_size))
                except Exception as ex:  # noqa: BLE001
                    observer.on_error(ex)

            return source.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler=scheduler,
            )

        return reactivex.create(subscribe)  # type: ignore[arg-type]

    return _handle
