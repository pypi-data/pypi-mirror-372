"""Engine debug command."""

import time

import boto3
import typer

from ..engine_studio_utils.api_utils import make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console
from ..engine_studio_utils.formatting import resolve_engine


def debug_engine(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
):
    """Debug engine bootstrap status and files."""
    check_aws_sso()

    # Resolve engine
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    console.print(f"[bold]Debug info for {engine['name']}:[/bold]\n")

    ssm = boto3.client("ssm", region_name="us-east-1")

    # Check multiple files and systemd status
    checks = [
        (
            "Stage file",
            "cat /opt/dayhoff/state/engine-init.stage 2>/dev/null || cat /var/run/engine-init.stage 2>/dev/null || echo 'MISSING'",
        ),
        (
            "Health file",
            "cat /opt/dayhoff/state/engine-health.json 2>/dev/null || cat /var/run/engine-health.json 2>/dev/null || echo 'MISSING'",
        ),
        (
            "Sentinel file",
            "ls -la /opt/dayhoff/first_boot_complete.sentinel 2>/dev/null || echo 'MISSING'",
        ),
        (
            "Setup service",
            "systemctl status setup-aws-vm.service --no-pager || echo 'Service not found'",
        ),
        (
            "Bootstrap log tail",
            "tail -20 /var/log/engine-setup.log 2>/dev/null || echo 'No log'",
        ),
        ("Environment file", "cat /etc/engine.env 2>/dev/null || echo 'MISSING'"),
    ]

    for name, cmd in checks:
        try:
            resp = ssm.send_command(
                InstanceIds=[engine["instance_id"]],
                DocumentName="AWS-RunShellScript",
                Parameters={"commands": [cmd], "executionTimeout": ["10"]},
            )
            cid = resp["Command"]["CommandId"]
            time.sleep(1)
            inv = ssm.get_command_invocation(
                CommandId=cid, InstanceId=engine["instance_id"]
            )

            if inv["Status"] == "Success":
                output = inv["StandardOutputContent"].strip()
                console.print(f"[cyan]{name}:[/cyan]")
                console.print(f"[dim]{output}[/dim]\n")
            else:
                console.print(f"[cyan]{name}:[/cyan] [red]FAILED[/red]\n")

        except Exception as e:
            console.print(f"[cyan]{name}:[/cyan] [red]ERROR: {e}[/red]\n")
