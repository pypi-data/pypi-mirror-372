"""Studio list command."""

import typer
from rich import box
from rich.table import Table

from ..engine_studio_utils.api_utils import make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console
from ..engine_studio_utils.formatting import get_studio_disk_usage_via_ssm


def list_studios(
    all_users: bool = typer.Option(
        False, "--all", "-a", help="Show all users' studios"
    ),
):
    """List studios."""
    username = check_aws_sso()

    response = make_api_request("GET", "/studios")

    if response.status_code == 200:
        studios = response.json().get("studios", [])

        if not studios:
            console.print("No studios found.")
            return

        # Get all engines to map instance IDs to names
        engines_response = make_api_request("GET", "/engines")
        engines = {}
        if engines_response.status_code == 200:
            for engine in engines_response.json().get("engines", []):
                engines[engine["instance_id"]] = engine["name"]

        # Create table
        table = Table(title="Studios", box=box.ROUNDED)
        table.add_column("Studio ID", style="cyan")
        table.add_column("User")
        table.add_column("Status")
        table.add_column("Size", justify="right")
        table.add_column("Disk Usage", justify="right")
        table.add_column("Attached To")

        for studio in studios:
            # Change status display
            if studio["status"] == "in-use":
                status_display = "[bright_blue]attached[/bright_blue]"
            elif studio["status"] in ["attaching", "detaching"]:
                status_display = "[yellow]" + studio["status"] + "[/yellow]"
            else:
                status_display = "[green]available[/green]"

            # Format attached engine info
            attached_to = "-"
            disk_usage = "?/?"
            if studio.get("attached_vm_id"):
                vm_id = studio["attached_vm_id"]
                engine_name = engines.get(vm_id, "unknown")
                attached_to = f"{engine_name} ({vm_id})"

                # Try to get disk usage if attached
                if studio["status"] == "in-use":
                    usage = get_studio_disk_usage_via_ssm(vm_id, studio["user"])
                    if usage:
                        disk_usage = usage

            table.add_row(
                studio["studio_id"],
                studio["user"],
                status_display,
                f"{studio['size_gb']}GB",
                disk_usage,
                attached_to,
            )

        console.print(table)
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to list studios: {error}[/red]")
