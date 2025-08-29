import glob
import os
import re
from collections.abc import Generator
from fnmatch import translate
from pathlib import Path
from typing import TextIO, cast

from labels.model.file import Coordinates, Location, Metadata, Type
from labels.model.resolver import (
    ContentResolver,
    FileReader,
    MetadataResolver,
    PathResolver,
    Resolver,
)

REPLACE_SET = {
    "[": "[[]",
    "]": "[]]",
}


def _normalize_rules(rules: tuple[str, ...]) -> tuple[str, ...]:
    normalized_rules: list[str] = []
    for rule in rules:
        new_rule = rule
        if new_rule.startswith("glob(") and new_rule.endswith(")"):
            new_rule = new_rule[5:-1]
        elif "[" in new_rule:
            new_rule = "".join(REPLACE_SET.get(char, char) for char in new_rule)
        if new_rule == ".":
            new_rule = "**"
        if new_rule.endswith("/"):
            new_rule += "**"
        if new_rule.startswith("**/"):
            normalized_rules.append(new_rule[3:])
        normalized_rules.append(new_rule)
    return tuple(normalized_rules)


class DirectoryPathResolver(PathResolver):
    root: str
    include: tuple[str, ...]
    exclude: tuple[str, ...]

    def __init__(
        self,
        root: str,
        include: tuple[str, ...] = (".",),
        exclude: tuple[str, ...] = (),
    ) -> None:
        self.root = os.path.realpath(root)
        self.include = include
        self.exclude = exclude

    def has_path(self, path: str) -> bool:
        return (Path(self.root) / path.lstrip("/")).exists()

    def files_by_path(self, *paths: str) -> list[Location]:
        locations: list[Location] = []
        for path in paths:
            relative_path = path.replace(self.root, "").lstrip("/")
            full_path = os.path.join(self.root, relative_path)  # noqa: PTH118
            if Path(full_path).exists():
                locations.append(
                    Location(
                        coordinates=Coordinates(real_path=full_path, file_system_id=""),
                        access_path=relative_path,
                        annotations={},
                    ),
                )
        return locations

    def files_by_glob(self, *patters: str) -> list[Location]:
        result: list[Location] = []
        for pattern in patters:
            result.extend(
                Location(
                    coordinates=Coordinates(
                        real_path=os.path.join(self.root, item),  # noqa: PTH118
                        file_system_id="",
                    ),
                    access_path=item,
                    annotations={},
                )
                for item in glob.glob(pattern, root_dir=self.root, recursive=True)  # noqa: PTH207
            )

        return result

    def relative_file_path(self, _: Location, _path: str) -> Location:
        real_path = os.path.realpath(_path)
        return Location(
            coordinates=Coordinates(real_path=real_path, file_system_id="", line=None),
            access_path=real_path.replace(self.root, "").lstrip("/"),
        )

    def walk_file(self) -> Generator[str, None, None]:
        excluded_dirs = ["node_modules", "dist", "__pycache__"]
        exclude_regex = [
            translate(os.path.join(self.root, rule))  # noqa: PTH118
            for rule in _normalize_rules(self.exclude)
        ]
        include_regex = [
            translate(os.path.join(self.root, rule))  # noqa: PTH118
            for rule in _normalize_rules(self.include)
        ]

        for dirpath, _, filenames in os.walk(self.root):
            if any(
                (
                    dirpath.endswith(excluded_dir)
                    or f"{os.path.sep}{excluded_dir}{os.path.sep}" in dirpath
                )
                for excluded_dir in excluded_dirs
            ):
                continue

            for filename in filenames:
                full_path = os.path.join(dirpath, filename)  # noqa: PTH118
                if any(re.match(regex, full_path) for regex in include_regex) and not any(
                    re.match(regex, full_path) for regex in exclude_regex
                ):
                    relative_path = full_path.replace(self.root, "").lstrip("/")
                    yield relative_path


class DirectoryContentResolver(ContentResolver):
    root: str

    def __init__(self, root: str) -> None:
        self.root = os.path.realpath(root)

    def file_contents_by_location(
        self,
        location: Location,
        *,
        function_reader: FileReader | None = None,
        mode: str = "r",
    ) -> TextIO | None:
        if not location.coordinates:
            return None

        location_path = Path(location.coordinates.real_path)

        if location_path.exists():
            if function_reader:
                return function_reader(location.coordinates.real_path, encoding="utf-8", mode=mode)

            return cast("TextIO", location_path.open(encoding="utf-8", mode=mode))

        return None


class DirectoryMetadataResolver(MetadataResolver):
    root: str

    def __init__(self, root: str) -> None:
        self.root = os.path.realpath(root)

    def file_metadata_by_location(self, location: Location) -> Metadata | None:
        link_destination = None
        if not location.access_path:
            return None

        stats = Path(location.access_path).stat()

        if Path(location.access_path).is_symlink():
            file_type = Type.TYPE_SYM_LINK
            link_destination = str(Path(location.access_path).readlink())
        elif Path(location.access_path).is_dir():
            file_type = Type.TYPE_DIRECTORY
        elif Path(location.access_path).is_file():
            file_type = Type.TYPE_REGULAR
        else:
            file_type = Type.TYPE_IRREGULAR

        return Metadata(
            path=location.access_path,
            link_destination=link_destination or "",
            user_id=stats.st_uid,
            group_id=stats.st_gid,
            type=file_type,
            mime_type="text/plain",
        )


class Directory(Resolver):
    root: str
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    _path_resolver: DirectoryPathResolver
    _content_resolver: DirectoryContentResolver
    _metadata_resolver: DirectoryMetadataResolver

    def __init__(
        self,
        root: str = "./",
        include: tuple[str, ...] = (".",),
        exclude: tuple[str, ...] = (),
    ) -> None:
        self.root = os.path.realpath(root)
        self.include = include
        self.exclude = exclude
        self._path_resolver = DirectoryPathResolver(root=root, include=include, exclude=exclude)
        self._content_resolver = DirectoryContentResolver(root=root)
        self._metadata_resolver = DirectoryMetadataResolver(root=root)

    def has_path(self, path: str) -> bool:
        return self._path_resolver.has_path(path)

    def files_by_path(self, *paths: str) -> list[Location]:
        return self._path_resolver.files_by_path(*paths)

    def files_by_glob(self, *patters: str) -> list[Location]:
        return self._path_resolver.files_by_glob(*patters)

    def file_contents_by_location(
        self,
        location: Location,
        *,
        function_reader: FileReader | None = None,
        mode: str = "r",
    ) -> TextIO | None:
        return self._content_resolver.file_contents_by_location(
            location,
            function_reader=function_reader,
            mode=mode,
        )

    def file_metadata_by_location(self, location: Location) -> Metadata | None:
        return self._metadata_resolver.file_metadata_by_location(location)

    def relative_file_path(self, loc: Location, path: str) -> Location:
        return self._path_resolver.relative_file_path(loc, path)

    def walk_file(self) -> Generator[str, None, None]:
        yield from self._path_resolver.walk_file()
