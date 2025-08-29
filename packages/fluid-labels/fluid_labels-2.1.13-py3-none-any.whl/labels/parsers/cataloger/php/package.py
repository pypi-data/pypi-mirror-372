import logging
from typing import cast

from packageurl import PackageURL
from pydantic import ValidationError

from labels.model.file import Location
from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.model.package import Language, Package, PackageType
from labels.parsers.cataloger.php.model import (
    PhpComposerAuthors,
    PhpComposerExternalReference,
    PhpComposerInstalledEntry,
)
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning

LOGGER = logging.getLogger(__name__)

EMPTY_LIST: IndexedList[str] = IndexedList()


def package_url(name: str, version: str) -> str:
    if not name:
        error_msg = "Package name cannot be empty"
        raise ValueError(error_msg)

    fields = name.split("/")

    vendor = ""
    if len(fields) == 1:
        name = fields[0]
    else:
        vendor = fields[0]
        name = "-".join(fields[1:])

    return PackageURL(  # type: ignore[misc]
        type="composer",
        namespace=vendor,
        name=name,
        version=version,
        qualifiers=None,
        subpath="",
    ).to_string()


def new_package_from_composer(
    package: IndexedDict[str, ParsedValue],
    location: Location,
    *,
    is_dev: bool = False,
) -> Package | None:
    empty_list_dict: IndexedList[IndexedDict[str, str]] = IndexedList()

    try:
        source = cast("IndexedDict[str, str]", package.get("source"))
        dist = cast("IndexedDict[str, str]", package.get("dist"))
        name = cast("str", package.get("name"))
        version = cast("str", package.get("version"))
        if not name or not version:
            return None

        new_location = get_enriched_location(
            location,
            line=package.get_key_position("name").start.line,
            is_dev=is_dev,
            is_transitive=False,
        )

        return Package(
            name=name,
            version=version,
            locations=[new_location],
            language=Language.PHP,
            licenses=list(cast("IndexedList[str]", package.get("license", EMPTY_LIST))),
            type=PackageType.PhpComposerPkg,
            p_url=package_url(name, version),
            metadata=PhpComposerInstalledEntry(
                name=name,
                version=version,
                source=PhpComposerExternalReference(
                    type=source.get("type") or None,
                    url=source.get("url") or None,
                    reference=source.get("reference") or None,
                    shasum=source.get("shasum") or None,
                )
                if source
                else None,
                dist=PhpComposerExternalReference(
                    type=dist.get("type") or None,
                    url=dist.get("url") or None,
                    reference=dist.get("reference") or None,
                    shasum=dist.get("shasum") or None,
                )
                if dist
                else None,
                require=cast("dict[str, str]", package.get("require"))
                if isinstance(package.get("require"), IndexedDict)
                else None,
                provide=cast("dict[str, str]", package.get("provide"))
                if isinstance(package.get("provide"), IndexedDict)
                else None,
                require_dev=cast("dict[str, str]", package.get("require-dev"))
                if isinstance(package.get("require-dev"), IndexedDict)
                else None,
                suggest=cast("dict[str, str]", package.get("suggest"))
                if isinstance(package.get("suggest"), IndexedDict)
                else None,
                license=cast("list[str]", package.get("license"))
                if isinstance(package.get("license"), IndexedList)
                else None,
                type=cast("str", package.get("type"))
                if isinstance(package.get("type"), str)
                else None,
                notification_url=cast("str", package.get("notification-url"))
                if isinstance(package.get("notification-url"), str)
                else None,
                bin=cast("list[str]", package.get("bin"))
                if isinstance(package.get("bin"), IndexedList)
                else None,
                authors=[
                    PhpComposerAuthors(
                        name=cast("str", x.get("name")),
                        email=x.get("email"),
                        homepage=x.get("homepage"),
                    )
                    for x in cast(
                        "list[IndexedDict[str, str]]",
                        package.get("authors", empty_list_dict),
                    )
                ],
                description=cast("str", package.get("description"))
                if isinstance(package.get("description"), str)
                else None,
                homepage=cast("str", package.get("homepage"))
                if isinstance(package.get("homepage"), str)
                else None,
                keywords=cast("list[str]", package.get("keywords")),
                time=cast("str", package.get("time"))
                if isinstance(package.get("time"), str)
                else None,
            ),
            is_dev=is_dev,
        )
    except ValidationError as ex:
        log_malformed_package_warning(new_location, ex)
        return None


def package_url_from_pecl(pkg_name: str, version: str) -> str:
    return PackageURL(  # type: ignore[misc]
        type="pecl",
        namespace="",
        name=pkg_name,
        version=version,
        qualifiers=None,
        subpath="",
    ).to_string()
