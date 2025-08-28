"""Engine config-ssh command."""

from pathlib import Path

import typer

from ..engine_studio_utils.api_utils import make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import SSH_MANAGED_COMMENT, console
from ..engine_studio_utils.ssh_utils import check_session_manager_plugin


def config_ssh(
    clean: bool = typer.Option(False, "--clean", help="Remove all managed entries"),
    all_engines: bool = typer.Option(
        False, "--all", "-a", help="Include all engines from all users"
    ),
    admin: bool = typer.Option(
        False,
        "--admin",
        help="Generate entries that use ec2-user instead of per-engine owner user",
    ),
):
    """Update SSH config with available engines."""
    username = check_aws_sso()

    # Only check for Session Manager Plugin if we're not just cleaning
    if not clean and not check_session_manager_plugin():
        raise typer.Exit(1)

    if clean:
        console.print("Removing all managed SSH entries...")
    else:
        if all_engines:
            console.print("Updating SSH config with all running engines...")
        else:
            console.print(
                f"Updating SSH config with running engines for [cyan]{username}[/cyan] and [cyan]shared[/cyan]..."
            )

    # Get all engines
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    running_engines = [e for e in engines if e["state"].lower() == "running"]

    # Filter engines based on options
    if not all_engines:
        # Show only current user's engines and shared engines
        running_engines = [
            e for e in running_engines if e["user"] == username or e["user"] == "shared"
        ]

    # Read existing config
    config_path = Path.home() / ".ssh" / "config"
    config_path.parent.mkdir(mode=0o700, exist_ok=True)

    if config_path.exists():
        content = config_path.read_text()
        lines = content.splitlines()
    else:
        content = ""
        lines = []

    # Remove old managed entries
    new_lines = []
    skip_until_next_host = False
    for line in lines:
        if SSH_MANAGED_COMMENT in line:
            skip_until_next_host = True
        elif line.strip().startswith("Host ") and skip_until_next_host:
            skip_until_next_host = False
            # Check if this is a managed host
            if SSH_MANAGED_COMMENT not in line:
                new_lines.append(line)
        elif not skip_until_next_host:
            new_lines.append(line)

    # Add new entries if not cleaning
    if not clean:
        for engine in running_engines:
            # Determine ssh user based on --admin flag
            ssh_user = "ec2-user" if admin else username
            new_lines.extend(
                [
                    "",
                    f"Host {engine['name']} {SSH_MANAGED_COMMENT}",
                    f"    HostName {engine['instance_id']}",
                    f"    User {ssh_user}",
                    f"    ProxyCommand sh -c \"AWS_SSM_IDLE_TIMEOUT=600 aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters 'portNumber=%p'\"",
                ]
            )

    # Write back
    config_path.write_text("\n".join(new_lines))
    config_path.chmod(0o600)

    if clean:
        console.print("[green]✓ Removed all managed SSH entries[/green]")
    else:
        console.print(
            f"[green]✓ Updated SSH config with {len(running_engines)} engines[/green]"
        )
        for engine in running_engines:
            user_display = (
                f"[dim]({engine['user']})[/dim]" if engine["user"] != username else ""
            )
            console.print(
                f"  • {engine['name']} → {engine['instance_id']} {user_display}"
            )
