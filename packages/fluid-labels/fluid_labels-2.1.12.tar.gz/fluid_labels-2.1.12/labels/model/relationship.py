from enum import Enum

from pydantic import BaseModel, ConfigDict


class RelationshipType(Enum):
    OWNERSHIP_BY_FILE_OVERLAP_RELATIONSHIP = "ownership-by-file-overlap"
    EVIDENT_BY_RELATIONSHIP = "evident-by"
    CONTAINS_RELATIONSHIP = "contains"
    DEPENDENCY_OF_RELATIONSHIP = "dependency-of"
    DESCRIBED_BY_RELATIONSHIP = "described-by"


class Relationship(BaseModel):
    from_: str
    to_: str
    type: RelationshipType
    model_config = ConfigDict(frozen=True)
