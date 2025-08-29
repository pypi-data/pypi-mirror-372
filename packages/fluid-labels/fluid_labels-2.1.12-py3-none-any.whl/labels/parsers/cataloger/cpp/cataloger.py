from fnmatch import (
    fnmatch,
)

import reactivex
from reactivex.abc import (
    ObserverBase,
    SchedulerBase,
)

from labels.model.parser import Request
from labels.parsers.cataloger.cpp.parse_conan_file import (
    parse_conan_file,
)
from labels.parsers.cataloger.cpp.parse_conan_file_py import parse_conan_file_py
from labels.parsers.cataloger.cpp.parse_conan_lock import (
    parse_conan_lock,
)


def on_next_cpp(
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
                        "**/conan.lock",
                        "conan.lock",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_conan_lock,
                            parser_name="parse-conan-lock",
                        ),
                    )
                if any(
                    fnmatch(value, x)
                    for x in (
                        "**/conanfile.txt",
                        "conanfile.txt",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_conan_file,
                            parser_name="parse-conan-file",
                        ),
                    )
                if any(
                    fnmatch(value, x)
                    for x in (
                        "**/conanfile.py",
                        "conanfile.py",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_conan_file_py,
                            parser_name="parse-conan-file-py",
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
