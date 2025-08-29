import logging
import re

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.java.package import package_url
from labels.parsers.cataloger.utils import get_enriched_location

LOGGER = logging.getLogger(__name__)

GRADLE_DIST = re.compile("^distributionUrl=.+gradle-(?P<gradle_version>[^-]+)-.+")


def parse_gradle_properties(
    _resolver: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages = []
    for line_no, raw_line in enumerate(reader.read_closer.readlines(), start=1):
        line = raw_line.strip()
        if (match := GRADLE_DIST.match(line)) and (version := match.group("gradle_version")):
            new_location = get_enriched_location(reader.location, line=line_no)

            packages.append(
                Package(
                    name="gradle",
                    version=version,
                    locations=[new_location],
                    language=Language.JAVA,
                    type=PackageType.JavaPkg,
                    p_url=package_url("gradle", version),
                    licenses=[],
                ),
            )

    return packages, []
