"""Studio attach command."""

import time
from typing import Optional

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm, IntPrompt

from ..engine_studio_utils.api_utils import get_user_studio, make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console
from ..engine_studio_utils.formatting import resolve_engine
from ..engine_studio_utils.ssh_utils import (
    check_session_manager_plugin,
    get_ssh_public_key,
    update_ssh_config_entry,
)


def attach_studio(
    engine_name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Attach a different user's studio (admin only)"
    ),
):
    """Attach your studio to an engine."""
    username = check_aws_sso()

    # Check for Session Manager Plugin since we'll update SSH config
    if not check_session_manager_plugin():
        raise typer.Exit(1)

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Add confirmation when attaching another user's studio
    if target_user != username:
        console.print(f"[yellow]⚠️  Managing studio for user: {target_user}[/yellow]")
        if not Confirm.ask(f"Are you sure you want to attach {target_user}'s studio?"):
            console.print("Operation cancelled.")
            return

    # Get user's studio
    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio yet.[/yellow]")
            if Confirm.ask("Would you like to create one now?"):
                size = IntPrompt.ask("Studio size (GB)", default=50)
                response = make_api_request(
                    "POST",
                    "/studios",
                    json_data={"user": username, "size_gb": size},
                )
                if response.status_code != 201:
                    console.print("[red]❌ Failed to create studio[/red]")
                    raise typer.Exit(1)
                studio = response.json()
                studio["studio_id"] = studio["studio_id"]  # Normalize key
            else:
                raise typer.Exit(0)
        else:
            console.print(f"[red]❌ User {target_user} doesn't have a studio.[/red]")
            raise typer.Exit(1)

    # Check if already attached
    if studio.get("status") == "in-use":
        console.print(
            f"[yellow]Studio is already attached to {studio.get('attached_vm_id')}[/yellow]"
        )
        if not Confirm.ask("Detach and reattach to new engine?"):
            return
        # Detach first
        response = make_api_request("POST", f"/studios/{studio['studio_id']}/detach")
        if response.status_code != 200:
            console.print("[red]❌ Failed to detach studio[/red]")
            raise typer.Exit(1)

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(engine_name_or_id, engines)

    # Flag to track if we started the engine in this command (affects retry length)
    engine_started_now: bool = False

    if engine["state"].lower() != "running":
        console.print(f"[yellow]⚠️  Engine is {engine['state']}[/yellow]")
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
            # Mark that we booted the engine so attach loop gets extended retries
            engine_started_now = True
            # No further waiting here – attachment attempts below handle retry logic while the
            # engine finishes booting.
        else:
            raise typer.Exit(1)

    # Retrieve SSH public key (required for authorised_keys provisioning)
    try:
        public_key = get_ssh_public_key()
    except FileNotFoundError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)

    console.print(f"Attaching studio to engine [cyan]{engine['name']}[/cyan]...")

    # Determine retry strategy based on whether we just started the engine
    if engine_started_now:
        max_attempts = 40  # About 7 minutes total with exponential backoff
        base_delay = 8
        max_delay = 20
    else:
        max_attempts = 15  # About 2 minutes total with exponential backoff
        base_delay = 5
        max_delay = 10

    # Unified retry loop with exponential backoff
    with Progress(
        SpinnerColumn(),
        TimeElapsedColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as prog:
        desc = (
            "Attaching studio (engine is still booting)…"
            if engine_started_now
            else "Attaching studio…"
        )
        task = prog.add_task(desc, total=None)

        consecutive_not_ready = 0
        last_error = None

        for attempt in range(max_attempts):
            # Check if the attach already completed
            if _is_studio_attached(studio["studio_id"], engine["instance_id"]):
                success = True
                break

            success, error_msg = _attempt_studio_attach(
                studio, engine, target_user, public_key
            )

            if success:
                break  # success!

            if error_msg:
                # Fatal error – bubble up immediately
                console.print(f"[red]❌ Failed to attach studio: {error_msg}[/red]")

                # Suggest repair command if engine seems broken
                if "not ready" in error_msg.lower() and attempt > 5:
                    console.print(
                        f"\n[yellow]Engine may be in a bad state. Try:[/yellow]"
                    )
                    console.print(f"[dim]  dh engine repair {engine['name']}[/dim]")
                return

            # Track consecutive "not ready" responses
            consecutive_not_ready += 1
            last_error = "Engine not ready"

            # Update progress display
            if attempt % 3 == 0:
                prog.update(
                    task,
                    description=f"{desc} attempt {attempt+1}/{max_attempts}",
                )

            # If engine seems stuck after many attempts, show a hint
            if consecutive_not_ready > 10 and attempt == 10:
                console.print(
                    "[yellow]Engine is taking longer than expected to become ready.[/yellow]"
                )
                console.print(
                    "[dim]This can happen after GAMI creation or if the engine is still bootstrapping.[/dim]"
                )

            # Exponential backoff with jitter
            delay = min(base_delay * (1.5 ** min(attempt, 5)), max_delay)
            delay += time.time() % 2  # Add 0-2 seconds of jitter
            time.sleep(delay)

        else:
            # All attempts exhausted
            console.print(
                f"[yellow]Engine is not becoming ready after {max_attempts} attempts.[/yellow]"
            )
            if last_error:
                console.print(f"[dim]Last issue: {last_error}[/dim]")
            console.print("\n[yellow]You can try:[/yellow]")
            console.print(
                f"  1. Wait a minute and retry: [cyan]dh studio attach {engine['name']}[/cyan]"
            )
            console.print(
                f"  2. Check engine status: [cyan]dh engine status {engine['name']}[/cyan]"
            )
            console.print(
                f"  3. Repair the engine: [cyan]dh engine repair {engine['name']}[/cyan]"
            )
            return

    # Successful attach path
    console.print(f"[green]✓ Studio attached successfully![/green]")

    # Update SSH config - use target_user for the connection
    update_ssh_config_entry(engine["name"], engine["instance_id"], target_user)
    console.print(f"[green]✓ SSH config updated[/green]")
    console.print(f"\nConnect with: [cyan]ssh {engine['name']}[/cyan]")
    console.print(f"Files are at: [cyan]/studios/{target_user}[/cyan]")


def _is_studio_attached(target_studio_id: str, target_vm_id: str) -> bool:
    """Check if a studio is attached to a specific VM."""
    response = make_api_request("GET", "/studios")
    if response.status_code != 200:
        return False

    studios = response.json().get("studios", [])
    for studio in studios:
        if (
            studio["studio_id"] == target_studio_id
            and studio.get("attached_vm_id") == target_vm_id
            and studio.get("status") == "in-use"
        ):
            return True
    return False


def _attempt_studio_attach(studio, engine, target_user, public_key):
    response = make_api_request(
        "POST",
        f"/studios/{studio['studio_id']}/attach",
        json_data={
            "vm_id": engine["instance_id"],
            "user": target_user,
            "public_key": public_key,
        },
    )

    # Fast-path success
    if response.status_code == 200:
        return True, None

    # Asynchronous path – API returned 202 Accepted and operation tracking ID
    if response.status_code == 202:
        # The operation status polling is broken in the Lambda, so we just
        # wait and check if the studio is actually attached
        time.sleep(5)  # Give the async operation a moment to start

        # Check periodically if the studio is attached
        for check in range(20):  # Check for up to 60 seconds
            if _is_studio_attached(studio["studio_id"], engine["instance_id"]):
                return True, None
            time.sleep(3)

        # If we get here, attachment didn't complete in reasonable time
        return False, None  # Return None to trigger retry

    # --- determine if we should retry ---
    recoverable = False
    error_text = response.json().get("error", "Unknown error")
    err_msg = error_text.lower()

    # Check for "Studio is not available (status: in-use)" which means it's already attached
    if (
        response.status_code == 400
        and "not available" in err_msg
        and "in-use" in err_msg
    ):
        # Studio is already attached somewhere - check if it's to THIS engine
        if _is_studio_attached(studio["studio_id"], engine["instance_id"]):
            return True, None  # It's attached to our target engine - success!
        else:
            return False, error_text  # It's attached elsewhere - fatal error

    if response.status_code in (409, 503):
        recoverable = True
    else:
        RECOVERABLE_PATTERNS = [
            "not ready",
            "still starting",
            "initializing",
            "failed to mount",
            "device busy",
            "pending",  # VM state pending
        ]
        FATAL_PATTERNS = [
            "permission",
        ]
        if any(p in err_msg for p in FATAL_PATTERNS):
            recoverable = False
        elif any(p in err_msg for p in RECOVERABLE_PATTERNS):
            recoverable = True

    if not recoverable:
        # fatal – abort immediately
        return False, error_text

    # recoverable – signal caller to retry without treating as error
    return False, None
