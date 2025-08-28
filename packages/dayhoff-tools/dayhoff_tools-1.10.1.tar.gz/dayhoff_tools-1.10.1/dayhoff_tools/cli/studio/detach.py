"""Studio detach command."""

from typing import Optional

import typer
from rich.prompt import Confirm

from ..engine_studio_utils.api_utils import get_user_studio, make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console


def detach_studio(
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Detach a different user's studio (admin only)"
    ),
):
    """Detach your studio from its current engine."""
    username = check_aws_sso()

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Add confirmation when detaching another user's studio
    if target_user != username:
        console.print(f"[yellow]⚠️  Managing studio for user: {target_user}[/yellow]")
        if not Confirm.ask(f"Are you sure you want to detach {target_user}'s studio?"):
            console.print("Operation cancelled.")
            return

    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio.[/yellow]")
        else:
            console.print(f"[yellow]User {target_user} doesn't have a studio.[/yellow]")
        return

    if studio.get("status") != "in-use":
        if target_user == username:
            console.print("[yellow]Your studio is not attached to any engine.[/yellow]")
        else:
            console.print(
                f"[yellow]{target_user}'s studio is not attached to any engine.[/yellow]"
            )
        return

    console.print(f"Detaching studio from {studio.get('attached_vm_id')}...")

    response = make_api_request("POST", f"/studios/{studio['studio_id']}/detach")

    if response.status_code == 200:
        console.print(f"[green]✓ Studio detached successfully![/green]")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to detach studio: {error}[/red]")
