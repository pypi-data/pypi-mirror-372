from fnmatch import fnmatch

import reactivex
from reactivex.abc import ObserverBase, SchedulerBase

from labels.model.parser import Request
from labels.parsers.cataloger.golang.parse_go_mod import parse_go_mod


def on_next_golang(
    source: reactivex.Observable[str],
) -> reactivex.Observable[Request]:
    def subscribe(
        observer: ObserverBase[Request],
        scheduler: SchedulerBase | None = None,
    ) -> reactivex.abc.DisposableBase:
        def on_next(value: str) -> None:
            try:
                if any(
                    fnmatch(value, x)
                    for x in (
                        "**/go.mod",
                        "go.mod",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_go_mod,
                            parser_name="parse-go-mod",
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
