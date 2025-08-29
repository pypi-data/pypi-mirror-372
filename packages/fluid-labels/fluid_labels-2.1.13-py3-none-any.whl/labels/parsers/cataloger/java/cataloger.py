from fnmatch import fnmatch

import reactivex
from reactivex.abc import ObserverBase, SchedulerBase

from labels.model.parser import Request
from labels.parsers.cataloger.java.archive_parser import parse_java_archive
from labels.parsers.cataloger.java.parse_android_apk import parse_apk
from labels.parsers.cataloger.java.parse_build_stb import build_stb
from labels.parsers.cataloger.java.parse_gradle import parse_gradle
from labels.parsers.cataloger.java.parse_gradle_kts import parse_gradle_lockfile_kts
from labels.parsers.cataloger.java.parse_gradle_lockfile import parse_gradle_lockfile
from labels.parsers.cataloger.java.parse_gradle_properties import parse_gradle_properties
from labels.parsers.cataloger.java.parse_pom_xml import parse_pom_xml


def on_next_java(  # mccabe: disable=MC0001
    source: reactivex.Observable[str],
) -> reactivex.Observable[Request]:
    def subscribe(
        observer: ObserverBase[Request],
        scheduler: SchedulerBase | None = None,
    ) -> reactivex.abc.DisposableBase:
        def on_next(value: str) -> None:
            patterns = [
                (
                    ("**/*.xml", "*.xml"),
                    parse_pom_xml,
                    "java-parse-pom-xml",
                ),
                (
                    (
                        "**/*.jar",
                        "*.jar",
                        "**/*.war",
                        "*.war",
                        "**/*.ear",
                        "*.ear",
                        "**/*.par",
                        "*.par",
                        "**/*.sar",
                        "*.sar",
                        "**/*.nar",
                        "*.nar",
                        "**/*.jpi",
                        "*.jpi",
                        "**/*.hpi",
                        "*.hpi",
                        "**/*.lpkg",
                        "*.lpkg",
                    ),
                    parse_java_archive,
                    "java-archive-parse",
                ),
                (
                    (
                        "gradle.lockfile*",
                        "**/gradle.lockfile*",
                    ),
                    parse_gradle_lockfile,
                    "java-parse-gradle-lock",
                ),
                (
                    (
                        "**/*.gradle",
                        "/*.gradle",
                        "*.gradle",
                    ),
                    parse_gradle,
                    "java-parse-gradle-lock",
                ),
                (
                    (
                        "**/*.gradle.kts",
                        "*.gradle.kts",
                    ),
                    parse_gradle_lockfile_kts,
                    "java-parse-gradle-kts",
                ),
                (
                    (
                        "**/*.apk",
                        "*.apk",
                    ),
                    parse_apk,
                    "java-parse-apk",
                ),
                (
                    (
                        "**/build.sbt",
                        "build.sbt",
                    ),
                    build_stb,
                    "java-parse-build-stb",
                ),
                (
                    (
                        "**/gradle-wrapper.properties",
                        "/gradle-wrapper.properties",
                        "gradle-wrapper.properties",
                    ),
                    parse_gradle_properties,
                    "java-parse-gradle-properties",
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
