import re
from typing import cast

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.elixir.utils import package_url
from labels.parsers.cataloger.utils import get_enriched_location

MIX_DEP: re.Pattern[str] = re.compile(
    r"\{:(?P<dep>[\w]*),\s\"~>\s(?P<version>[\d.]+)\".+",
)


def parse_mix_exs(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    relationships: list[Relationship] = []
    is_line_deps = False

    for line_number, raw_line in enumerate(
        reader.read_closer.read().splitlines(),
        1,
    ):
        line = raw_line.strip()
        if line == "defp deps do":
            is_line_deps = True
        elif is_line_deps:
            if line == "end":
                break
            if matched := MIX_DEP.match(line):
                is_dev = ":dev" in line
                pkg_name = cast("str", matched.group("dep"))
                pkg_version = cast("str", matched.group("version"))

                new_location = get_enriched_location(
                    reader.location, line=line_number, is_dev=is_dev, is_transitive=False
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
                        is_dev=is_dev,
                    ),
                )
    return packages, relationships
