import re

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.elixir.utils import package_url
from labels.parsers.cataloger.utils import get_enriched_location

MIX_LOCK_DEP: re.Pattern[str] = re.compile(r"^\"(?P<dep>[\w]*)\":\{(?P<info>.+)\},")


def parse_mix_lock(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    relationships: list[Relationship] = []

    for line_number, line in enumerate(
        reader.read_closer.read().splitlines(),
        1,
    ):
        if matched := MIX_LOCK_DEP.match(line.replace(" ", "")):
            pkg_name = matched.group("dep")
            pkg_version = matched.group("info").split(",")[2].strip('"')

            new_location = get_enriched_location(
                reader.location, line=line_number, is_transitive=False
            )

            packages.append(
                Package(
                    name=pkg_name,
                    version=pkg_version,
                    type=PackageType.HexPkg,
                    locations=[new_location],
                    p_url=package_url(pkg_name, pkg_version),
                    metadata=None,
                    language=Language.ELIXIR,
                    licenses=[],
                    is_dev=False,
                ),
            )

    return packages, relationships
