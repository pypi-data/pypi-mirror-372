"""Studio resize command."""

import time
from typing import Optional

import boto3
import typer
from botocore.exceptions import ClientError
from rich.prompt import Confirm

from ..engine_studio_utils.api_utils import get_user_studio, make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console


def resize_studio(
    size: int = typer.Option(..., "--size", "-s", help="New size in GB"),
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Resize a different user's studio (admin only)"
    ),
):
    """Resize your studio volume (requires detachment)."""
    username = check_aws_sso()

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Add warning when resizing another user's studio
    if target_user != username:
        console.print(f"[yellow]⚠️  Resizing studio for user: {target_user}[/yellow]")

    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio yet.[/yellow]")
        else:
            console.print(f"[yellow]User {target_user} doesn't have a studio.[/yellow]")
        return

    current_size = studio["size_gb"]

    if size <= current_size:
        console.print(
            f"[red]❌ New size ({size}GB) must be larger than current size ({current_size}GB)[/red]"
        )
        raise typer.Exit(1)

    # Check if studio is attached
    if studio["status"] == "in-use":
        console.print("[yellow]⚠️  Studio must be detached before resizing[/yellow]")
        console.print(f"Currently attached to: {studio.get('attached_vm_id')}")

        if not Confirm.ask("\nDetach studio and proceed with resize?"):
            console.print("Resize cancelled.")
            return

        # Detach the studio
        console.print("Detaching studio...")
        response = make_api_request("POST", f"/studios/{studio['studio_id']}/detach")
        if response.status_code != 200:
            console.print("[red]❌ Failed to detach studio[/red]")
            raise typer.Exit(1)

        console.print("[green]✓ Studio detached[/green]")

        # Wait a moment for detachment to complete
        time.sleep(5)

    console.print(f"[yellow]Resizing studio from {current_size}GB to {size}GB[/yellow]")

    # Call the resize API
    resize_response = make_api_request(
        "POST", f"/studios/{studio['studio_id']}/resize", json_data={"size": size}
    )

    if resize_response.status_code != 200:
        error = resize_response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to resize studio: {error}[/red]")
        raise typer.Exit(1)

    # Wait for volume modification to complete
    ec2 = boto3.client("ec2", region_name="us-east-1")
    console.print("Resizing volume...")

    # Track progress
    last_progress = 0

    while True:
        try:
            mod_state = ec2.describe_volumes_modifications(
                VolumeIds=[studio["studio_id"]]
            )
            if not mod_state["VolumesModifications"]:
                break  # Modification complete

            modification = mod_state["VolumesModifications"][0]
            state = modification["ModificationState"]
            progress = modification.get("Progress", 0)

            # Show progress updates only for the resize phase
            if state == "modifying" and progress > last_progress:
                console.print(f"[yellow]Progress: {progress}%[/yellow]")
                last_progress = progress

            # Exit as soon as optimization starts (resize is complete)
            if state == "optimizing":
                console.print(
                    f"[green]✓ Studio resized successfully to {size}GB![/green]"
                )
                console.print(
                    "[dim]AWS is optimizing the volume in the background (no action needed).[/dim]"
                )
                break

            if state == "completed":
                console.print(
                    f"[green]✓ Studio resized successfully to {size}GB![/green]"
                )
                break
            elif state == "failed":
                console.print("[red]❌ Volume modification failed[/red]")
                raise typer.Exit(1)

            time.sleep(2)  # Check more frequently for better UX

        except ClientError:
            # Modification might be complete
            console.print(f"[green]✓ Studio resized successfully to {size}GB![/green]")
            break

    console.print(
        "\n[dim]The filesystem will be automatically expanded when you next attach the studio.[/dim]"
    )
    console.print(f"To attach: [cyan]dh studio attach <engine-name>[/cyan]")
