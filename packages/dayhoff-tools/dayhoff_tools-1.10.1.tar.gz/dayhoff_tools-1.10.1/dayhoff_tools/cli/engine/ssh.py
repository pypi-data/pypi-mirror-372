"""Engine SSH command."""

import subprocess

import typer

from ..engine_studio_utils.api_utils import make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console
from ..engine_studio_utils.formatting import resolve_engine
from ..engine_studio_utils.ssh_utils import check_session_manager_plugin, update_ssh_config_entry


def ssh_engine(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    admin: bool = typer.Option(
        False, "--admin", help="Connect as ec2-user instead of the engine owner user"
    ),
    idle_timeout: int = typer.Option(
        600,
        "--idle-timeout",
        help="Idle timeout (seconds) for the SSM port-forward (0 = disable)",
    ),
):
    """Connect to an engine via SSH.

    By default the CLI connects using the engine's owner username (the same one stored in the `User` tag).
    Pass `--admin` to connect with the underlying [`ec2-user`] account for break-glass or debugging.
    """
    username = check_aws_sso()

    # Check for Session Manager Plugin
    if not check_session_manager_plugin():
        raise typer.Exit(1)

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    if engine["state"].lower() != "running":
        console.print(f"[red]❌ Engine is not running (state: {engine['state']})[/red]")
        raise typer.Exit(1)

    # Choose SSH user
    ssh_user = "ec2-user" if admin else username

    # Update SSH config
    console.print(
        f"Updating SSH config for [cyan]{engine['name']}[/cyan] (user: {ssh_user})..."
    )
    update_ssh_config_entry(
        engine["name"], engine["instance_id"], ssh_user, idle_timeout
    )

    # Connect
    console.print(f"[green]✓ Connecting to {engine['name']}...[/green]")
    subprocess.run(["ssh", engine["name"]])
