from collections.abc import Callable

from pydantic import BaseModel, ConfigDict

from labels.model.file import Location, LocationReadCloser
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver

Parser = Callable[
    [Resolver, Environment, LocationReadCloser],
    tuple[list[Package], list[Relationship]] | None,
]


class Request(BaseModel):
    real_path: str
    parser: Parser
    parser_name: str
    model_config = ConfigDict(frozen=True)


class Task(BaseModel):
    location: Location
    parser: Parser
    parser_name: str
    model_config = ConfigDict(frozen=True)
