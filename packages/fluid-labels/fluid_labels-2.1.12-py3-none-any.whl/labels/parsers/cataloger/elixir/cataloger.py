from fnmatch import (
    fnmatch,
)

import reactivex
from reactivex.abc import (
    ObserverBase,
    SchedulerBase,
)

from labels.model.parser import Request
from labels.parsers.cataloger.elixir.parse_mix_exs import (
    parse_mix_exs,
)
from labels.parsers.cataloger.elixir.parse_mix_lock import (
    parse_mix_lock,
)


def on_next_elixir(
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
                        "**/mix.lock",
                        "mix.lock",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_mix_lock,
                            parser_name="parse-elixir-mix-lock",
                        ),
                    )
                if any(
                    fnmatch(value, x)
                    for x in (
                        "**/mix.exs",
                        "mix.exs",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_mix_exs,
                            parser_name="parse-elixir-mix-exs",
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
