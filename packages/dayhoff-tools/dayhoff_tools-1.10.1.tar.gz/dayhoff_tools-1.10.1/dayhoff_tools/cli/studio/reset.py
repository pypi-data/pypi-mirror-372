"""Studio reset command."""

from typing import Optional

import boto3
import typer
from botocore.exceptions import ClientError
from rich.prompt import Confirm

from ..engine_studio_utils.api_utils import get_user_studio
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console


def reset_studio(
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Reset a different user's studio"
    ),
):
    """Reset a stuck studio (admin operation)."""
    username = check_aws_sso()

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Add warning when resetting another user's studio
    if target_user != username:
        console.print(f"[yellow]⚠️  Resetting studio for user: {target_user}[/yellow]")

    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio.[/yellow]")
        else:
            console.print(f"[yellow]User {target_user} doesn't have a studio.[/yellow]")
        return

    console.print(f"[yellow]⚠️  This will force-reset the studio state[/yellow]")
    console.print(f"Current status: {studio['status']}")
    if studio.get("attached_vm_id"):
        console.print(f"Listed as attached to: {studio['attached_vm_id']}")

    if not Confirm.ask("\nReset studio state?"):
        console.print("Reset cancelled.")
        return

    # Direct DynamoDB update
    console.print("Resetting studio state...")

    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("dev-studios")

    try:
        # Check if volume is actually attached
        ec2 = boto3.client("ec2", region_name="us-east-1")
        volumes = ec2.describe_volumes(VolumeIds=[studio["studio_id"]])

        if volumes["Volumes"]:
            volume = volumes["Volumes"][0]
            attachments = volume.get("Attachments", [])
            if attachments:
                console.print(
                    f"[red]Volume is still attached to {attachments[0]['InstanceId']}![/red]"
                )
                if Confirm.ask("Force-detach the volume?"):
                    ec2.detach_volume(
                        VolumeId=studio["studio_id"],
                        InstanceId=attachments[0]["InstanceId"],
                        Force=True,
                    )
                    console.print("Waiting for volume to detach...")
                    waiter = ec2.get_waiter("volume_available")
                    waiter.wait(VolumeIds=[studio["studio_id"]])

        # Reset in DynamoDB – align attribute names with Studio Manager backend
        table.update_item(
            Key={"StudioID": studio["studio_id"]},
            UpdateExpression="SET #st = :status, AttachedVMID = :vm_id, AttachedDevice = :device",
            ExpressionAttributeNames={"#st": "Status"},
            ExpressionAttributeValues={
                ":status": "available",
                ":vm_id": None,
                ":device": None,
            },
        )

        console.print(f"[green]✓ Studio reset to available state![/green]")

    except ClientError as e:
        console.print(f"[red]❌ Failed to reset studio: {e}[/red]")
