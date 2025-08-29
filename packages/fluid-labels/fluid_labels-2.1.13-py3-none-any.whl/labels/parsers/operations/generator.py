from collections.abc import Callable

import reactivex
from reactivex import Observable
from reactivex.abc import ObserverBase, SchedulerBase

from labels.model.parser import Request, Task
from labels.model.resolver import Resolver


def gen_location_tasks(
    resolver: Resolver,
) -> Callable[[Observable[Request]], Observable]:
    def _handle(source: Observable[Request]) -> Observable:
        def subscribe(
            observer: ObserverBase[Task],
            scheduler: SchedulerBase | None = None,
        ) -> reactivex.abc.DisposableBase:
            def on_next(value: Request) -> None:
                try:
                    locations = resolver.files_by_path(value.real_path)
                    for location in locations:
                        observer.on_next(
                            Task(
                                location=location,
                                parser=value.parser,
                                parser_name=value.parser_name,
                            ),
                        )
                except Exception as ex:  # noqa: BLE001
                    observer.on_error(ex)

            return source.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler=scheduler,
            )

        return reactivex.create(subscribe)

    return _handle
