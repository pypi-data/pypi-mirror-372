import json
import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from labels.model.sources import ImageContext, ImageMetadata, LayerData
from labels.utils.exceptions import (
    DockerImageNotFoundError,
    InvalidImageReferenceError,
    SkopeoNotFoundError,
)
from labels.utils.file import extract_tar_file

LOGGER = logging.getLogger(__name__)


def _format_image_ref(image_ref: str, *, daemon: bool = False) -> str:
    image_ref_pattern = (
        r"^(?:(?P<host>[\w\.\-]+(?:\:\d+)?)/)?"
        r"(?P<namespace>(?:[\w\.\-]+(?:/[\w\.\-]+)*)?/)?"
        r"(?P<image>[\w\.\-]+)(?::(?P<tag>[\w\.\-]+))?(?:@"
        r"(?P<digest>sha256:[A-Fa-f0-9]{64}))?$"
    )
    prefix_to_use = "docker-daemon:" if daemon else "docker://"
    prefix_used: str | None = None
    prefixes = ["docker://", "docker-daemon:"]
    for prefix in prefixes:
        if image_ref.startswith(prefix):
            image_ref = image_ref.replace(prefix, "", 1)
            prefix_used = prefix
            break

    prefix_to_use = prefix_used or prefix_to_use

    if re.match(image_ref_pattern, image_ref):
        return f"{prefix_to_use}{image_ref}"

    raise InvalidImageReferenceError(image_ref)


def _get_skopeo_path() -> str:
    skopeo_path = shutil.which("skopeo")
    if not skopeo_path:
        raise SkopeoNotFoundError
    return skopeo_path


def _execute_command(command_args: list[str]) -> bool:
    with subprocess.Popen(  # noqa: S603
        command_args,
        shell=False,
        stdout=subprocess.PIPE,
    ) as proc:
        exit_code = proc.wait()
        return exit_code == 0


def _load_manifest(layers_dir: str) -> dict[str, Any]:
    path = Path(layers_dir, "manifest.json")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_config(config_digest: str, layers_dir: str) -> dict[str, Any]:
    path = Path(layers_dir, config_digest.replace("sha256:", ""))
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _extract_layer(layer: dict[str, Any], layers_dir: str, output_dir: str) -> None:
    layer_digest = layer["digest"].replace("sha256:", "")
    tar_path = Path(layers_dir, layer_digest)
    if tar_path.exists():
        dest = Path(output_dir, layer["digest"])
        dest.mkdir(parents=True, exist_ok=True)
        extract_tar_file(str(tar_path), str(dest))


def _build_copy_auth_args(
    *,
    unauthenticated_args: list[str],
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
) -> list[str]:
    if username and password:
        unauthenticated_args.extend(
            ["--src-username", username, "--src-password", password],
        )

    elif token:
        unauthenticated_args.extend(["--src-registry-token", token])

    elif aws_creds:
        unauthenticated_args.append(f"--src-creds={aws_creds}")

    return unauthenticated_args


def _build_inspect_auth_args(
    *,
    unauthenticated_args: list[str],
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
) -> list[str]:
    if username and password:
        unauthenticated_args.extend(["--username", username, "--password", password])

    elif token:
        unauthenticated_args.append(f"--registry-token={token}")

    elif aws_creds:
        unauthenticated_args.append(f"--creds={aws_creds}")

    return unauthenticated_args


def _custom_object_hook(json_object: dict[str, Any]) -> ImageMetadata | dict:
    if "Name" in json_object and "Digest" in json_object and "RepoTags" in json_object:
        layersdata = [
            LayerData(
                mimetype=layer_data["MIMEType"],
                digest=layer_data["Digest"],
                size=layer_data["Size"],
                annotations=layer_data.get("Annotations"),
            )
            for layer_data in json_object["LayersData"]
        ]
        return ImageMetadata(
            name=json_object["Name"],
            digest=json_object["Digest"],
            repotags=json_object["RepoTags"],
            created=json_object["Created"],
            dockerversion=json_object["DockerVersion"],
            labels=json_object["Labels"],
            architecture=json_object["Architecture"],
            os=json_object["Os"],
            layers=json_object["Layers"],
            layersdata=layersdata,
            env=json_object["Env"],
        )
    return json_object


