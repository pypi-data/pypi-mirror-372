from packageurl import PackageURL


def package_url(name: str, version: str) -> str:
    return PackageURL(  # type: ignore[misc]
        type="hex",
        namespace="",
        name=name,
        version=version,
        qualifiers=None,
        subpath="",
    ).to_string()
