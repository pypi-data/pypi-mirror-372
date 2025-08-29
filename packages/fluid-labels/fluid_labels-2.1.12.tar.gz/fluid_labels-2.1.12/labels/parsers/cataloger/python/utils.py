from packageurl import PackageURL

from labels.parsers.cataloger.python.model import PythonPackage


def package_url(name: str, version: str, package: PythonPackage | None) -> str:
    return PackageURL(
        type="pypi",
        namespace="",
        name=name,
        version=version,
        qualifiers=_purl_qualifiers_for_package(package),
        subpath="",
    ).to_string()


def _purl_qualifiers_for_package(
    package: PythonPackage | None,
) -> dict[str, str]:
    if not package:
        return {}
    if (
        hasattr(package, "direct_url_origin")
        and package.direct_url_origin
        and package.direct_url_origin.vcs
    ):
        url = package.direct_url_origin
        return {"vcs_url": f"{url.vcs}+{url.url}@{url.commit_id}"}
    return {}
