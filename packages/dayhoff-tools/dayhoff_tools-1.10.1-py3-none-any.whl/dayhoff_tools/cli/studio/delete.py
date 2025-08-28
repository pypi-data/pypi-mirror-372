"""Studio delete command."""

from typing import Optional

import typer
from rich.prompt import Confirm, Prompt

from ..engine_studio_utils.api_utils import get_user_studio, make_api_request
from ..engine_studio_utils.aws_utils import check_aws_sso
from ..engine_studio_utils.constants import console


def delete_studio(
    user: Optional[str] = typer.Option(
        None, "--user", "-u", help="Delete a different user's studio (admin only)"
    ),
):
    """Delete your studio permanently."""
    username = check_aws_sso()

    # Use specified user if provided, otherwise use current user
    target_user = user if user else username

    # Extra warning when deleting another user's studio
    if target_user != username:
        console.print(
            f"[red]⚠️  ADMIN ACTION: Deleting studio for user: {target_user}[/red]"
        )

    studio = get_user_studio(target_user)
    if not studio:
        if target_user == username:
            console.print("[yellow]You don't have a studio to delete.[/yellow]")
        else:
            console.print(
                f"[yellow]User {target_user} doesn't have a studio to delete.[/yellow]"
            )
        return

    console.print(
        "[red]⚠️  WARNING: This will permanently delete the studio and all data![/red]"
    )
    console.print(f"Studio ID: {studio['studio_id']}")
    console.print(f"User: {target_user}")
    console.print(f"Size: {studio['size_gb']}GB")

    # Multiple confirmations
    if not Confirm.ask(
        f"\nAre you sure you want to delete {target_user}'s studio?"
        if target_user != username
        else "\nAre you sure you want to delete your studio?"
    ):
        console.print("Deletion cancelled.")
        return

    if not Confirm.ask("[red]This action cannot be undone. Continue?[/red]"):
        console.print("Deletion cancelled.")
        return

    typed_confirm = Prompt.ask('Type "DELETE" to confirm permanent deletion')
    if typed_confirm != "DELETE":
        console.print("Deletion cancelled.")
        return

    response = make_api_request("DELETE", f"/studios/{studio['studio_id']}")

    if response.status_code == 200:
        console.print(f"[green]✓ Studio deleted successfully![/green]")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to delete studio: {error}[/red]")
