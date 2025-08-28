"""Engine launch command."""

from typing import Any, Dict, Optional

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..engine_studio_utils.api_utils import make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import HOURLY_COSTS, console


def launch_engine(
    name: str = typer.Argument(help="Name for the new engine"),
    engine_type: str = typer.Option(
        "cpu",
        "--type",
        "-t",
        help="Engine type: cpu, cpumax, t4, a10g, a100, 4_t4, 8_t4, 4_a10g, 8_a10g",
    ),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Override username"),
    boot_disk_size: Optional[int] = typer.Option(
        None,
        "--size",
        "-s",
        help="Boot disk size in GB (default: 50GB, min: 20GB, max: 1000GB)",
    ),
    availability_zone: Optional[str] = typer.Option(
        None,
        "--az",
        help="Prefer a specific Availability Zone (e.g., us-east-1b). If omitted the service will try all public subnets.",
    ),
):
    """Launch a new engine instance."""
    username = check_aws_sso()
    if user:
        username = user

    # Validate engine type
    valid_types = [
        "cpu",
        "cpumax",
        "t4",
        "a10g",
        "a100",
        "4_t4",
        "8_t4",
        "4_a10g",
        "8_a10g",
    ]
    if engine_type not in valid_types:
        console.print(f"[red]❌ Invalid engine type: {engine_type}[/red]")
        console.print(f"Valid types: {', '.join(valid_types)}")
        raise typer.Exit(1)

    # Validate boot disk size
    if boot_disk_size is not None:
        if boot_disk_size < 20:
            console.print("[red]❌ Boot disk size must be at least 20GB[/red]")
            raise typer.Exit(1)
        if boot_disk_size > 1000:
            console.print("[red]❌ Boot disk size cannot exceed 1000GB[/red]")
            raise typer.Exit(1)

    cost = HOURLY_COSTS.get(engine_type, 0)
    disk_info = f" with {boot_disk_size}GB boot disk" if boot_disk_size else ""
    console.print(
        f"Launching [cyan]{name}[/cyan] ({engine_type}){disk_info} for ${cost:.2f}/hour..."
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Creating engine...", total=None)

        request_data: Dict[str, Any] = {
            "name": name,
            "user": username,
            "engine_type": engine_type,
        }
        if boot_disk_size is not None:
            request_data["boot_disk_size"] = boot_disk_size
        if availability_zone:
            request_data["availability_zone"] = availability_zone

        response = make_api_request("POST", "/engines", json_data=request_data)

    if response.status_code == 201:
        data = response.json()
        console.print(f"[green]✓ Engine launched successfully![/green]")
        console.print(f"Instance ID: [cyan]{data['instance_id']}[/cyan]")
        console.print(f"Type: {data['instance_type']} (${cost:.2f}/hour)")
        if boot_disk_size:
            console.print(f"Boot disk: {boot_disk_size}GB")
        console.print("\nThe engine is initializing. This may take a few minutes.")
        console.print(f"Check status with: [cyan]dh engine status {name}[/cyan]")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to launch engine: {error}[/red]")
