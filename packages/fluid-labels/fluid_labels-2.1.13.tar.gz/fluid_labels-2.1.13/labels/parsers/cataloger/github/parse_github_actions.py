from typing import cast

from packageurl import PackageURL

from labels.model.file import LocationReadCloser
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.utils import get_enriched_location
from labels.parsers.collection.yaml import parse_yaml_with_tree_sitter
from labels.utils.strings import normalize_name


def package_url(name: str, version: str) -> str:
    return PackageURL(  # type: ignore[misc]
        type="github",
        namespace="",
        name=name,
        version=version,
        qualifiers=None,
        subpath="",
    ).to_string()


def extract_dep(step: IndexedDict[str, ParsedValue]) -> tuple[str, int] | None:
    uses = step.get("uses")
    if not isinstance(uses, str):
        return None
    if "name" in step:
        line_number = step.get_key_position("name").start.line
    else:
        line_number = step.get_key_position("uses").start.line

    return uses, line_number


def _get_deps(jobs: IndexedDict[str, ParsedValue]) -> list[tuple[str, int]]:
    deps: list[tuple[str, int]] = []
    for job in jobs.values():
        if isinstance(job, IndexedDict):
            steps = job.get("steps")
            if isinstance(steps, IndexedList):
                deps.extend(
                    filter(
                        None,
                        (extract_dep(step) for step in steps if isinstance(step, IndexedDict)),
                    ),
                )
    return deps


def parse_github_actions_deps(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    parsed_content = cast(
        "IndexedDict[str, ParsedValue]",
        parse_yaml_with_tree_sitter(reader.read_closer.read()),
    )
    if not parsed_content:
        return packages, []
    jobs = parsed_content.get("jobs")
    if not jobs or not isinstance(jobs, IndexedDict):
        return packages, []

    for dep, line_number in _get_deps(jobs):
        dep_info = dep.rsplit("@", 1)
        new_location = get_enriched_location(reader.location, line=line_number, is_dev=True)

        if len(dep_info) == 2:
            normalized_name = normalize_name(dep_info[0], PackageType.GithubActionPkg)
            p_url = package_url(normalized_name, dep_info[1])

            packages.append(
                Package(
                    name=normalized_name,
                    version=dep_info[1],
                    language=Language.GITHUB_ACTIONS,
                    licenses=[],
                    locations=[new_location],
                    type=PackageType.GithubActionPkg,
                    metadata=None,
                    p_url=p_url,
                ),
            )
    return packages, []
