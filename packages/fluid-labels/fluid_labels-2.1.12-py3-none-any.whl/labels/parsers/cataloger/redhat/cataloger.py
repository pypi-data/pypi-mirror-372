from fnmatch import (
    fnmatch,
)

import reactivex
from reactivex.abc import (
    ObserverBase,
    SchedulerBase,
)

from labels.model.parser import Request
from labels.parsers.cataloger.redhat.parse_rpm_db import (
    parse_rpm_db,
)


def on_next_redhat(
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
                        # /var/lib/rpm/Packages
                        # /var/lib/rpm/Packages.db
                        "/var/lib/rpm/rpmdb.sqlite",
                        # /usr/share/rpm/Packages
                        # /usr/share/rpm/Packages.db
                        "/usr/share/rpm/rpmdb.sqlite",
                        # /usr/lib/sysimage/rpm/Packages
                        # /usr/lib/sysimage/rpm/Packages.db
                        "/usr/lib/sysimage/rpm/rpmdb.sqlite",
                    )
                ):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_rpm_db,
                            parser_name="redhat-parse-rpmdb",
                        ),
                    )
                if any(fnmatch(value, x) for x in ("**/*.rpm", "*.rpm")):
                    observer.on_next(
                        Request(
                            real_path=value,
                            parser=parse_rpm_db,
                            parser_name="redhat-parse-rpmdb",
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
