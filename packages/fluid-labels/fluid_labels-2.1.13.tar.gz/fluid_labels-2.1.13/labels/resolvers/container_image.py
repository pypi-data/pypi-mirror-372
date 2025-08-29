import glob
import os
import tarfile
from collections.abc import Generator
from pathlib import Path
from typing import TextIO, cast

from labels.model.file import Location, Metadata, Type
from labels.model.resolver import ContentResolver, FileReader, PathResolver, Resolver
from labels.model.sources import ImageContext, ImageMetadata
from labels.utils.file import new_location_from_image


def is_in_dependency_dir(path: str, dependency_dirs: set[str]) -> bool:
    for dep in dependency_dirs:
        dep_norm = dep if dep.endswith(os.path.sep) else dep + os.path.sep
        if path.startswith(dep_norm):
            return "node_modules" in path
    return False


def _normalize_rel_root(root: str, base_path: str) -> str:
    rel_root = os.path.relpath(root, base_path)
    return os.path.sep if rel_root == "." else str(Path(os.path.sep, rel_root))


def get_type_from_tar_member(member: tarfile.TarInfo) -> Type:
    type_map = {
        member.issym: Type.TYPE_SYM_LINK,
        member.islnk: Type.TYPE_HARD_LINK,
        member.isreg: Type.TYPE_REGULAR,
        member.isdir: Type.TYPE_DIRECTORY,
        member.isfifo: Type.TYPE_FIFO,
        member.ischr: Type.TYPE_CHARACTER_DEVICE,
        member.isblk: Type.TYPE_BLOCK_DEVICE,
    }

    for check_func, type_value in type_map.items():
        if check_func():
            return type_value

    return Type.TYPE_IRREGULAR


class ContainerImagePathResolver(PathResolver):
    def __init__(self, *, img: ImageMetadata, context: ImageContext) -> None:
        self.img = img
        self.context = context

    def _has_path(self, path: str) -> bool:
        layer_ids = [x["digest"] for x in self.context.manifest["layers"]]

        success = []
        path = path.lstrip(os.path.sep)
        for layer_id in layer_ids:
            p_file_path = Path(self.context.full_extraction_dir).joinpath(layer_id, path)
            if p_file_path.exists():
                success.append(True)
                break

        return any(success)

    def has_path(self, path: str) -> bool:
        return self._has_path(path)

    def _search_path(self, path: str) -> list[Location]:
        locations: list[Location] = []
        layer_ids = [x["digest"] for x in self.context.manifest["layers"]]

        for layer_id in layer_ids:
            p_file_path = Path(self.context.full_extraction_dir).joinpath(
                layer_id,
                path.lstrip(os.path.sep),
            )
            if p_file_path.exists():
                locations.append(new_location_from_image(path, layer_id, str(p_file_path)))
        return locations

    def files_by_path(self, *paths: str) -> list[Location]:
        locations: list[Location] = []

        for path in paths:
            if find_path := self._search_path(path.lstrip("/")):
                locations.extend(find_path)
            else:
                locations.extend(self._search_path(path))
        return locations

    def files_by_glob(self, *patterns: str) -> list[Location]:
        locations: list[Location] = []
        for layer_info in self.context.manifest["layers"]:
            layer_digest = layer_info["digest"]
            layer_extract_dir = Path(self.context.full_extraction_dir, layer_digest)

            for pattern in patterns:
                full_pattern = os.path.join(layer_extract_dir, pattern)  # noqa: PTH118
                locations.extend(
                    new_location_from_image(
                        os.path.relpath(file_path, layer_extract_dir),
                        layer_digest,
                        file_path,
                    )
                    for file_path in glob.glob(full_pattern, recursive=True)  # noqa: PTH207
                )
        return locations

    def relative_file_path(self, _: Location, _path: str) -> Location | None:  # Review
        files = self.files_by_path(_path)
        if not files:
            return None
        return files[0]

    def _walk_layer(
        self,
        current_layer_path: str,
        global_dependency_dirs: set[str],
    ) -> Generator[str, None, None]:
        dependency_files = {"package.json", "package-lock.json", "yarn.lock"}
        for root, dirs, files in os.walk(current_layer_path):
            rel_root = _normalize_rel_root(root, current_layer_path)
            if is_in_dependency_dir(rel_root, global_dependency_dirs):
                continue
            if any(dep in files for dep in dependency_files):
                global_dependency_dirs.add(rel_root)
                if "node_modules" in dirs:
                    dirs.remove("node_modules")

            for file in files:
                yield os.path.join(rel_root, file)  # noqa: PTH118

    def walk_file(self) -> Generator[str, None, None]:
        layer_ids = [x["digest"] for x in self.context.manifest["layers"]]
        global_dependency_dirs: set[str] = set()

        for layer_id in layer_ids:
            current_layer_path = Path(self.context.full_extraction_dir, layer_id)
            yield from self._walk_layer(str(current_layer_path), global_dependency_dirs)


class ContainerImageContentResolver(ContentResolver):
    def __init__(self, *, img: ImageMetadata, context: ImageContext) -> None:
        self.img = img
        self.context = context

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


class ContainerImage(Resolver):
    img: ImageMetadata
    context: ImageContext
    _path_resolver: ContainerImagePathResolver
    _content_resolver: ContainerImageContentResolver

    def __init__(self, *, img: ImageMetadata, context: ImageContext) -> None:
        self.img = img
        self.context = context
        self._path_resolver = ContainerImagePathResolver(img=self.img, context=self.context)
        self._content_resolver = ContainerImageContentResolver(img=self.img, context=self.context)

    def has_path(self, path: str) -> bool:
        return self._path_resolver.has_path(path)

    def files_by_path(self, *paths: str) -> list[Location]:
        return self._path_resolver.files_by_path(*paths)

    def files_by_glob(self, *patterns: str) -> list[Location]:
        return self._path_resolver.files_by_glob(*patterns)

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

    def file_metadata_by_location(self, _location: Location) -> Metadata | None:
        raise NotImplementedError

    def relative_file_path(self, loc: Location, path: str) -> Location | None:
        return self._path_resolver.relative_file_path(loc, path)

    def walk_file(self) -> Generator[str, None, None]:
        yield from self._path_resolver.walk_file()
