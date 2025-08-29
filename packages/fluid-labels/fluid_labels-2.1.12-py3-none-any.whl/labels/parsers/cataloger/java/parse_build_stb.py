import re

from packageurl import (
    PackageURL,
)

from labels.model.file import (
    LocationReadCloser,
)
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import (
    Relationship,
)
from labels.model.release import Environment
from labels.model.resolver import (
    Resolver,
)
from labels.parsers.cataloger.utils import get_enriched_location

QUOTE = r'["\']'
NL = r"(\n?\s*)?"
TEXT = r'[^"\']+'
RE_SBT: re.Pattern[str] = re.compile(
    r"^[^%]*"
    rf"{NL}{QUOTE}(?P<group>{TEXT}){QUOTE}{NL}%"
    rf"{NL}{QUOTE}(?P<name>{TEXT}){QUOTE}{NL}%"
    rf"{NL}{QUOTE}(?P<version>{TEXT}){QUOTE}{NL}"
    r".*$",
)

VERSION_VAR_RE: re.Pattern[str] = re.compile(
    rf"^\s*val\s+(?P<var_name>\w+)(?:\s*:\s*\w+)?\s*=\s*{QUOTE}(?P<value>{TEXT}){QUOTE}\s*$",
)

VERSION_REF_RE: re.Pattern[str] = re.compile(
    rf"{QUOTE}(?P<group>{TEXT}){QUOTE}\s*%%?\s*{QUOTE}(?P<name>{TEXT}){QUOTE}\s*%\s*(?P<version_var>\w+)",
)


def build_stb(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages = []
    version_vars = {}
    content = reader.read_closer.read()

    for line in content.splitlines():
        if match := VERSION_VAR_RE.match(line):
            version_vars[match.group("var_name")] = match.group("value")

    for line_no, line in enumerate(content.splitlines(), start=1):
        if match := RE_SBT.match(line):
            product = str(match.group("group")) + ":" + match.group("name")
            version = match.group("version")
        elif match := VERSION_REF_RE.search(line):
            product = str(match.group("group")) + ":" + match.group("name")
            version_var = match.group("version_var")
            version = version_vars.get(version_var, "unknown")
        else:
            continue

        new_location = get_enriched_location(reader.location, line=line_no, is_transitive=False)

        packages.append(
            Package(
                name=product,
                version=version,
                type=PackageType.JavaPkg,
                locations=[new_location],
                p_url=PackageURL(
                    type="maven",
                    namespace=str(match.group("group")),
                    name=str(match.group("name")),
                    version=version,
                    qualifiers=None,
                    subpath="",
                ).to_string(),
                metadata=None,
                language=Language.JAVA,
                licenses=[],
                is_dev=False,
            ),
        )
    return packages, []
