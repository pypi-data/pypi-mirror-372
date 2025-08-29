import logging
import textwrap
from typing import Unpack

import click

from labels.core.configurator import build_labels_config_from_args, build_labels_config_from_file
from labels.core.scanner import execute_labels_scan
from labels.model.core import ScanArgs

LOGGER = logging.getLogger(__name__)


def show_fluid_attacks_banner() -> None:
    logo = textwrap.dedent(
        """
         ───── ⌝
        |    ⌝|  Fluid Attacks
        |  ⌝  |  We hack your software.
         ─────
        """,
    )
    click.secho(logo, fg="red")


@click.group(help="Fluid labels CLI")
def cli() -> None:
    """Entry point for the command-line interface (CLI) of the application.

    This function serves as the main entry point for the CLI, grouping
    all the available commands under a single interface.

    Available commands:
    - config: Load and process a configuration file.
    - scan: Perform a scan based on the provided arguments and options.
    - static-scan: Perform a scan for a full static analysis (SCA and SAST).
    """


@click.command(
    name="config",
    short_help="Load and process a YAML configuration file.",
    epilog="Check out our docs at https://help.fluidattacks.com/portal/en/kb",
)
@click.argument(
    "config_path",
    type=click.Path(exists=True, readable=True, path_type=str),
    required=True,
    metavar="config_path",
)
def run_labels_from_config(config_path: str) -> None:
    """Execute SBOM scan from a configuration file.

    \b
    ARGUMENT:
        config_path:  Path to the YAML configuration file (.yaml or .yml).

    \b
    USAGE EXAMPLES:
        - labels config ./config.yaml   # Load and execute the SBOM scan using config.yaml
        - labels config ./config.yml    # Load and execute the SBOM scan using config.yml

    \b
    The configuration file must be in YAML format (.yaml or .yml).
    """  # noqa: D301
    show_fluid_attacks_banner()
    sbom_config = build_labels_config_from_file(config_path)
    execute_labels_scan(sbom_config)


@click.command(
    name="static_scan",
    short_help="Scan a directory for a static analysis.",
    epilog="Check out our docs at https://help.fluidattacks.com/portal/en/kb",
)
@click.argument(
    "config_path",
    type=click.Path(exists=True, readable=True, path_type=str),
    required=True,
    metavar="config_path",
)
def run_static_scanner(config_path: str) -> None:
    """Execute SBOM scan from a configuration file used for a static analysis (SCA and SAST).

    \b
    ARGUMENT:
        config_path:  Path to the YAML configuration file (.yaml or .yml).

    \b
    USAGE EXAMPLES:
        - labels config ./config.yaml   # Load and execute the SBOM scan using config.yaml

    \b
    The configuration file must be in YAML format (.yaml or .yml).
    """  # noqa: D301
    show_fluid_attacks_banner()
    sbom_config = build_labels_config_from_file(config_path, static_scan=True)
    execute_labels_scan(sbom_config)


@click.command(
    name="scan",
    short_help="Perform an SBOM scan using the specified args.",
    epilog="Check out our docs at https://help.fluidattacks.com/portal/en/kb",
)
@click.option(
    "--source",
    type=click.Choice(["docker", "dir", "docker-daemon", "ecr"], case_sensitive=False),
    required=True,
    default="dir",
    show_default=True,
    help="Specify the source of the scan: 'docker', 'dir', 'docker-daemon', or 'ecr'.",
)
@click.option(
    "--output",
    default="my_sbom",
    type=click.STRING,
    show_default=True,
    help="Output filename for the scan results.",
)
@click.option(
    "--format",
    type=click.Choice(
        ["fluid-json", "cyclonedx-json", "spdx-json", "cyclonedx-xml", "spdx-xml"],
        case_sensitive=False,
    ),
    default="fluid-json",
    help="Output format for the resulting file.",
)
@click.option(
    "--docker-user",
    default=None,
    type=click.STRING,
    help="Docker registry username, if required.",
)
@click.option(
    "--docker-password",
    default=None,
    type=click.STRING,
    help="Docker registry password, if required.",
)
@click.option(
    "--aws-external-id",
    default=None,
    type=click.STRING,
    help="AWS external ID for ECR access, if necessary.",
)
@click.option(
    "--aws-role",
    default=None,
    type=click.STRING,
    help="AWS role ARN for ECR access, if necessary.",
)
@click.option(
    "--debug",
    is_flag=True,
    default=False,
    show_default=True,
    help="Enable debug mode for detailed logging.",
)
@click.argument(
    "target",
    type=click.STRING,
    required=True,
)
def run_labels_from_args(target: str, **kwargs: Unpack[ScanArgs]) -> None:
    """Execute SBOM scan with arguments.

    \b
    ARGUMENT:
        target:  The target to scan, depending on the selected source:

    \b
    USAGE EXAMPLES:
        - labels scan my-image:latest --source docker # Scan a Docker image
        - labels scan ./my-project --source dir # Scan a local directory
        - labels scan my-image:latest --source docker-daemon # Scan a running local image
        - labels scan 1234567890.dkr.ecr.us-east-1.amazonaws.com/my-image --from ecr (To scan an ECR Image)
    """  # noqa: D301, E501
    show_fluid_attacks_banner()
    sbom_config = build_labels_config_from_args(target, **kwargs)
    execute_labels_scan(sbom_config)


cli.add_command(run_labels_from_config)
cli.add_command(run_labels_from_args)
cli.add_command(run_static_scanner)

if __name__ == "__main__":
    cli(prog_name="labels")
