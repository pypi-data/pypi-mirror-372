from typing import cast

from spdx_matcher import analyse_license_text

LICENSES_FILE_NAMES = [
    "AL2.0",
    "COPYING",
    "COPYING.md",
    "COPYING.markdown",
    "COPYING.txt",
    "LGPL2.1",
    "LICENCE",
    "LICENCE.md",
    "LICENCE.markdown",
    "licence.txt",
    "LICENCE.txt",
    "LICENSE",
    "LICENSE.md",
    "LICENSE.markdown",
    "LICENSE.txt",
    "LICENSE-2.0.txt",
    "LICENCE-2.0.txt",
    "LICENSE-APACHE",
    "LICENCE-APACHE",
    "LICENSE-APACHE-2.0.txt",
    "LICENCE-APACHE-2.0.txt",
    "LICENSE-MIT",
    "LICENCE-MIT",
    "LICENSE.MIT",
    "LICENCE.MIT",
    "LICENSE.code",
    "LICENCE.code",
    "LICENSE.docs",
    "LICENCE.docs",
    "LICENSE.rst",
    "LICENCE.rst",
    "MIT-LICENSE",
    "MIT-LICENCE",
    "MIT-LICENSE.md",
    "MIT-LICENCE.md",
    "MIT-LICENSE.markdown",
    "MIT-LICENCE.markdown",
    "MIT-LICENSE.txt",
    "MIT-LICENCE.txt",
    "MIT_LICENSE",
    "MIT_LICENCE",
    "UNLICENSE",
    "UNLICENCE",
]


def parse_license(reader: str) -> list[str]:
    licenses_detected, _ = cast(
        "tuple[dict[str, dict[str, str]], float]",
        analyse_license_text(reader),
    )
    return list(licenses_detected["licenses"].keys())
