import re

from labels.model.package import PackageType


def format_exception(exc: str) -> str:
    return re.sub(r"^\s*For further information.*(?:\n|$)", "", exc, flags=re.MULTILINE)


def normalize_python_package_name(name: str) -> str:
    """Normalize a package name according to PEP 503."""
    return re.sub(r"[-_.]+", "-", name)


def normalize_name(name: str, package_type: PackageType) -> str:
    name_str = name

    if package_type in (PackageType.GithubActionPkg, PackageType.PythonPkg, PackageType.DotnetPkg):
        name_str = name_str.lower()
    if package_type == PackageType.PythonPkg:
        name_str = normalize_python_package_name(name_str)

    return name_str
