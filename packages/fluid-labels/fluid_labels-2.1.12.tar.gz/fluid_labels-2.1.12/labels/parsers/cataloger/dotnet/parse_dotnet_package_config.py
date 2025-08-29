from bs4 import BeautifulSoup
from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning
from labels.utils.strings import normalize_name


def parse_dotnet_pkgs_config(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    root = BeautifulSoup(reader.read_closer.read(), features="html.parser")
    packages = []

    for pkg in root.find_all("package", recursive=True):
        name: str | None = pkg.get("id")
        version: str | None = pkg.get("version")

        if not name or not version:
            continue

        new_location = get_enriched_location(
            reader.location, line=pkg.sourceline, is_transitive=False
        )

        normalized_package_name = normalize_name(name, PackageType.DotnetPkg)
        p_url = PackageURL(
            type="nuget",
            namespace="",
            name=normalized_package_name,
            version=version,
            qualifiers={},
            subpath="",
        ).to_string()

        try:
            packages.append(
                Package(
                    name=normalized_package_name,
                    version=version,
                    locations=[new_location],
                    language=Language.DOTNET,
                    licenses=[],
                    type=PackageType.DotnetPkg,
                    metadata=None,
                    p_url=p_url,
                ),
            )
        except ValidationError as ex:
            log_malformed_package_warning(new_location, ex)
            continue

    return packages, []