def copy_image(  # noqa: PLR0913
    image_ref: str,
    dest_path: str,
    *,
    username: str | None = None,
    password: str | None = None,
    aws_creds: str | None = None,
    token: str | None = None,
) -> bool:
    skopeo_path = _get_skopeo_path()

    formated_image_ref = _format_image_ref(image_ref)

    command_args = [
        skopeo_path,
        "copy",
        "--dest-decompress",
        "--src-tls-verify=false",
        "--insecure-policy",
        "--override-os",
        "linux",
        formated_image_ref,
        f"dir:{dest_path}",
    ]

    authenticated_args = _build_copy_auth_args(
        unauthenticated_args=command_args,
        username=username,
        password=password,
        aws_creds=aws_creds,
        token=token,
    )

    return _execute_command(authenticated_args)


def extract_docker_image(  # noqa: PLR0913
    image: ImageMetadata,
    output_dir: str,
    *,
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
    daemon: bool = False,
) -> tuple[str, dict[str, Any]]:
    layers_dir_temp = tempfile.mkdtemp()

    formated_image_ref = _format_image_ref(image.image_ref, daemon=daemon)

    copy_image(
        image_ref=formated_image_ref or image.image_ref,
        dest_path=layers_dir_temp,
        username=username,
        password=password,
        token=token,
        aws_creds=aws_creds,
    )

    manifest = _load_manifest(layers_dir_temp)
    manifest["config_full"] = _load_config(manifest["config"]["digest"], layers_dir_temp)

    for layer in manifest["layers"]:
        _extract_layer(layer, layers_dir_temp, output_dir)

    return layers_dir_temp, manifest


def get_docker_image(  # noqa: PLR0913
    image_ref: str,
    *,
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
    daemon: bool = False,
) -> ImageMetadata:
    skopeo_path = _get_skopeo_path()

    formated_image_ref = _format_image_ref(image_ref, daemon=daemon)

    command_args = [
        skopeo_path,
        "inspect",
        "--tls-verify=false",
        "--override-os",
        "linux",
        formated_image_ref,
    ]

    authenticated_args = _build_inspect_auth_args(
        unauthenticated_args=command_args,
        username=username,
        password=password,
        aws_creds=aws_creds,
        token=token,
    )

    try:
        result = subprocess.run(  # noqa: S603
            authenticated_args,
            check=True,
            capture_output=True,
            text=True,
        )
        image_metadata: ImageMetadata = json.loads(
            result.stdout,
            object_hook=_custom_object_hook,
        )
        if image_metadata:
            image_metadata = image_metadata.model_copy(
                update={"image_ref": image_ref},
            )
    except subprocess.CalledProcessError as error:
        raise DockerImageNotFoundError(image_ref, error.stderr.strip()) from error
    else:
        return image_metadata


def get_image_context(  # noqa: PLR0913
    *,
    image: ImageMetadata,
    username: str | None = None,
    password: str | None = None,
    token: str | None = None,
    aws_creds: str | None = None,
    daemon: bool = False,
) -> ImageContext:
    temp_dir = tempfile.mkdtemp()

    layers_dir, manifest = extract_docker_image(
        image,
        temp_dir,
        username=username,
        password=password,
        token=token,
        aws_creds=aws_creds,
        daemon=daemon,
    )

    return ImageContext(
        id=image.digest,
        name=image.name,
        publisher="",
        arch=image.architecture,
        size=str(sum(x.size for x in image.layersdata)),
        full_extraction_dir=temp_dir,
        layers_dir=layers_dir,
        manifest=manifest,
        image_ref=image.image_ref,
    )
