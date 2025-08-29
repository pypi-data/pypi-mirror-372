from fnmatch import fnmatch

import reactivex
from reactivex.abc import ObserverBase, SchedulerBase

from labels.model.parser import Request
from labels.parsers.cataloger.dotnet.parse_csproj import parse_csproj
from labels.parsers.cataloger.dotnet.parse_dotnet_exe_config import parse_dotnet_config_executable
from labels.parsers.cataloger.dotnet.parse_dotnet_package_config import parse_dotnet_pkgs_config
from labels.parsers.cataloger.dotnet.parse_dotnet_package_lock import parse_dotnet_package_lock
from labels.parsers.cataloger.dotnet.parse_dotnet_portable_executable import (
    parse_dotnet_portable_executable,
)


def on_next_dotnet(
    source: reactivex.Observable[str],
) -> reactivex.Observable[Request]:
    def subscribe(
        observer: ObserverBase[Request],
        scheduler: SchedulerBase | None = None,
    ) -> reactivex.abc.DisposableBase:
        def on_next(value: str) -> None:
            patterns = [
                (
                    ("**/packages.config", "packages.config"),
                    parse_dotnet_pkgs_config,
                    "dotnet-parse-packages-config",
                ),
                (
                    ("**/packages.lock.json", "packages.lock.json"),
                    parse_dotnet_package_lock,
                    "dotnet-parse-package-lock",
                ),
                (
                    ("**/*.csproj", "*.csproj"),
                    parse_csproj,
                    "dotnet-parse-csproj",
                ),
                (
                    ("**/*.dll", "*.dll", "**/*.exe", "*.exe"),
                    parse_dotnet_portable_executable,
                    "dotnet-parse-portable-executable",
                ),
                (
                    ("**/*.exe.config", "*.exe.config"),
                    parse_dotnet_config_executable,
                    "dotnet-parse-config-executable",
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
