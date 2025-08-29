import logging
import re

from bs4 import BeautifulSoup
from bs4.element import Tag
from packageurl import PackageURL

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.utils import get_enriched_location

LOGGER = logging.getLogger(__name__)


def parse_dotnet_config_executable(
    _resolver: Resolver | None,
    _env: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages = []
    root = BeautifulSoup(reader.read_closer.read(), features="html.parser")
    net_dep = re.compile(r".NETFramework,Version=v(?P<version>[^\s,]*)")
    net_runtime = root.find("supportedruntime")
    if (
        isinstance(net_runtime, Tag)
        and isinstance(net_runtime.parent, Tag)
        and net_runtime.parent.name == "startup"
        and (runtime_info := net_runtime.get("sku", ""))
        and (version_match := net_dep.match(str(runtime_info)))
    ):
        version = version_match.group("version")

        new_location = get_enriched_location(
            reader.location, line=net_runtime.sourceline, is_transitive=False, is_dev=False
        )

        packages.append(
            Package(
                name="netframework",
                version=version,
                locations=[new_location],
                licenses=[],
                type=PackageType.DotnetPkg,
                language=Language.DOTNET,
                metadata=None,
                p_url=PackageURL(
                    type="nuget",
                    namespace="",
                    name="netframework",
                    version=version,
                    qualifiers={},
                    subpath="",
                ).to_string(),
            ),
        )

    return packages, []
