from enum import Enum, StrEnum
from io import TextIOWrapper
from typing import TextIO

from pydantic import BaseModel, ConfigDict


class DependencyType(StrEnum):
    DIRECT = "DIRECT"
    TRANSITIVE = "TRANSITIVE"
    UNDETERMINABLE = "UNDETERMINABLE"


class Scope(StrEnum):
    BUILD = "BUILD"
    RUN = "RUN"
    UNDETERMINABLE = "UNDETERMINABLE"


class Type(Enum):
    TYPE_REGULAR = "TypeRegular"
    TYPE_HARD_LINK = "TypeHardLink"
    TYPE_SYM_LINK = "TypeSymLink"
    TYPE_CHARACTER_DEVICE = "TypeCharacterDevice"
    TYPE_BLOCK_DEVICE = "TypeBlockDevice"
    TYPE_DIRECTORY = "TypeDirectory"
    TYPE_FIFO = "TypeFIFO"
    TYPE_SOCKET = "TypeSocket"
    TYPE_IRREGULAR = "TypeIrregular"


class Metadata(BaseModel):
    path: str
    link_destination: str
    user_id: int
    group_id: int
    type: Type
    mime_type: str


class Coordinates(BaseModel):
    real_path: str
    file_system_id: str | None = None
    line: int | None = None

    def __str__(self) -> str:
        result = f"RealPath={self.real_path}"
        if self.file_system_id:
            result += f" Layer={self.file_system_id}"
        return f"Location<{result}>"


class LocationMetadata(BaseModel):
    annotations: dict[str, str]

    def merge(self, other: "LocationMetadata") -> "LocationMetadata":
        return LocationMetadata(annotations={**self.annotations, **other.annotations})


class LocationData(BaseModel):
    coordinates: Coordinates
    access_path: str

    def __hash__(self) -> int:
        return hash((self.access_path, self.coordinates.file_system_id))


class Location(BaseModel):
    scope: Scope = Scope.UNDETERMINABLE
    coordinates: Coordinates | None = None
    access_path: str | None = None
    annotations: dict[str, str] | None = None
    dependency_type: DependencyType = DependencyType.UNDETERMINABLE
    reachable_cves: list[str] = []

    def path(self) -> str:
        path = self.access_path or (self.coordinates.real_path if self.coordinates else None)
        if not path:
            error_msg = "Both access_path and coordinates.real_path are empty"
            raise ValueError(error_msg)
        return path.strip().replace(" ", "_")


class LocationReadCloser(BaseModel):
    location: Location
    read_closer: TextIO | TextIOWrapper
    model_config = ConfigDict(arbitrary_types_allowed=True)
