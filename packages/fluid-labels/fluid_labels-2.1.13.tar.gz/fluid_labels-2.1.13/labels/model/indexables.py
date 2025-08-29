from collections import UserDict, UserList
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from tree_sitter import Node

KEY = TypeVar("KEY")
VALUE = TypeVar("VALUE")


class FileCoordinate(BaseModel):
    line: int
    column: int
    model_config = ConfigDict(frozen=True)


class Position(BaseModel):
    start: FileCoordinate
    end: FileCoordinate
    model_config = ConfigDict(frozen=True)


class IndexedDict(UserDict[KEY, VALUE], Generic[KEY, VALUE]):
    def __init__(self, root_node: Node | None = None) -> None:
        self.position_value_index: dict[KEY, Position] = {}
        self.position_key_index: dict[KEY, Position] = {}
        data: dict[KEY, VALUE] = {}
        if root_node:
            self.position = Position(
                start=FileCoordinate(
                    line=root_node.start_point[0] + 1,
                    column=root_node.start_point[1] + 1,
                ),
                end=FileCoordinate(
                    line=root_node.end_point[0] + 1,
                    column=root_node.end_point[1] + 1,
                ),
            )
        super().__init__(data)

    def __setitem__(  # type: ignore[override]
        self,
        key: tuple[KEY, Position | Node],
        item: tuple[VALUE, Position | Node],
    ) -> None:
        key_value, key_position = key
        value_value, value_position = item
        if isinstance(key_position, Node):
            key_position = Position(
                start=FileCoordinate(
                    line=key_position.start_point[0] + 1,
                    column=key_position.start_point[1] + 1,
                ),
                end=FileCoordinate(
                    line=key_position.end_point[0] + 1,
                    column=key_position.end_point[1] + 1,
                ),
            )
        if isinstance(value_position, Node):
            value_position = Position(
                start=FileCoordinate(
                    line=value_position.start_point[0] + 1,
                    column=value_position.start_point[1] + 1,
                ),
                end=FileCoordinate(
                    line=value_position.end_point[0] + 1,
                    column=value_position.end_point[1] + 1,
                ),
            )
        self.position_key_index[key_value] = key_position
        self.position_value_index[key_value] = value_position
        return super().__setitem__(key_value, value_value)

    def get_value_position(self, key: KEY) -> Position:
        return self.position_value_index[key]

    def get_key_position(self, key: KEY) -> Position:
        return self.position_key_index[key]


class IndexedList(UserList[VALUE], Generic[VALUE]):
    def __init__(self, node: Node | None = None) -> None:
        self.position_index: dict[int, Position] = {}
        data: list[VALUE] = []
        if node:
            self.position = Position(
                start=FileCoordinate(
                    line=node.start_point[0] + 1,
                    column=node.start_point[1] + 1,
                ),
                end=FileCoordinate(
                    line=node.end_point[0] + 1,
                    column=node.end_point[1] + 1,
                ),
            )
        super().__init__(data)

    def __setitem__(self, index: int, value: tuple[VALUE, Position]) -> None:  # type: ignore[override]
        self.position_index[index] = value[1]
        return super().__setitem__(index, value[0])

    def append(self, item: tuple[VALUE, Position | Node]) -> None:  # type: ignore[override]
        value, position = item
        if isinstance(position, Node):
            position = Position(
                start=FileCoordinate(
                    line=position.start_point[0] + 1,
                    column=position.start_point[1] + 1,
                ),
                end=FileCoordinate(
                    line=position.end_point[0] + 1,
                    column=position.end_point[1] + 1,
                ),
            )
        self.position_index[len(self.data)] = position
        return super().append(value)

    def get_position(self, index: int) -> Position:
        return self.position_index[index]


ParsedValue = (
    str
    | int
    | float
    | bool
    | None
    | Position
    | list[str]
    | IndexedDict[str, "ParsedValue"]
    | IndexedList["ParsedValue"]
)
