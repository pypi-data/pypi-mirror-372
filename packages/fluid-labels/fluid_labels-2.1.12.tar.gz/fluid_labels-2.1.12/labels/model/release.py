from typing import TypedDict

from pydantic import BaseModel, ConfigDict


class OsReleaseDict(TypedDict, total=False):
    PRETTY_NAME: str
    NAME: str
    ID: str
    ID_LIKE: str
    VERSION: str
    VERSION_ID: str
    VERSION_CODENAME: str
    BUILD_ID: str
    IMAGE_ID: str
    IMAGE_VERSION: str
    VARIANT: str
    VARIANT_ID: str
    HOME_URL: str
    SUPPORT_URL: str
    BUG_REPORT_URL: str
    PRIVACY_POLICY_URL: str
    CPE_NAME: str
    SUPPORT_END: str


class Release(BaseModel):
    id_: str
    version_id: str
    name: str | None = None
    pretty_name: str | None = None
    version: str | None = None
    id_like: list[str] | None = None
    version_code_name: str | None = None
    build_id: str | None = None
    image_id: str | None = None
    image_version: str | None = None
    variant: str | None = None
    variant_id: str | None = None
    home_url: str | None = None
    support_url: str | None = None
    bug_report_url: str | None = None
    privacy_policy_url: str | None = None
    cpe_name: str | None = None
    support_end: str | None = None

    def __str__(self) -> str:
        if self.pretty_name:
            return self.pretty_name
        if self.name:
            return self.name
        if self.version:
            return f"{self.id_} {self.version}"
        if self.version_id != "":
            return f"{self.id_} {self.version_id}"
        return f"{self.id_} {self.build_id or ''}"


class Environment(BaseModel):
    linux_release: Release | None
    model_config = ConfigDict(frozen=True)
