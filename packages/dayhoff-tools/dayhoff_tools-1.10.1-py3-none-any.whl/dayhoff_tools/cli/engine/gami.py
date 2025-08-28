"""Engine GAMI (Golden AMI) creation command."""

from datetime import datetime

import boto3
import typer
from botocore.exceptions import ClientError
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from ..engine_studio_utils.api_utils import make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console
from ..engine_studio_utils.formatting import resolve_engine


def create_ami(
    name_or_id: str = typer.Argument(
        help="Engine name or instance ID to create AMI from"
    ),
):
    """Create a 'Golden AMI' from a running engine.

    This process is for creating a pre-warmed, standardized machine image
    that can be used to launch new engines more quickly.

    IMPORTANT:
    - The engine MUST have all studios detached before running this command.
    - This process will make the source engine unusable. You should
      plan to TERMINATE the engine after the AMI is created.
    """
    check_aws_sso()

    # Get all engines to resolve name and check status
    # We pass check_ready=True to get attached studio info
    response = make_api_request("GET", "/engines", params={"check_ready": "true"})
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    # --- Pre-flight checks ---

    # 1. Check if engine is running
    if engine["state"].lower() != "running":
        console.print(f"[red]❌ Engine '{engine['name']}' is not running.[/red]")
        console.print("Please start it before creating an AMI.")
        raise typer.Exit(1)

    # 2. Check for attached studios from the detailed API response
    attached_studios = engine.get("studios", [])
    if attached_studios:
        console.print(
            f"[bold red]❌ Engine '{engine['name']}' has studios attached.[/bold red]"
        )
        console.print("Please detach all studios before creating an AMI:")
        for studio in attached_studios:
            console.print(f"  - {studio['user']} ({studio['studio_id']})")
        console.print("\nTo detach, run [bold]dh studio detach[/bold]")
        raise typer.Exit(1)

    # Construct AMI name and description
    ami_name = (
        f"prewarmed-engine-{engine['engine_type']}-{datetime.now().strftime('%Y%m%d')}"
    )
    description = (
        f"Amazon Linux 2023 with NVIDIA drivers, Docker, and pre-pulled "
        f"dev container image for {engine['engine_type']} engines"
    )

    console.print(f"Creating AMI from engine [cyan]{engine['name']}[/cyan]...")
    console.print(f"[bold]AMI Name:[/] {ami_name}")
    console.print(f"[bold]Description:[/] {description}")

    console.print(
        "\n[bold yellow]⚠️  Important:[/bold yellow]\n"
        "1. This process will run cleanup scripts on the engine.\n"
        "2. The source engine should be [bold]terminated[/bold] after the AMI is created.\n"
    )

    if not Confirm.ask("Continue with AMI creation?"):
        raise typer.Exit()

    # Create AMI using EC2 client directly, as the backend logic is too complex
    ec2 = boto3.client("ec2", region_name="us-east-1")
    ssm = boto3.client("ssm", region_name="us-east-1")

    try:
        # Clean up instance state before snapshotting
        console.print("Cleaning up instance for AMI creation...")
        cleanup_commands = [
            "sudo rm -f /opt/dayhoff/first_boot_complete.sentinel",
            "history -c",
            "sudo rm -rf /tmp/* /var/log/messages /var/log/cloud-init.log",
            "sudo rm -rf /var/lib/amazon/ssm/* /etc/amazon/ssm/*",
            "sleep 2 && sudo systemctl stop amazon-ssm-agent &",  # Stop agent last
        ]

        cleanup_response = ssm.send_command(
            InstanceIds=[engine["instance_id"]],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": cleanup_commands, "executionTimeout": ["120"]},
        )

        # Acknowledge that the SSM command might be in progress as the agent shuts down
        console.print(
            "[dim]ℹ️  Cleanup command sent (status may show 'InProgress' as SSM agent stops)[/dim]"
        )

        # Create the AMI
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(
                "Creating AMI (this will take several minutes)...", total=None
            )

            response = ec2.create_image(
                InstanceId=engine["instance_id"],
                Name=ami_name,
                Description=description,
                NoReboot=False,
                TagSpecifications=[
                    {
                        "ResourceType": "image",
                        "Tags": [
                            {"Key": "Environment", "Value": "dev"},
                            {"Key": "Type", "Value": "golden-ami"},
                            {"Key": "EngineType", "Value": engine["engine_type"]},
                            {"Key": "Name", "Value": ami_name},
                        ],
                    }
                ],
            )

            ami_id = response["ImageId"]
            progress.update(
                task,
                completed=True,
                description=f"[green]✓ AMI creation initiated![/green]",
            )

        console.print(f"  [bold]AMI ID:[/] {ami_id}")
        console.print("\nThe AMI creation process will continue in the background.")
        console.print("You can monitor progress in the EC2 Console under 'AMIs'.")
        console.print(
            "\nOnce complete, update the AMI ID in [bold]terraform/environments/dev/variables.tf[/bold] "
            "and run [bold]terraform apply[/bold]."
        )
        console.print(
            f"\nRemember to [bold red]terminate the source engine '{engine['name']}'[/bold red] to save costs."
        )

    except ClientError as e:
        console.print(f"[red]❌ Failed to create AMI: {e}[/red]")
        raise typer.Exit(1)
