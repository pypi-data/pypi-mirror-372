import re

from packageurl import PackageURL

from labels.model.file import Location, LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.graph_parser import Graph, NId, node_to_str
from labels.parsers.cataloger.utils import get_enriched_location


def get_conan_dep_info(dep_line: str) -> tuple[str, str]:
    product, version = re.sub(r"[\"\]\[]", "", dep_line).strip().split("@")[0].split("/")
    if "," in version:
        version = re.sub(r",(?=[<>=])", " ", version).split(",")[0]
    return product, version


def package_url(name: str, version: str) -> str:
    return PackageURL(
        type="conan",
        namespace="",
        name=name,
        version=version,
        qualifiers=None,
        subpath="",
    ).to_string()


def new_conan_file_py_dep(
    *,
    graph: Graph,
    node_id: NId,
    dep_info: str | None = None,
    is_dev: bool,
    location: Location,
) -> Package:
    dep_attrs = graph.nodes[node_id]
    if dep_info is None:
        dep_info = dep_attrs.get("label_text") or node_to_str(graph, node_id)
    dep_info = dep_info.replace("(", "").replace(")", "")
    product, version = get_conan_dep_info(dep_info)
    dep_line = dep_attrs["label_l"]

    new_location = get_enriched_location(location, line=dep_line, is_dev=is_dev)

    return Package(
        name=product,
        version=version,
        type=PackageType.ConanPkg,
        locations=[new_location],
        p_url=package_url(product, version),
        metadata=None,
        language=Language.CPP,
        licenses=[],
        is_dev=is_dev,
    )


def new_conan_file_dep(
    line: str,
    reader: LocationReadCloser,
    line_number: int,
    *,
    is_dev: bool,
    packages: list[Package],
) -> None:
    pkg_name, pkg_version = get_conan_dep_info(line)
    new_location = get_enriched_location(
        reader.location,
        line=line_number,
        is_dev=is_dev,
        is_transitive=False,
    )
    packages.append(
        Package(
            name=pkg_name,
            version=pkg_version,
            type=PackageType.ConanPkg,
            locations=[new_location],
            p_url=package_url(pkg_name, pkg_version),
            metadata=None,
            language=Language.CPP,
            licenses=[],
            is_dev=is_dev,
        ),
    )


def new_conan_lock_dep(
    dep_info: str,
    location: Location,
    *,
    is_dev: bool = False,
) -> Package:
    product, version = dep_info.split("/")
    version = version.split("#")[0]
    return Package(
        name=product,
        version=version,
        type=PackageType.ConanPkg,
        locations=[location],
        p_url=package_url(product, version),
        metadata=None,
        language=Language.CPP,
        licenses=[],
        is_dev=is_dev,
    )
