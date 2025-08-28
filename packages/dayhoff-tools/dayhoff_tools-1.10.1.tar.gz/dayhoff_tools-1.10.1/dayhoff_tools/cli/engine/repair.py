"""Engine repair command."""

import time

import boto3
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from ..engine_studio_utils.api_utils import make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console
from ..engine_studio_utils.formatting import resolve_engine


def repair_engine(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
):
    """Repair an engine that's stuck in a bad state (e.g., after GAMI creation)."""
    check_aws_sso()

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)

    if engine["state"].lower() != "running":
        console.print(
            f"[yellow]⚠️  Engine is {engine['state']}. Must be running to repair.[/yellow]"
        )
        if engine["state"].lower() == "stopped" and Confirm.ask(
            "Start the engine first?"
        ):
            response = make_api_request(
                "POST", f"/engines/{engine['instance_id']}/start"
            )
            if response.status_code != 200:
                console.print("[red]❌ Failed to start engine[/red]")
                raise typer.Exit(1)
            console.print("[green]✓ Engine started[/green]")
            console.print("Waiting for engine to become ready...")
            time.sleep(30)  # Give it time to boot
        else:
            raise typer.Exit(1)

    console.print(f"[bold]Repairing engine [cyan]{engine['name']}[/cyan][/bold]")
    console.print(
        "[dim]This will restore bootstrap state and ensure all services are running[/dim]\n"
    )

    ssm = boto3.client("ssm", region_name="us-east-1")

    # Repair commands
    repair_commands = [
        # Create necessary directories
        "sudo mkdir -p /opt/dayhoff /opt/dayhoff/state /opt/dayhoff/scripts",
        # Download scripts from S3 if missing
        "source /etc/engine.env && sudo aws s3 sync s3://${VM_SCRIPTS_BUCKET}/ /opt/dayhoff/scripts/ --exclude '*' --include '*.sh' --quiet",
        "sudo chmod +x /opt/dayhoff/scripts/*.sh 2>/dev/null || true",
        # Restore bootstrap state
        "sudo touch /opt/dayhoff/first_boot_complete.sentinel",
        "echo 'finished' | sudo tee /opt/dayhoff/state/engine-init.stage > /dev/null",
        # Ensure SSM agent is running
        "sudo systemctl restart amazon-ssm-agent 2>/dev/null || true",
        # Restart idle detector (service only)
        "sudo systemctl restart engine-idle-detector.service 2>/dev/null || true",
        # Report status
        "echo '=== Repair Complete ===' && echo 'Sentinel: ' && ls -la /opt/dayhoff/first_boot_complete.sentinel",
        "echo 'Stage: ' && cat /opt/dayhoff/state/engine-init.stage",
        "echo 'Scripts: ' && ls /opt/dayhoff/scripts/*.sh 2>/dev/null | wc -l",
    ]

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Repairing engine...", total=None)

            response = ssm.send_command(
                InstanceIds=[engine["instance_id"]],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    "commands": repair_commands,
                    "executionTimeout": ["60"],
                },
            )

            command_id = response["Command"]["CommandId"]

            # Wait for command
            for _ in range(60):
                time.sleep(1)
                result = ssm.get_command_invocation(
                    CommandId=command_id,
                    InstanceId=engine["instance_id"],
                )
                if result["Status"] in ["Success", "Failed"]:
                    break

        if result["Status"] == "Success":
            output = result["StandardOutputContent"]
            console.print("[green]✓ Engine repaired successfully![/green]\n")

            # Show repair results
            if "=== Repair Complete ===" in output:
                repair_section = output.split("=== Repair Complete ===")[1].strip()
                console.print("[bold]Repair Results:[/bold]")
                console.print(repair_section)

            console.print(
                "\n[dim]You should now be able to attach studios to this engine.[/dim]"
            )
        else:
            console.print(
                f"[red]❌ Repair failed: {result.get('StandardErrorContent', 'Unknown error')}[/red]"
            )
            console.print(
                "\n[yellow]Try running 'dh engine debug' for more information.[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]❌ Failed to repair engine: {e}[/red]")
