"""AWS-specific utilities for engine and studio commands."""

import subprocess
from typing import Dict, List

import boto3
import typer
from botocore.exceptions import ClientError, NoCredentialsError
from rich.prompt import Confirm

from .constants import console


def check_aws_sso() -> str:
    """Check AWS SSO status and return username."""
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        # Parse username from assumed role ARN
        # Format: arn:aws:sts::123456789012:assumed-role/AWSReservedSSO_DeveloperAccess_xxxx/username
        arn = identity["Arn"]
        if "assumed-role" in arn:
            username = arn.split("/")[-1]
            return username
        else:
            # Fallback for other auth methods
            return identity["UserId"].split(":")[-1]
    except (NoCredentialsError, ClientError):
        console.print("[red]❌ Not logged in to AWS SSO[/red]")
        console.print("Please run: [cyan]aws sso login[/cyan]")
        if Confirm.ask("Would you like to login now?"):
            try:
                result = subprocess.run(
                    ["aws", "sso", "login"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                if result.returncode == 0:
                    console.print("[green]✓ Successfully logged in![/green]")
                    return check_aws_sso()
            except subprocess.CalledProcessError as e:
                console.print(f"[red]Login failed: {e}[/red]")
        raise typer.Exit(1)


def get_api_url() -> str:
    """Get Studio Manager API URL from SSM Parameter Store."""
    ssm = boto3.client("ssm", region_name="us-east-1")
    try:
        response = ssm.get_parameter(Name="/dev/studio-manager/api-url")
        return response["Parameter"]["Value"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "ParameterNotFound":
            console.print(
                "[red]❌ API URL parameter not found in SSM Parameter Store[/red]"
            )
            console.print(
                "Please ensure the Studio Manager infrastructure is deployed."
            )
        else:
            console.print(f"[red]❌ Error retrieving API URL: {e}[/red]")
        raise typer.Exit(1)


def _colour_stage(stage: str) -> str:
    """Return colourised stage name for table output."""
    if not stage:
        return "[dim]-[/dim]"
    low = stage.lower()
    if low.startswith("error"):
        return f"[red]{stage}[/red]"
    if low == "finished":
        return f"[green]{stage}[/green]"
    return f"[yellow]{stage}[/yellow]"


def _fetch_init_stages(instance_ids: List[str]) -> Dict[str, str]:
    """Fetch DayhoffInitStage tag for many instances in one call."""
    if not instance_ids:
        return {}
    ec2 = boto3.client("ec2", region_name="us-east-1")
    stages: Dict[str, str] = {}
    try:
        paginator = ec2.get_paginator("describe_instances")
        for page in paginator.paginate(InstanceIds=instance_ids):
            for res in page["Reservations"]:
                for inst in res["Instances"]:
                    iid = inst["InstanceId"]
                    tag_val = next(
                        (
                            t["Value"]
                            for t in inst.get("Tags", [])
                            if t["Key"] == "DayhoffInitStage"
                        ),
                        None,
                    )
                    if tag_val:
                        stages[iid] = tag_val
    except Exception:
        pass  # best-effort
    return stages
