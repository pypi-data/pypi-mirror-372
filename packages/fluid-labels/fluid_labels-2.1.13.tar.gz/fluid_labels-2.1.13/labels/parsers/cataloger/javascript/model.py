from pydantic import (
    BaseModel,
)

from labels.model.package import (
    Digest,
)


class NpmPackage(BaseModel):
    name: str
    version: str | None = None
    author: str | None = None
    homepage: str | None = None
    description: str | None = None
    url: str | None = None
    private: bool | None = None
    is_dev: bool = False


class NpmPackageLockEntry(BaseModel):
    resolved: str | None = None
    integrity: str | None = None
    is_dev: bool = False


class YarnLockEntry(BaseModel):
    resolved: str | None = None
    integrity: str | None = None


class PnpmEntry(BaseModel):
    is_dev: bool = False
    integrity: Digest | None = None
