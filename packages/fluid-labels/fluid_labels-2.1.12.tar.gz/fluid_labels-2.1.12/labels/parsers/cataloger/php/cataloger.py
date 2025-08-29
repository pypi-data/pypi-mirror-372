from fnmatch import fnmatch

import reactivex
from reactivex.abc import ObserverBase, SchedulerBase

from labels.model.parser import Request
from labels.parsers.cataloger.php.parse_composer_json import parse_composer_json
from labels.parsers.cataloger.php.parse_composer_lock import parse_composer_lock
from labels.parsers.cataloger.php.parse_installed_json import parse_installed_json
from labels.parsers.cataloger.php.parse_serialized import parse_pecl_serialized


def on_next_php(
    source: reactivex.Observable[str],
) -> reactivex.Observable[Request]:
    def subscribe(
        observer: ObserverBase[Request],
        scheduler: SchedulerBase | None = None,
    ) -> reactivex.abc.DisposableBase:
        def on_next(value: str) -> None:
            try:
                if any(
                    fnmatch(value, pattern) for pattern in ("**/composer.lock", "composer.lock")
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_composer_lock,
                            parser_name="parse-php-composer-lock",
                        ),
                    )
                elif any(
                    fnmatch(value, pattern) for pattern in ("**/composer.json", "composer.json")
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_composer_json,
                            parser_name="parse-php-composer-json",
                        ),
                    )
                elif any(
                    fnmatch(value, pattern) for pattern in ("**/installed.json", "installed.json")
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_installed_json,
                            parser_name="parse-php-installed-json",
                        ),
                    )
                elif fnmatch(value, "**/php/.registry/.channel.*/*.reg"):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_pecl_serialized,
                            parser_name="parse-php-pecl-serialized",
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
