"""Display formatting utilities for engine and studio commands."""

import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import boto3
import typer
from rich.prompt import IntPrompt

from .constants import HOURLY_COSTS, console


def format_duration(duration: timedelta) -> str:
    """Format a duration as a human-readable string."""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def parse_launch_time(launch_time_str: str) -> datetime:
    """Parse launch time from API response."""
    # Try different datetime formats
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",  # ISO format with timezone
        "%Y-%m-%dT%H:%M:%S+00:00",  # Explicit UTC offset
        "%Y-%m-%d %H:%M:%S",
    ]

    # First try parsing with fromisoformat for better timezone handling
    try:
        # Handle the ISO format properly
        return datetime.fromisoformat(launch_time_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        pass

    # Fallback to manual format parsing
    for fmt in formats:
        try:
            parsed = datetime.strptime(launch_time_str, fmt)
            # If no timezone info, assume UTC
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            continue

    # Fallback: assume it's recent
    return datetime.now(timezone.utc)


def format_status(state: str, ready: Optional[bool]) -> str:
    """Format engine status with ready indicator."""
    if state.lower() == "running":
        if ready is True:
            return "[green]Running ✓[/green]"
        elif ready is False:
            return "[yellow]Running ⚠ (Bootstrapping...)[/yellow]"
        else:
            return "[green]Running[/green]"
    elif state.lower() == "stopped":
        return "[dim]Stopped[/dim]"
    elif state.lower() == "stopping":
        return "[yellow]Stopping...[/yellow]"
    elif state.lower() == "pending":
        return "[yellow]Starting...[/yellow]"
    else:
        return state


def resolve_engine(name_or_id: str, engines: List[Dict]) -> Dict:
    """Resolve engine by name or ID with interactive selection."""
    # Exact ID match
    exact_id = [e for e in engines if e["instance_id"] == name_or_id]
    if exact_id:
        return exact_id[0]

    # Exact name match
    exact_name = [e for e in engines if e["name"] == name_or_id]
    if len(exact_name) == 1:
        return exact_name[0]

    # Prefix matches
    matches = [
        e
        for e in engines
        if e["name"].startswith(name_or_id) or e["instance_id"].startswith(name_or_id)
    ]

    if len(matches) == 0:
        console.print(f"[red]❌ No engine found matching '{name_or_id}'[/red]")
        raise typer.Exit(1)
    elif len(matches) == 1:
        return matches[0]
    else:
        # Interactive selection
        console.print(f"Multiple engines match '{name_or_id}':")
        for i, engine in enumerate(matches, 1):
            cost = HOURLY_COSTS.get(engine["engine_type"], 0)
            console.print(
                f"  {i}. [cyan]{engine['name']}[/cyan] ({engine['instance_id']}) "
                f"- {engine['engine_type']} - {engine['state']} - ${cost:.2f}/hr"
            )

        while True:
            try:
                choice = IntPrompt.ask(
                    "Select engine",
                    default=1,
                    choices=[str(i) for i in range(1, len(matches) + 1)],
                )
                return matches[choice - 1]
            except (ValueError, IndexError):
                console.print("[red]Invalid selection, please try again[/red]")


def get_disk_usage_via_ssm(instance_id: str) -> Optional[str]:
    """Get disk usage for an engine via SSM.

    Returns:
        String like "17/50 GB" or None if failed
    """
    try:
        ssm = boto3.client("ssm", region_name="us-east-1")

        # Run df command to get disk usage
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": [
                    # Get root filesystem usage in GB
                    'df -BG / | tail -1 | awk \'{gsub(/G/, "", $2); gsub(/G/, "", $3); print $3 "/" $2 " GB"}\''
                ],
                "executionTimeout": ["10"],
            },
        )

        command_id = response["Command"]["CommandId"]

        # Wait for command to complete (with timeout)
        for _ in range(5):  # 5 second timeout
            time.sleep(1)
            result = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id,
            )
            if result["Status"] in ["Success", "Failed"]:
                break

        if result["Status"] == "Success":
            output = result["StandardOutputContent"].strip()
            return output if output else None

        return None

    except Exception as e:
        # logger.debug(f"Failed to get disk usage for {instance_id}: {e}") # Original code had this line commented out
        return None


def get_studio_disk_usage_via_ssm(instance_id: str, username: str) -> Optional[str]:
    """Get disk usage for a studio via SSM.

    Returns:
        String like "333/500 GB" or None if failed
    """
    try:
        ssm = boto3.client("ssm", region_name="us-east-1")

        # Run df command to get studio disk usage
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={
                "commands": [
                    # Get studio filesystem usage in GB
                    f'df -BG /studios/{username} 2>/dev/null | tail -1 | awk \'{{gsub(/G/, "", $2); gsub(/G/, "", $3); print $3 "/" $2 " GB"}}\''
                ],
                "executionTimeout": ["10"],
            },
        )

        command_id = response["Command"]["CommandId"]

        # Wait for command to complete (with timeout)
        for _ in range(5):  # 5 second timeout
            time.sleep(1)
            result = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id,
            )
            if result["Status"] in ["Success", "Failed"]:
                break

        if result["Status"] == "Success":
            output = result["StandardOutputContent"].strip()
            return output if output else None

        return None

    except Exception:
        return None
