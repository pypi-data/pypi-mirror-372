from pydantic import (
    BaseModel,
    ConfigDict,
)


class PythonFileDigest(BaseModel):
    algorithm: str
    value: str
    model_config = ConfigDict(frozen=True)


class PythonFileRecord(BaseModel):
    path: str
    digest: PythonFileDigest | None = None
    size: str | None = None
    model_config = ConfigDict(frozen=True)


class PythonDirectURLOriginInfo(BaseModel):
    url: str
    commit_id: str | None
    vcs: str | None
    model_config = ConfigDict(frozen=True)


class PythonPackage(BaseModel):
    name: str
    version: str | None = None
    author: str | None = None
    author_email: str | None = None
    platform: str | None = None
    files: list[PythonFileRecord] | None = None
    site_package_root_path: str | None = None
    top_level_packages: list[str] | None = None
    direct_url_origin: PythonDirectURLOriginInfo | None = None
    dependencies: list[str] | None = None


class PythonRequirementsEntry(BaseModel):
    name: str
    extras: list[str] | None
    markers: str | None
    version_constraint: str | None = None
    model_config = ConfigDict(frozen=True)
