import logging
import multiprocessing
import traceback

import reactivex
from reactivex import Observable
from reactivex import operators as ops
from reactivex.scheduler import ThreadPoolScheduler

from labels.domain.cloudwatch import BaseMetrics
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.operations.cataloger import execute_parsers
from labels.parsers.operations.generator import gen_location_tasks
from labels.parsers.operations.handler import handle_parser
from labels.parsers.operations.utils import handle_relationships, identify_release

LOGGER = logging.getLogger(__name__)


def log_and_continue(e: Exception, file_item: str) -> Observable[None]:
    LOGGER.error(
        "Error found while resolving packages of %s: %s: %s",
        file_item,
        str(e),
        traceback.format_exc(),
    )
    return reactivex.empty()


def process_file_item(
    file_item: str,
    resolver: Resolver,
    pool_scheduler: ThreadPoolScheduler,
) -> Observable[tuple[list[Package], list[Relationship], int]]:
    return reactivex.just(file_item).pipe(
        handle_parser(scheduler=pool_scheduler),
        gen_location_tasks(resolver),
        execute_parsers(resolver, Environment(linux_release=identify_release(resolver))),
        ops.catch(lambda e, _: log_and_continue(e, file_item)),
    )


def package_operations_factory(
    resolver: Resolver,
) -> tuple[list[Package], list[Relationship], BaseMetrics]:
    observer: Observable[str] = reactivex.from_iterable(resolver.walk_file())
    result_packages: list[Package] = []
    result_relations: list[Relationship] = []
    file_sizes: list[int] = []
    completed_event = multiprocessing.Event()
    errors = []

    def on_completed() -> None:
        completed_event.set()

    def on_error(error: Exception) -> None:
        errors.append(error)
        on_completed()

    def on_next(value: tuple[list[Package], list[Relationship], int]) -> None:
        packages, relations, file_size = value
        result_packages.extend(packages)
        result_relations.extend(relations)
        file_sizes.append(file_size)

    optimal_thread_count = multiprocessing.cpu_count()
    pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

    final_obs: Observable[tuple[list[Package], list[Relationship], int]] = observer.pipe(
        ops.map(
            lambda file_item: process_file_item(file_item, resolver, pool_scheduler),  # type: ignore[arg-type]
        ),
        ops.merge(max_concurrent=optimal_thread_count),
    )
    final_obs.subscribe(on_next=on_next, on_error=on_error, on_completed=on_completed)

    completed_event.wait()
    result_relations.extend(handle_relationships(result_packages))

    return (
        result_packages,
        result_relations,
        BaseMetrics(files_amount=len(file_sizes), files_size=sum(file_sizes)),
    )
