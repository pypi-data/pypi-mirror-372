"""Engine list command."""

from datetime import datetime, timezone
from typing import Optional

import typer
from rich import box
from rich.table import Table

from ..engine_studio_utils.api_utils import make_api_request
from ..engine_studio_utils.aws_utils import _fetch_init_stages, check_aws_sso
from ..engine_studio_utils.constants import HOURLY_COSTS, console
from ..engine_studio_utils.formatting import (
    format_duration,
    format_status,
    get_disk_usage_via_ssm,
    parse_launch_time,
)


def list_engines(
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Filter by user"),
    running_only: bool = typer.Option(
        False, "--running", help="Show only running engines"
    ),
    stopped_only: bool = typer.Option(
        False, "--stopped", help="Show only stopped engines"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed status (slower)"
    ),
):
    """List engines (shows all engines by default)."""
    current_user = check_aws_sso()

    params = {}
    if user:
        params["user"] = user
    if detailed:
        params["check_ready"] = "true"

    response = make_api_request("GET", "/engines", params=params)

    if response.status_code == 200:
        data = response.json()
        engines = data.get("engines", [])

        # Filter by state if requested
        if running_only:
            engines = [e for e in engines if e["state"].lower() == "running"]
        elif stopped_only:
            engines = [e for e in engines if e["state"].lower() == "stopped"]

        if not engines:
            console.print("No engines found.")
            return

        # Only fetch detailed info if requested (slow)
        stages_map = {}
        if detailed:
            stages_map = _fetch_init_stages([e["instance_id"] for e in engines])

        # Create table
        table = Table(title="Engines", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Instance ID", style="dim")
        table.add_column("Type")
        table.add_column("User")
        table.add_column("Status")
        if detailed:
            table.add_column("Disk Usage")
        table.add_column("Uptime/Since")
        table.add_column("$/hour", justify="right")

        for engine in engines:
            launch_time = parse_launch_time(engine["launch_time"])
            uptime = datetime.now(timezone.utc) - launch_time
            hourly_cost = HOURLY_COSTS.get(engine["engine_type"], 0)

            if engine["state"].lower() == "running":
                time_str = format_duration(uptime)
                # Only get disk usage if detailed mode
                if detailed:
                    disk_usage = get_disk_usage_via_ssm(engine["instance_id"]) or "-"
                else:
                    disk_usage = None
            else:
                time_str = launch_time.strftime("%Y-%m-%d %H:%M")
                disk_usage = "-" if detailed else None

            row_data = [
                engine["name"],
                engine["instance_id"],
                engine["engine_type"],
                engine["user"],
                format_status(engine["state"], engine.get("ready")),
            ]
            if detailed:
                row_data.append(disk_usage)
            row_data.extend(
                [
                    time_str,
                    f"${hourly_cost:.2f}",
                ]
            )

            table.add_row(*row_data)

        console.print(table)
        if not detailed and any(e["state"].lower() == "running" for e in engines):
            console.print(
                "\n[dim]Tip: Use --detailed to see disk usage and bootstrap status (slower)[/dim]"
            )
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to list engines: {error}[/red]")
