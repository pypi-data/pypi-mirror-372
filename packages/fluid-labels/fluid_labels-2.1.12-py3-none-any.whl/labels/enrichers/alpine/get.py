from labels.enrichers.api_interface import make_get


def normalize_architecture(arch: str | None) -> str | None:
    if not arch:
        return None

    arch_mapping = {
        "x86": "x86",
        "x86_64": "x86_64",
        "amd64": "x86_64",
        "i386": "x86",
        "i686": "x86",
        "arm": "arm",
        "armhf": "arm",
        "armv7": "arm",
        "arm64": "aarch64",
        "aarch64": "aarch64",
        "ppc64le": "ppc64le",
        "s390x": "s390x",
    }

    return arch_mapping.get(arch.lower(), arch)


def format_distro_version(version: str | None) -> str:
    if not version:
        return "edge"

    parts = version.split(".")
    if len(parts) == 3:
        return f"v{parts[0]}.{parts[1]}"

    return version


def get_package_versions_html(
    name: str,
    distro_version: str | None = None,
    arch: str | None = None,
) -> str | None:
    normalized_arch = normalize_architecture(arch)
    if normalized_arch is None:
        return None

    branch = format_distro_version(distro_version)

    return make_get(
        "https://pkgs.alpinelinux.org/packages",
        params={
            "name": name,
            "branch": branch,
            "repo": "",
            "arch": normalized_arch,
            "maintainer": "",
        },
        content=True,
    )
