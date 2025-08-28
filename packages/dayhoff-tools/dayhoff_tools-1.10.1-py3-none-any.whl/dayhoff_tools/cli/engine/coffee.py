"""Engine coffee command."""

import re
import time

import boto3
import typer
from botocore.exceptions import ClientError

from ..engine_studio_utils.api_utils import make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console
from ..engine_studio_utils.formatting import resolve_engine


def coffee(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    duration: str = typer.Argument("4h", help="Duration (e.g., 2h, 30m, 2h30m)"),
    cancel: bool = typer.Option(
        False, "--cancel", help="Cancel existing coffee lock instead of extending"
    ),
):
    """Pour ☕ for an engine: keeps it awake for the given duration (or cancel)."""
    username = check_aws_sso()

    # Parse duration
    if not cancel:
        match = re.match(r"(?:(\d+)h)?(?:(\d+)m)?", duration)
        if not match or (not match.group(1) and not match.group(2)):
            console.print(f"[red]❌ Invalid duration format: {duration}[/red]")
            console.print("Use format like: 4h, 30m, 2h30m")
            raise typer.Exit(1)

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds_total = (hours * 60 + minutes) * 60
        if seconds_total == 0:
            console.print("[red]❌ Duration must be greater than zero[/red]")
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

    if cancel:
        console.print(f"Cancelling coffee for [cyan]{engine['name']}[/cyan]…")
    else:
        console.print(
            f"Pouring coffee for [cyan]{engine['name']}[/cyan] for {duration}…"
        )

    # Use SSM to run the engine coffee command
    ssm = boto3.client("ssm", region_name="us-east-1")
    try:
        response = ssm.send_command(
            InstanceIds=[engine["instance_id"]],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": [
                    (
                        "/usr/local/bin/engine-coffee --cancel"
                        if cancel
                        else f"/usr/local/bin/engine-coffee {seconds_total}"
                    )
                ],
                "executionTimeout": ["60"],
            },
        )

        command_id = response["Command"]["CommandId"]

        # Wait for command to complete
        for _ in range(10):
            time.sleep(1)
            result = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=engine["instance_id"],
            )
            if result["Status"] in ["Success", "Failed"]:
                break

        if result["Status"] == "Success":
            if cancel:
                console.print(
                    "[green]✓ Coffee cancelled – auto-shutdown re-enabled[/green]"
                )
            else:
                console.print(f"[green]✓ Coffee poured for {duration}[/green]")
            console.print(
                "\n[dim]Note: Detached Docker containers (except dev containers) will also keep the engine awake.[/dim]"
            )
            console.print(
                "[dim]Use coffee for nohup operations or other background tasks.[/dim]"
            )
        else:
            console.print(
                f"[red]❌ Failed to manage coffee: {result.get('StatusDetails', 'Unknown error')}[/red]"
            )

    except ClientError as e:
        console.print(f"[red]❌ Failed to manage coffee: {e}[/red]")
