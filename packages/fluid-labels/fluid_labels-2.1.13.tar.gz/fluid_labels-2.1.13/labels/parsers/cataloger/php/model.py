from pydantic import (
    BaseModel,
)


class PhpComposerExternalReference(BaseModel):
    type: str | None = None
    url: str | None = None
    reference: str | None
    shasum: str | None = None


class PhpComposerAuthors(BaseModel):
    name: str
    email: str | None = None
    homepage: str | None = None


class PhpComposerLockEntry(BaseModel):
    name: str
    version: str
    source: PhpComposerExternalReference | None
    dist: PhpComposerExternalReference | None
    require: dict[str, str] | None = None
    provide: dict[str, str] | None = None
    require_dev: dict[str, str] | None = None
    suggest: dict[str, str] | None = None
    license: list[str] | None = None
    type: str | None = None
    notification_url: str | None = None
    bin: list[str] | None = None
    authors: list[PhpComposerAuthors] | None = None
    description: str | None = None
    homepage: str | None = None
    keywords: list[str] | None = None
    time: str | None = None


# PhpComposerInstalledEntry is an alias for PhpComposerLockEntry
PhpComposerInstalledEntry = PhpComposerLockEntry
