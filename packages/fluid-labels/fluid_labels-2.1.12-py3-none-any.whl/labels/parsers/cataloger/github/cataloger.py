from fnmatch import fnmatch

import reactivex
from reactivex.abc import ObserverBase, SchedulerBase

from labels.model.parser import Request
from labels.parsers.cataloger.github.parse_github_actions import parse_github_actions_deps


def on_next_github_action(
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
                        "**/.github/workflows/*.yaml",
                        "**/.github/workflows/*.yml",
                        ".github/workflows/*.yaml",
                        ".github/workflows/*.yml",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_github_actions_deps,
                            parser_name="parse-github-actions-deps",
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
