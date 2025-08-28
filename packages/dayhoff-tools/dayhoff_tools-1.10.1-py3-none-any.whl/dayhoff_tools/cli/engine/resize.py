"""Engine resize command."""

import time

import boto3
import typer
from botocore.exceptions import ClientError
from rich.prompt import Confirm

from ..engine_studio_utils.api_utils import make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console
from ..engine_studio_utils.formatting import resolve_engine


def resize_engine(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    size: int = typer.Option(..., "--size", "-s", help="New size in GB"),
    online: bool = typer.Option(
        False,
        "--online",
        help="Resize while running (requires manual filesystem expansion)",
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force resize and detach all studios"
    ),
):
    """Resize an engine's boot disk."""
    check_aws_sso()

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    # Get current volume info to validate size
    ec2 = boto3.client("ec2", region_name="us-east-1")

    try:
        # Get instance details to find root volume
        instance_info = ec2.describe_instances(InstanceIds=[engine["instance_id"]])
        instance = instance_info["Reservations"][0]["Instances"][0]

        # Find root volume
        root_device = instance.get("RootDeviceName", "/dev/xvda")
        root_volume_id = None

        for bdm in instance.get("BlockDeviceMappings", []):
            if bdm["DeviceName"] == root_device:
                root_volume_id = bdm["Ebs"]["VolumeId"]
                break

        if not root_volume_id:
            console.print("[red]❌ Could not find root volume[/red]")
            raise typer.Exit(1)

        # Get current volume size
        volumes = ec2.describe_volumes(VolumeIds=[root_volume_id])
        current_size = volumes["Volumes"][0]["Size"]

        if size <= current_size:
            console.print(
                f"[red]❌ New size ({size}GB) must be larger than current size ({current_size}GB)[/red]"
            )
            raise typer.Exit(1)

        console.print(
            f"[yellow]Resizing engine boot disk from {current_size}GB to {size}GB[/yellow]"
        )

        # Check if we need to stop the instance
        if not online and engine["state"].lower() == "running":
            console.print("Stopping engine for offline resize...")
            stop_response = make_api_request(
                "POST",
                f"/engines/{engine['instance_id']}/stop",
                json_data={"detach_studios": False},
            )
            if stop_response.status_code != 200:
                console.print("[red]❌ Failed to stop engine[/red]")
                raise typer.Exit(1)

            # Wait for instance to stop
            console.print("Waiting for engine to stop...")
            waiter = ec2.get_waiter("instance_stopped")
            waiter.wait(InstanceIds=[engine["instance_id"]])
            console.print("[green]✓ Engine stopped[/green]")

        # Call the resize API
        console.print("Resizing volume...")
        resize_response = make_api_request(
            "POST",
            f"/engines/{engine['instance_id']}/resize",
            json_data={"size": size, "detach_studios": force},
        )

        if resize_response.status_code == 409 and not force:
            # Engine has attached studios
            data = resize_response.json()
            attached_studios = data.get("attached_studios", [])

            console.print("\n[yellow]⚠️  This engine has attached studios:[/yellow]")
            for studio in attached_studios:
                console.print(f"  • {studio['user']} ({studio['studio_id']})")

            if Confirm.ask("\nDetach all studios and resize the engine?"):
                resize_response = make_api_request(
                    "POST",
                    f"/engines/{engine['instance_id']}/resize",
                    json_data={"size": size, "detach_studios": True},
                )
            else:
                console.print("Resize cancelled.")
                return

        if resize_response.status_code != 200:
            error = resize_response.json().get("error", "Unknown error")
            console.print(f"[red]❌ Failed to resize engine: {error}[/red]")
            raise typer.Exit(1)

        # Check if studios were detached
        data = resize_response.json()
        detached_studios = data.get("detached_studios", 0)
        if detached_studios > 0:
            console.print(
                f"[green]✓ Detached {detached_studios} studio(s) before resize[/green]"
            )

        # Wait for modification to complete
        console.print("Waiting for volume modification to complete...")
        while True:
            mod_state = ec2.describe_volumes_modifications(VolumeIds=[root_volume_id])
            if not mod_state["VolumesModifications"]:
                break  # Modification complete

            modification = mod_state["VolumesModifications"][0]
            state = modification["ModificationState"]
            progress = modification.get("Progress", 0)

            # Show progress updates only for the resize phase
            if state == "modifying":
                console.print(f"[yellow]Progress: {progress}%[/yellow]")

            # Exit as soon as optimization starts (resize is complete)
            if state == "optimizing":
                console.print("[green]✓ Volume resized successfully[/green]")
                console.print(
                    "[dim]AWS is optimizing the volume in the background (no action needed).[/dim]"
                )
                break

            if state == "completed":
                console.print("[green]✓ Volume resized successfully[/green]")
                break
            elif state == "failed":
                console.print("[red]❌ Volume modification failed[/red]")
                raise typer.Exit(1)

            time.sleep(2)  # Check more frequently for better UX

        # If offline resize, start the instance back up
        if not online and engine["state"].lower() == "running":
            console.print("Starting engine back up...")
            start_response = make_api_request(
                "POST", f"/engines/{engine['instance_id']}/start"
            )
            if start_response.status_code != 200:
                console.print(
                    "[yellow]⚠️  Failed to restart engine automatically[/yellow]"
                )
                console.print(
                    f"Please start it manually: [cyan]dh engine start {engine['name']}[/cyan]"
                )
            else:
                console.print("[green]✓ Engine started[/green]")
                console.print("The filesystem will be automatically expanded on boot.")

        elif online and engine["state"].lower() == "running":
            console.print(
                "\n[yellow]⚠️  Online resize complete. You must now expand the filesystem:[/yellow]"
            )
            console.print(f"1. SSH into the engine: [cyan]ssh {engine['name']}[/cyan]")
            console.print("2. Find the root device: [cyan]lsblk[/cyan]")
            console.print(
                "3. Expand the partition: [cyan]sudo growpart /dev/nvme0n1 1[/cyan] (adjust device name as needed)"
            )
            console.print("4. Expand the filesystem: [cyan]sudo xfs_growfs /[/cyan]")

    except ClientError as e:
        console.print(f"[red]❌ Failed to resize engine: {e}[/red]")
        raise typer.Exit(1)
