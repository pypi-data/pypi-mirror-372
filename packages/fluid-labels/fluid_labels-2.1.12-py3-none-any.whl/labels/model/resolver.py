import abc
from collections.abc import Generator
from typing import Protocol, TextIO, runtime_checkable

from labels.model.file import Location, Metadata


class FileReader(Protocol):  # pragma: no cover
    def __call__(self, filename: str, *, encoding: str, mode: str) -> TextIO: ...


@runtime_checkable
class ContentResolverProtocol(Protocol):  # pragma: no cover
    def file_contents_by_location(
        self,
        location: Location,
        *,
        function_reader: FileReader | None = None,
        mode: str = "r",
    ) -> TextIO | None: ...


class ContentResolver(metaclass=abc.ABCMeta):  # pragma: no cover
    @classmethod
    def __subclasshook__(cls: type["ContentResolver"], subclass: object) -> bool:
        return bool(isinstance(subclass, ContentResolverProtocol))

    @abc.abstractmethod
    def file_contents_by_location(
        self,
        location: Location,
        *,
        function_reader: FileReader | None = None,
        mode: str = "r",
    ) -> TextIO | None:
        """Resolve file context."""
        raise NotImplementedError


@runtime_checkable
class MetadataResolverProtocol(Protocol):  # pragma: no cover
    def file_metadata_by_location(
        self,
        location: Location,
    ) -> Metadata | None: ...


class MetadataResolver(metaclass=abc.ABCMeta):  # pragma: no cover
    @classmethod
    def __subclasshook__(cls: type["MetadataResolver"], subclass: object) -> bool:
        return bool(isinstance(subclass, MetadataResolverProtocol))

    @abc.abstractmethod
    def file_metadata_by_location(
        self,
        location: Location,
    ) -> Metadata | None:
        """Resolve file context."""
        raise NotImplementedError


@runtime_checkable
class PathResolverProtocol(Protocol):  # pragma: no cover
    def has_path(self, path: str) -> bool: ...

    def files_by_path(self, *paths: str) -> list[Location]: ...

    def files_by_glob(self, *patters: str) -> list[Location]: ...

    def relative_file_path(self, _: Location, path: str) -> Location | None: ...

    def walk_file(self) -> Generator[str, None, str]: ...


class PathResolver(metaclass=abc.ABCMeta):  # pragma: no cover
    @classmethod
    def __subclasshook__(cls: type["PathResolver"], subclass: object) -> bool:
        return bool(isinstance(subclass, PathResolverProtocol))

    @abc.abstractmethod
    def has_path(self, path: str) -> bool:
        """Resolve file context."""
        raise NotImplementedError

    @abc.abstractmethod
    def files_by_path(self, *paths: str) -> list[Location]:
        """Resolve file context."""
        raise NotImplementedError

    @abc.abstractmethod
    def files_by_glob(self, *patters: str) -> list[Location]:
        """Resolve file context."""
        raise NotImplementedError

    @abc.abstractmethod
    def relative_file_path(self, _: Location, path: str) -> Location | None:
        """Resolve file context."""
        raise NotImplementedError

    @abc.abstractmethod
    def walk_file(self) -> Generator[str, None, None]:
        raise NotImplementedError


class Resolver(  # pragma: no cover
    ContentResolver,
    PathResolver,
    MetadataResolver,
    metaclass=abc.ABCMeta,
):
    pass
