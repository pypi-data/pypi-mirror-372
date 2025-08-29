import logging
from typing import cast

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, ParsedValue
from labels.model.package import Package
from labels.model.relationship import Relationship, RelationshipType
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.javascript.package import new_package_lock_v1, new_package_lock_v2
from labels.parsers.collection.json import parse_json_with_tree_sitter

LOGGER = logging.getLogger(__name__)
EMPTY_DICT: IndexedDict[str, ParsedValue] = IndexedDict()


def get_name_from_path(name: str) -> str:
    return name.split("node_modules/")[-1]


def get_direct_dependencies(package_lock_path: IndexedDict[str, ParsedValue]) -> list[str]:
    all_dependencies: ParsedValue = package_lock_path.get("dependencies", IndexedDict())

    transitives: set[str] = set()
    for details in cast("IndexedDict[str, ParsedValue]", all_dependencies).values():
        if not isinstance(details, IndexedDict):
            continue
        reqs = cast("IndexedDict[str, ParsedValue]", details.get("requires", EMPTY_DICT))
        for dep in reqs:
            transitives.add(dep)

    return [
        dep
        for dep in cast("IndexedDict[str, ParsedValue]", all_dependencies)
        if dep not in transitives
    ]


def get_direct_dependencies_v2_v3(package_lock_path: IndexedDict[str, ParsedValue]) -> list[str]:
    all_dependencies: ParsedValue = package_lock_path.get("packages", IndexedDict())
    if not isinstance(all_dependencies, IndexedDict):
        LOGGER.warning("No direct deps found found in package JSON")
        return []

    result: list[str] = []
    for dep, value in all_dependencies.items():
        if isinstance(value, IndexedDict) and dep == "":
            deps_candidate: ParsedValue = value.get("dependencies", EMPTY_DICT)
            if isinstance(deps_candidate, IndexedDict):
                result.extend(deps_candidate)
            dev_deps_candidate: ParsedValue = value.get("devDependencies", EMPTY_DICT)
            if isinstance(dev_deps_candidate, IndexedDict):
                result.extend(dev_deps_candidate)
    return result


def _solve_sub_dependencies(
    reader: LocationReadCloser,
    sub_deps: IndexedDict[str, ParsedValue],
) -> list[Package]:
    packages = []
    for dep_key, dep_value in sub_deps.items():
        if isinstance(dep_value, IndexedDict):
            pkg = new_package_lock_v1(
                reader.location,
                dep_key,
                dep_value,
                is_transitive=True,
            )
            if pkg:
                packages.append(pkg)

            nested_sub_deps = dep_value.get("dependencies", EMPTY_DICT)
            if isinstance(nested_sub_deps, IndexedDict):
                packages.extend(_solve_sub_dependencies(reader, nested_sub_deps))
    return packages


def handle_v1(
    reader: LocationReadCloser,
    package_json: IndexedDict[str, ParsedValue],
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    relationships: list[Relationship] = []

    deps: ParsedValue = package_json.get("dependencies", IndexedDict())
    direct_dependencies = get_direct_dependencies(package_json)
    if not isinstance(deps, IndexedDict):
        LOGGER.warning("No packages found in package JSON")
        return ([], [])
    for dependency_key, dependency_value in deps.items():
        if not isinstance(dependency_value, IndexedDict):
            continue
        name: str = dependency_key
        is_transitive = name not in direct_dependencies
        if pkg := new_package_lock_v1(
            reader.location,
            name,
            dependency_value,
            is_transitive=is_transitive,
        ):
            packages.append(pkg)

        requires = [
            package
            for package in packages
            if package.name
            in cast("IndexedDict[str, ParsedValue]", dependency_value.get("requires", EMPTY_DICT))
        ]
        sub_deps: ParsedValue = dependency_value.get("dependencies", EMPTY_DICT)
        if sub_deps and isinstance(sub_deps, IndexedDict):
            packages.extend(_solve_sub_dependencies(reader, sub_deps))
        current_package: Package | None = next(
            (package for package in packages if package.name == dependency_key),
            None,
        )
        if not current_package:
            continue
        relationships.extend(
            [
                Relationship(
                    from_=require.id_,
                    to_=current_package.id_,
                    type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                )
                for require in requires
            ],
        )
    return packages, relationships


def _get_name(dependency_key: str, package_value: IndexedDict[str, ParsedValue]) -> str | None:
    name = dependency_key
    if not name:
        if "name" not in package_value:
            return None
        name = str(package_value["name"])

    # handle alias name
    if "name" in package_value and package_value["name"] != dependency_key:
        name = str(package_value["name"])

    return get_name_from_path(name)


def handle_v2(
    reader: LocationReadCloser,
    package_json: IndexedDict[str, ParsedValue],
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    relationships: list[Relationship] = []
    pkgs: ParsedValue = package_json.get("packages", IndexedDict())
    if not isinstance(pkgs, IndexedDict):
        LOGGER.warning("No packages found in package JSON")
        return ([], [])
    dependency_map: dict[str, ParsedValue] = {}
    direct_dependencies = get_direct_dependencies_v2_v3(package_json)
    for dependency_key, package_value in pkgs.items():
        if not dependency_key or not isinstance(package_value, IndexedDict):
            continue
        name = _get_name(dependency_key, package_value)
        is_transitive = name not in direct_dependencies
        if pkg := new_package_lock_v2(
            reader.location,
            get_name_from_path(name or dependency_key),
            package_value,
            is_transitive=is_transitive,
        ):
            packages.append(pkg)
            dependencies = package_value.get("dependencies", EMPTY_DICT)
            dependency_map[name or dependency_key] = dependencies

    for pkg in packages:
        dependencies = dependency_map.get(pkg.name, IndexedDict())
        if not isinstance(dependencies, IndexedDict):
            continue
        for dep_name in dependencies:
            dependency_pkg = next((p for p in packages if p.name == dep_name), None)
            if dependency_pkg:
                relationships.append(
                    Relationship(
                        from_=dependency_pkg.id_,
                        to_=pkg.id_,
                        type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
                    ),
                )

    return packages, relationships


def parse_package_lock(
    _resolver: Resolver | None,
    _environment: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    package_json: IndexedDict[str, ParsedValue] = cast(
        "IndexedDict[str, ParsedValue]",
        parse_json_with_tree_sitter(reader.read_closer.read()),
    )
    packages: list[Package] = []
    relationships: list[Relationship] = []

    match package_json.get("lockfileVersion", 1):
        case 1:
            return handle_v1(reader, package_json)
        case 2 | 3:
            return handle_v2(reader, package_json)
    return packages, relationships
