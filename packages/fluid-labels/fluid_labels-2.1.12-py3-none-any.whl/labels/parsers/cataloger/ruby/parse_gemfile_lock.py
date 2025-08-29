import logging
import re

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.ruby.package import package_url
from labels.parsers.cataloger.utils import get_enriched_location

LOGGER = logging.getLogger(__name__)

GEM_LOCK_DEP: re.Pattern[str] = re.compile(r"^\s{4}(?P<gem>[^\s]*)\s\([^\d]*(?P<version>.*)\)$")


def parse_gemfile_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    relationships: list[Relationship] = []
    line_gem: bool = False

    for line_number, line in enumerate(
        reader.read_closer.read().splitlines(),
        1,
    ):
        if line.startswith("GEM"):
            line_gem = True
        elif line_gem:
            if matched := GEM_LOCK_DEP.match(line):
                pkg_name = matched.group("gem")
                pkg_version = matched.group("version")

                new_location = get_enriched_location(
                    reader.location, line=line_number, is_transitive=False
                )

                packages.append(
                    Package(
                        name=pkg_name,
                        version=pkg_version,
                        type=PackageType.GemPkg,
                        locations=[new_location],
                        p_url=package_url(pkg_name, pkg_version),
                        metadata=None,
                        language=Language.RUBY,
                        licenses=[],
                        is_dev=False,
                    ),
                )
            elif not line:
                break

    return packages, relationships
