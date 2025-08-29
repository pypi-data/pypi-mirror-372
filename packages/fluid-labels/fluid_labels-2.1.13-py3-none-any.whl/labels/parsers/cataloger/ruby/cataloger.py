from fnmatch import fnmatch

import reactivex
from reactivex.abc import ObserverBase, SchedulerBase

from labels.model.parser import Request
from labels.parsers.cataloger.ruby.parse_gemfile import parse_gemfile
from labels.parsers.cataloger.ruby.parse_gemfile_lock import parse_gemfile_lock


def on_next_ruby(
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
                        "**/Gemfile.lock",
                        "Gemfile.lock",
                        "**/gems.locked",
                        "gems.locked",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_gemfile_lock,
                            parser_name="parse-gemfile-lock",
                        ),
                    )
                elif any(fnmatch(value, x) for x in ("**/Gemfile", "Gemfile")):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_gemfile,
                            parser_name="parse-gemfile",
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
