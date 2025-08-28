"""Engine idle timeout command."""

import re
import time
from typing import Optional

import boto3
import typer

from ..engine_studio_utils.api_utils import make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console
from ..engine_studio_utils.formatting import resolve_engine


def idle_timeout_cmd(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    set: Optional[str] = typer.Option(
        None, "--set", "-s", help="New timeout (e.g., 2h30m, 45m)"
    ),
    slack: Optional[str] = typer.Option(
        None, "--slack", help="Set Slack notifications: none, default, all"
    ),
):
    """Show or set engine idle-detector settings."""
    check_aws_sso()

    # Resolve engine
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    ssm = boto3.client("ssm", region_name="us-east-1")

    # Handle slack notifications change
    if slack:
        slack = slack.lower()
        if slack not in ["none", "default", "all"]:
            console.print("[red]❌ Invalid slack option. Use: none, default, all[/red]")
            raise typer.Exit(1)

        console.print(f"Setting Slack notifications to [bold]{slack}[/bold]...")

        if slack == "none":
            settings = {
                "SLACK_NOTIFY_WARNINGS": "false",
                "SLACK_NOTIFY_IDLE_START": "false",
                "SLACK_NOTIFY_IDLE_END": "false",
                "SLACK_NOTIFY_SHUTDOWN": "false",
            }
        elif slack == "default":
            settings = {
                "SLACK_NOTIFY_WARNINGS": "true",
                "SLACK_NOTIFY_IDLE_START": "false",
                "SLACK_NOTIFY_IDLE_END": "false",
                "SLACK_NOTIFY_SHUTDOWN": "true",
            }
        else:  # all
            settings = {
                "SLACK_NOTIFY_WARNINGS": "true",
                "SLACK_NOTIFY_IDLE_START": "true",
                "SLACK_NOTIFY_IDLE_END": "true",
                "SLACK_NOTIFY_SHUTDOWN": "true",
            }

        commands = []
        for key, value in settings.items():
            # Use a robust sed command that adds the line if it doesn't exist
            commands.append(
                f"grep -q '^{key}=' /etc/engine.env && sudo sed -i 's|^{key}=.*|{key}={value}|' /etc/engine.env || echo '{key}={value}' | sudo tee -a /etc/engine.env > /dev/null"
            )

        # Instead of restarting service, send SIGHUP to reload config
        commands.append(
            "sudo pkill -HUP -f engine-idle-detector.py || sudo systemctl restart engine-idle-detector.service"
        )

        resp = ssm.send_command(
            InstanceIds=[engine["instance_id"]],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": commands, "executionTimeout": ["60"]},
        )
        cid = resp["Command"]["CommandId"]
        time.sleep(2)  # Give it a moment to process
        console.print(f"[green]✓ Slack notifications updated to '{slack}'[/green]")
        console.print("[dim]Note: Settings updated without resetting idle timer[/dim]")

    # Handle setting new timeout value
    if set is not None:
        m = re.match(r"^(?:(\d+)h)?(?:(\d+)m)?$", set)
        if not m:
            console.print(
                "[red]❌ Invalid duration format. Use e.g. 2h, 45m, 1h30m[/red]"
            )
            raise typer.Exit(1)
        hours = int(m.group(1) or 0)
        minutes = int(m.group(2) or 0)
        seconds = hours * 3600 + minutes * 60
        if seconds == 0:
            console.print("[red]❌ Duration must be greater than zero[/red]")
            raise typer.Exit(1)

        console.print(f"Setting idle timeout to {set} ({seconds} seconds)…")

        cmd = (
            "sudo sed -i '/^IDLE_TIMEOUT_SECONDS=/d' /etc/engine.env && "
            f"echo 'IDLE_TIMEOUT_SECONDS={seconds}' | sudo tee -a /etc/engine.env >/dev/null && "
            "sudo systemctl restart engine-idle-detector.service"
        )

        resp = ssm.send_command(
            InstanceIds=[engine["instance_id"]],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": [cmd], "executionTimeout": ["60"]},
        )
        cid = resp["Command"]["CommandId"]
        time.sleep(2)
        console.print(f"[green]✓ Idle timeout updated to {set}[/green]")

    # If no action was specified, show current timeout
    if set is None and slack is None:
        # Show current timeout setting
        resp = ssm.send_command(
            InstanceIds=[engine["instance_id"]],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": [
                    "grep -E '^IDLE_TIMEOUT_SECONDS=' /etc/engine.env || echo 'IDLE_TIMEOUT_SECONDS=1800'"
                ],
                "executionTimeout": ["10"],
            },
        )
        cid = resp["Command"]["CommandId"]
        time.sleep(1)
        inv = ssm.get_command_invocation(
            CommandId=cid, InstanceId=engine["instance_id"]
        )
        if inv["Status"] == "Success":
            line = inv["StandardOutputContent"].strip()
            secs = int(line.split("=")[1]) if "=" in line else 1800
            console.print(f"Current idle timeout: {secs//60}m ({secs} seconds)")
        else:
            console.print("[red]❌ Could not retrieve idle timeout[/red]")
        return
