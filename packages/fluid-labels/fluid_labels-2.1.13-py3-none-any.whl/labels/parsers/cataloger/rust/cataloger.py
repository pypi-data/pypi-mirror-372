from fnmatch import fnmatch

import reactivex
from reactivex.abc import ObserverBase, SchedulerBase

from labels.model.parser import Request
from labels.parsers.cataloger.rust.parse_cargo_lock import parse_cargo_lock
from labels.parsers.cataloger.rust.parse_cargo_toml import parse_cargo_toml


def on_next_rust(
    source: reactivex.Observable[str],
) -> reactivex.Observable[Request]:
    def subscribe(
        observer: ObserverBase[Request],
        scheduler: SchedulerBase | None = None,
    ) -> reactivex.abc.DisposableBase:
        def on_next(value: str) -> None:
            try:
                if any(fnmatch(value, pattern) for pattern in ("**/Cargo.lock", "Cargo.lock")):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_cargo_lock,
                            parser_name="parse-rust-cargo-lock",
                        ),
                    )
                elif any(fnmatch(value, pattern) for pattern in ("**/Cargo.toml", "Cargo.toml")):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_cargo_toml,
                            parser_name="parse-rust-cargo-toml",
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
