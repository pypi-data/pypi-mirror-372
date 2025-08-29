from pydantic import BaseModel, Field

from labels.model.package import Digest, Package, PackageType

JENKINS_PLUGIN_POM_PROPERTIES_GROUP_IDS = [
    "io.jenkins.plugins",
    "org.jenkins.plugins",
    "org.jenkins-ci.plugins",
    "io.jenkins-ci.plugins",
    "com.cloudbees.jenkins.plugins",
]


class PomContext(BaseModel):
    parent_info: dict[str, str] | None
    parent_version_properties: dict[str, str] | None
    manage_deps: dict[str, str] | None


class JavaPomParent(BaseModel):
    group_id: str
    artifact_id: str
    version: str


class JavaPomProject(BaseModel):
    path: str | None = None
    group_id: str | None = None
    artifact_id: str | None = None
    version: str | None = None
    name: str | None = None
    parent: JavaPomParent | None = None
    description: str | None = None
    url: str | None = None


class JavaPomProperties(BaseModel):
    name: str | None = None
    group_id: str | None = None
    artifact_id: str | None = None
    version: str | None = None
    path: str | None = None
    scope: str | None = None
    extra: dict[str, str] = Field(default_factory=dict)

    def pkg_type_indicated(self) -> PackageType:
        if any(
            self.group_id and self.group_id.startswith(prefix)
            for prefix in JENKINS_PLUGIN_POM_PROPERTIES_GROUP_IDS
        ) or (self.group_id and ".jenkins.plugin" in self.group_id):
            return PackageType.JenkinsPluginPkg
        return PackageType.JavaPkg


class JavaManifest(BaseModel):
    main: dict[str, str]
    sections: list[dict[str, str]] | None = None


class JavaArchive(BaseModel):
    virtual_path: str | None = None
    manifest: JavaManifest | None = None
    pom_properties: JavaPomProperties | None = None
    pom_project: JavaPomProject | None = None
    archive_digests: list[Digest] = Field(default_factory=list)
    parent: Package | None = None
