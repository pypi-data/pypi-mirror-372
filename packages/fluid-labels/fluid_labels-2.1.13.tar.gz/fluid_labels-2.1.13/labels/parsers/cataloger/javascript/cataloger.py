from fnmatch import fnmatch

import reactivex
from reactivex.abc import ObserverBase, SchedulerBase

from labels.model.parser import Request
from labels.parsers.cataloger.javascript.parse_html_scripts import parse_html_scripts
from labels.parsers.cataloger.javascript.parse_package_json import parse_package_json
from labels.parsers.cataloger.javascript.parse_package_lock import parse_package_lock
from labels.parsers.cataloger.javascript.parse_pnpm_lock import parse_pnpm_lock
from labels.parsers.cataloger.javascript.parse_yarn_lock import parse_yarn_lock


def on_next_javascript(
    source: reactivex.Observable[str],
) -> reactivex.Observable[Request]:
    def subscribe(
        observer: ObserverBase[Request],
        scheduler: SchedulerBase | None = None,
    ) -> reactivex.abc.DisposableBase:
        def on_next(value: str) -> None:
            patterns = [
                (
                    ("**/package.json", "package.json"),
                    parse_package_json,
                    "javascript-parse-package-json",
                ),
                (
                    ("**/package-lock.json", "package-lock.json"),
                    parse_package_lock,
                    "javascript-parse-package-lock",
                ),
                (
                    ("**/yarn.lock", "yarn.lock"),
                    parse_yarn_lock,
                    "javascript-parse-yarn-lock",
                ),
                (
                    ("**/pnpm-lock.yaml", "pnpm-lock.yaml"),
                    parse_pnpm_lock,
                    "javascript-parse-pnpm-lock",
                ),
                (
                    ("*.html",),
                    parse_html_scripts,
                    "javascript-parse-html-scripts",
                ),
            ]
            try:
                for pattern, parser, parser_name in patterns:
                    if any(fnmatch(value, x) for x in pattern):
                        observer.on_next(
                            Request(
                                real_path=value,
                                parser=parser,
                                parser_name=parser_name,
                            ),
                        )
                        break
            except Exception as ex:  # noqa: BLE001
                observer.on_error(ex)

        return source.subscribe(
            on_next,
            observer.on_error,
            observer.on_completed,
            scheduler=scheduler,
        )

    return reactivex.create(subscribe)
