import logging
from typing import Any

import phpserialize
from pydantic import ValidationError

from labels.model.file import LocationReadCloser
from labels.model.package import Language, Package, PackageType
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.php.package import package_url_from_pecl
from labels.parsers.cataloger.utils import get_enriched_location, log_malformed_package_warning

LOGGER = logging.getLogger(__name__)


def php_to_python(obj: Any) -> Any:  # noqa: ANN401
    if isinstance(obj, phpserialize.phpobject):
        return {k: php_to_python(v) for k, v in obj.__php_vars__.items()}
    if isinstance(obj, dict):
        return {php_to_python(k): php_to_python(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [php_to_python(i) for i in obj]

    return obj


def parse_pecl_serialized(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    relationships: list[Relationship] = []

    unserialized_data = phpserialize.loads(reader.read_closer.read().encode(), decode_strings=True)
    parsed_data = php_to_python(unserialized_data)
    name = parsed_data.get("name")
    version = parsed_data.get("version", {}).get("release")

    if not name or not version:
        return [], []

    new_location = get_enriched_location(reader.location)

    try:
        packages.append(
            Package(
                name=name,
                version=version,
                locations=[new_location],
                language=Language.PHP,
                licenses=[],
                type=PackageType.PhpPeclPkg,
                metadata=None,
                p_url=package_url_from_pecl(name, version),
            ),
        )
    except ValidationError as ex:
        log_malformed_package_warning(new_location, ex)
        return [], []
    else:
        return packages, relationships
