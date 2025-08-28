"""Studio create command."""

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..engine_studio_utils.api_utils import get_user_studio, make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console


def create_studio(
    size_gb: int = typer.Option(50, "--size", "-s", help="Studio size in GB"),
):
    """Create a new studio for the current user."""
    username = check_aws_sso()

    # Check if user already has a studio
    existing = get_user_studio(username)
    if existing:
        console.print(
            f"[yellow]You already have a studio: {existing['studio_id']}[/yellow]"
        )
        return

    console.print(f"Creating {size_gb}GB studio for user [cyan]{username}[/cyan]...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Creating studio volume...", total=None)

        response = make_api_request(
            "POST",
            "/studios",
            json_data={"user": username, "size_gb": size_gb},
        )

    if response.status_code == 201:
        data = response.json()
        console.print(f"[green]✓ Studio created successfully![/green]")
        console.print(f"Studio ID: [cyan]{data['studio_id']}[/cyan]")
        console.print(f"Size: {data['size_gb']}GB")
        console.print(f"\nNext step: [cyan]dh studio attach <engine-name>[/cyan]")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to create studio: {error}[/red]")
