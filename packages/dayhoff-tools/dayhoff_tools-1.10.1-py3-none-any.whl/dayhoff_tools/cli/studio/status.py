"""Studio status command."""

from typing import Optional

import typer
from rich.panel import Panel

from ..engine_studio_utils.api_utils import get_user_studio, make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console


def studio_status(
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Check status for a different user (admin only)"
    ),
):
    """Show status of your studio."""
    username = check_aws_sso()

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Add warning when checking another user's studio
    if target_user != username:
        console.print(
            f"[yellow]⚠️  Checking studio status for user: {target_user}[/yellow]"
        )

    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio yet.[/yellow]")
            console.print("Create one with: [cyan]dh studio create[/cyan]")
        else:
            console.print(f"[yellow]User {target_user} doesn't have a studio.[/yellow]")
        return

    # Create status panel
    # Format status with colors
    status = studio["status"]
    if status == "in-use":
        status_display = "[bright_blue]attached[/bright_blue]"
    elif status in ["attaching", "detaching"]:
        status_display = f"[yellow]{status}[/yellow]"
    else:
        status_display = f"[green]{status}[/green]"

    status_lines = [
        f"[bold]Studio ID:[/bold]    {studio['studio_id']}",
        f"[bold]User:[/bold]         {studio['user']}",
        f"[bold]Status:[/bold]       {status_display}",
        f"[bold]Size:[/bold]         {studio['size_gb']}GB",
        f"[bold]Created:[/bold]      {studio['creation_date']}",
    ]

    if studio.get("attached_vm_id"):
        status_lines.append(f"[bold]Attached to:[/bold]  {studio['attached_vm_id']}")

        # Try to get engine details
        response = make_api_request("GET", "/engines")
        if response.status_code == 200:
            engines = response.json().get("engines", [])
            attached_engine = next(
                (e for e in engines if e["instance_id"] == studio["attached_vm_id"]),
                None,
            )
            if attached_engine:
                status_lines.append(
                    f"[bold]Engine Name:[/bold]  {attached_engine['name']}"
                )

    panel = Panel(
        "\n".join(status_lines),
        title="Studio Details",
        border_style="blue",
    )
    console.print(panel)
