from collections.abc import Callable
from fnmatch import fnmatch

import reactivex
from reactivex.abc import ObserverBase, SchedulerBase

from labels.model.parser import Request
from labels.parsers.cataloger.python.parse_pipfile_deps import parse_pipfile_deps
from labels.parsers.cataloger.python.parse_pipfile_lock import parse_pipfile_lock_deps
from labels.parsers.cataloger.python.parse_poetry_lock import parse_poetry_lock
from labels.parsers.cataloger.python.parse_pyproject_toml import parse_pyproject_toml
from labels.parsers.cataloger.python.parse_requirements import parse_requirements_txt
from labels.parsers.cataloger.python.parse_uv_lock import parse_uv_lock
from labels.parsers.cataloger.python.parse_wheel_egg import parse_wheel_or_egg


def _get_parser_config(value: str) -> tuple[str, Callable, str] | None:
    patterns = [
        (
            ("*.txt", "*/*.txt", "*requirements.in", "requirements.in", "*/requirements.in"),
            parse_requirements_txt,
            "python-requirements-cataloger",
        ),
        (
            ("*poetry.lock", "poetry.lock", "*/poetry.lock"),
            parse_poetry_lock,
            "python-poetry-lock-cataloger",
        ),
        (("*uv.lock", "uv.lock", "*/uv.lock"), parse_uv_lock, "python-uv-lock-cataloger"),
        (
            (
                "**/*.egg-info",
                "**/*dist-info/METADATA",
                "**/*egg-info/PKG-INFO",
                "**/*DIST-INFO/METADATA",
                "**/*EGG-INFO/PKG-INFO",
            ),
            parse_wheel_or_egg,
            "python-installed-package-cataloger",
        ),
        (
            ("**/Pipfile.lock", "Pipfile.lock"),
            parse_pipfile_lock_deps,
            "python-pipfile-lock-cataloger",
        ),
        (("**/Pipfile", "Pipfile"), parse_pipfile_deps, "python-pipfile-package-cataloger"),
        (
            ("**/pyproject.toml", "pyproject.toml"),
            parse_pyproject_toml,
            "python-pyproject-toml-cataloger",
        ),
    ]

    for pattern_list, parser_func, parser_name in patterns:
        if any(fnmatch(value, pattern) for pattern in pattern_list):
            return value, parser_func, parser_name
    return None


def on_next_python(
    source: reactivex.Observable[str],
) -> reactivex.Observable[Request]:
    def subscribe(
        observer: ObserverBase[Request],
        scheduler: SchedulerBase | None = None,
    ) -> reactivex.abc.DisposableBase:
        def on_next(value: str) -> None:
            try:
                config = _get_parser_config(value)
                if config:
                    real_path, parser_func, parser_name = config
                    observer.on_next(
                        Request(
                            real_path=real_path,
                            parser=parser_func,
                            parser_name=parser_name,
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
