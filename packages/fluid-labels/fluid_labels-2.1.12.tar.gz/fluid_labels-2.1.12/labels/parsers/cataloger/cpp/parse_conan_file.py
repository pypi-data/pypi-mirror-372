import re

from labels.model.file import (
    LocationReadCloser,
)
from labels.model.package import Package
from labels.model.relationship import (
    Relationship,
)
from labels.model.release import Environment
from labels.model.resolver import (
    Resolver,
)
from labels.parsers.cataloger.cpp.package import new_conan_file_dep


def parse_conan_file(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    line_deps: bool = False
    is_dev = False
    for line_number, line in enumerate(
        reader.read_closer.read().splitlines(),
        1,
    ):
        if re.search(r"^\[(tool|build)_requires\]$", line):
            line_deps = True
            is_dev = True
        elif not is_dev and line.startswith("[requires]"):
            line_deps = True
            is_dev = False
        elif line_deps:
            if not line or line.startswith("["):
                line_deps = False
                continue
            new_conan_file_dep(
                line,
                reader,
                line_number,
                is_dev=is_dev,
                packages=packages,
            )
    return packages, []
