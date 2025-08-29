from packageurl import PackageURL

from labels.parsers.cataloger.java.model import JavaArchive, JavaPomProject, JavaPomProperties


def looks_like_group_id(group_id: str) -> bool:
    return "." in group_id


def remove_osgi_directives(group_id: str) -> str:
    return group_id.split(";")[0]


def clean_group_id(group_id: str) -> str:
    return remove_osgi_directives(group_id).strip()


def group_id_from_pom_properties(properties: JavaPomProperties | None) -> str:
    if not properties:
        return ""
    if properties.group_id:
        return clean_group_id(properties.group_id)
    if properties.artifact_id and looks_like_group_id(properties.artifact_id):
        return clean_group_id(properties.artifact_id)
    return ""


def group_id_pom_project(project: JavaPomProject | None) -> str:
    if not project:
        return ""
    if project.group_id:
        return clean_group_id(project.group_id)
    if project.artifact_id and looks_like_group_id(project.artifact_id):
        return clean_group_id(project.artifact_id)
    if project.parent:
        if project.parent.group_id:
            return clean_group_id(project.parent.group_id)
        if looks_like_group_id(project.parent.artifact_id):
            return clean_group_id(project.parent.artifact_id)
    return ""


def group_id_from_java_metadata(_pkg_name: str, metadata: JavaArchive | None) -> str | None:
    if metadata:
        if group_id := group_id_from_pom_properties(metadata.pom_properties):
            return group_id
        if group_id := group_id_pom_project(metadata.pom_project):
            return group_id
    return None


def package_url(name: str, version: str, metadata: JavaArchive | None = None) -> str:
    group_id = name
    if (g_id := group_id_from_java_metadata(name, metadata)) and g_id:
        group_id = g_id
    return PackageURL(
        type="maven",
        namespace=group_id,
        name=name,
        version=version,
        qualifiers=None,
        subpath="",
    ).to_string()
