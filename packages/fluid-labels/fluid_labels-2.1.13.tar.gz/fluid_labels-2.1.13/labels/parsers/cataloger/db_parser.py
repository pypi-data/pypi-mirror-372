import logging
from fnmatch import fnmatch

import reactivex
from reactivex.abc import ObserverBase, SchedulerBase

from labels.model.parser import Request
from labels.parsers.cataloger.alpine.parse_apk_db import parse_apk_db
from labels.parsers.cataloger.arch.parse_alpm import parse_alpm_db
from labels.parsers.cataloger.debian.parse_dpkg_db import parse_dpkg_db
from labels.parsers.cataloger.redhat.parse_rpm_db import parse_rpm_db

LOGGER = logging.getLogger(__name__)


def on_next_db_file(
    source: reactivex.Observable[str],
) -> reactivex.Observable[Request]:
    def subscribe(
        observer: ObserverBase[Request],
        scheduler: SchedulerBase | None = None,
    ) -> reactivex.abc.DisposableBase:
        def on_next(value: str) -> None:
            try:
                if "lib/apk/db/installed" in value:
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_apk_db,
                            parser_name="apk-db-selector",
                        ),
                    )
                elif any(
                    fnmatch(value, x)
                    for x in (
                        "**/var/lib/dpkg/status",
                        "*var/lib/dpkg/status",
                        "/var/lib/dpkg/status",
                        "**/var/lib/dpkg/status.d/*",
                        "*var/lib/dpkg/status.d/*",
                        "/var/lib/dpkg/status.d/*",
                        "**/lib/opkg/info/*.control",
                        "*lib/opkg/info/*.control",
                        "/lib/opkg/info/*.control",
                        "**/lib/opkg/status",
                        "*lib/opkg/status",
                        "/lib/opkg/status",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_dpkg_db,
                            parser_name="dpkg-db-selector",
                        ),
                    )
                elif any(
                    fnmatch(value, pattern)
                    for pattern in (
                        "**/var/lib/pacman/local/**/desc",
                        "var/lib/pacman/local/**/desc",
                        "/var/lib/pacman/local/**/desc",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_alpm_db,
                            parser_name="alpm-db-selector",
                        ),
                    )
                elif any(
                    fnmatch(value, x)
                    for x in (
                        (
                            "**/{var/lib,usr/share,usr/lib/sysimage}"
                            "/rpm/{Packages,Packages.db,rpmdb.sqlite}"
                        ),
                        (
                            "/{var/lib,usr/share,usr/lib/sysimage}"
                            "/rpm/{Packages,Packages.db,rpmdb.sqlite}"
                        ),
                        "**/rpmdb.sqlite",
                        "**/var/lib/rpm/Packages",
                        "**/var/lib/rpm/Packages.db",
                        "**/var/lib/rpm/rpmdb.sqlite",
                        "**/usr/share/rpm/Packages",
                        "**/usr/share/rpm/Packages.db",
                        "**/usr/share/rpm/rpmdb.sqlite",
                        "**/usr/lib/sysimage/rpm/Packages",
                        "**/usr/lib/sysimage/rpm/Packages.db",
                        "**/usr/lib/sysimage/rpm/rpmdb.sqlite",
                        "/var/lib/rpm/Packages",
                        "/var/lib/rpm/Packages.db",
                        "/var/lib/rpm/rpmdb.sqlite",
                        "/usr/share/rpm/Packages",
                        "/usr/share/rpm/Packages.db",
                        "/usr/share/rpm/rpmdb.sqlite",
                        "/usr/lib/sysimage/rpm/Packages",
                        "/usr/lib/sysimage/rpm/Packages.db",
                        "/usr/lib/sysimage/rpm/rpmdb.sqlite",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_rpm_db,
                            parser_name="environment-parser",
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
