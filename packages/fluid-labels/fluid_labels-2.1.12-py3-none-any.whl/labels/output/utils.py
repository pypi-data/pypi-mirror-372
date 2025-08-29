import re
import uuid
from pathlib import Path
from urllib.parse import urlunparse

from labels.model.advisories import Advisory
from labels.model.core import SbomConfig, SourceType
from labels.model.package import HealthMetadata, Language, Package, PackageType
from labels.model.relationship import Relationship, RelationshipType
from labels.model.resolver import Resolver
from labels.resolvers.container_image import ContainerImage
from labels.resolvers.directory import Directory


def is_valid_email(email: str) -> bool:
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None


def get_author_info(
    health_metadata: HealthMetadata,
) -> list[tuple[str | None, str | None]]:
    author_info = []

    if health_metadata.authors:
        authors_list = health_metadata.authors.split(", ")
        for author in authors_list:
            name: str | None = None
            email: str | None = None
            email_match = re.search(r"<([^<>]+)>", author)

            if email_match:
                email_candidate: str = email_match.group(1)
                email = email_candidate if is_valid_email(email_candidate) else None
                name = author.replace(email_match.group(0), "").strip() or None
            else:
                name = author.strip() or None

            author_info.append((name, email))

    return author_info


def sanitize_name(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9.-]", "-", text)


def get_document_namespace(working_dir: str) -> str:
    input_type = "unknown-source-type"
    path_working_dir = Path(working_dir)

    if path_working_dir.is_file():
        input_type = "file"
    elif path_working_dir.is_dir():
        input_type = "dir"

    unique_id = uuid.uuid4()
    identifier = Path(input_type, str(unique_id))
    if working_dir != ".":
        identifier = Path(input_type, f"{working_dir}-{unique_id}")

    return urlunparse(
        ("https", "fluidattacks.com", str(identifier), "", "", ""),
    )


def get_relative_path(absolute_path: str) -> str:
    root_path = Path(absolute_path)
    current_dir = Path.cwd()
    try:
        return str(root_path.relative_to(current_dir))
    except ValueError:
        return absolute_path


def set_namespace_version(config: SbomConfig, resolver: Resolver) -> tuple[str, str | None]:
    namespace = ""
    version = None
    if config.source_type == SourceType.DIRECTORY and isinstance(resolver, Directory):
        namespace = get_relative_path(resolver.root)
    if config.source_type in {SourceType.DOCKER, SourceType.ECR} and isinstance(
        resolver,
        ContainerImage,
    ):
        namespace = resolver.context.image_ref
        version = resolver.context.id
    return namespace, version


def create_packages_for_test() -> tuple[list[Package], list[Relationship]]:
    test_from_pkg = Package(
        name="source-package",
        version="1.0.0",
        locations=[],
        licenses=[],
        language=Language.PYTHON,
        type=PackageType.PythonPkg,
        p_url="pkg:test/source@1.0.0",
        metadata=None,
        found_by="python-pyproject-toml-cataloger",
        advisories=[
            Advisory(
                id="test-advisory",
                source="https://test-url.com",
                severity_level="HIGH",
                epss=0.75,
                percentile=8.5,
                details="Test advisory description",
                vulnerable_version=">=1.0.0",
                cpes=[],
                package_manager="github",
                severity=None,
                severity_v4=None,
            ),
        ],
    )
    test_to_pkg = Package(
        name="target-package",
        version="1.0.0",
        locations=[],
        licenses=[],
        language=Language.PYTHON,
        type=PackageType.PythonPkg,
        p_url="pkg:test/target@1.0.0",
        metadata=None,
        found_by="python-pyproject-toml-cataloger",
    )
    test_packages = [
        Package(
            name="test-package",
            version="1.0.0",
            locations=[],
            licenses=[],
            language=Language.PYTHON,
            type=PackageType.PythonPkg,
            p_url="pkg:python/test-package@1.0.0",
            metadata=None,
            found_by="python-pyproject-toml-cataloger",
        ),
        test_from_pkg,
        test_to_pkg,
    ]
    test_relationships = [
        Relationship(
            from_=test_from_pkg.id_,
            to_=test_to_pkg.id_,
            type=RelationshipType.DEPENDENCY_OF_RELATIONSHIP,
        ),
    ]
    return test_packages, test_relationships
