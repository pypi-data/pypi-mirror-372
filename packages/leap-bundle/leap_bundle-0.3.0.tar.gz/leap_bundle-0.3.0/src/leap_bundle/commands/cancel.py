"""Cancel command for bundle requests."""

import typer
from rich.console import Console

from leap_bundle.utils.api_client import APIClient
from leap_bundle.utils.config import is_logged_in

console = Console()


def cancel(
    request_id: str = typer.Argument(..., help="Bundle request ID to cancel"),
) -> None:
    """Cancel a bundle request."""

    if not is_logged_in():
        console.print(
            "[red]✗[/red] You must be logged in. Run 'leap-bundle login' first."
        )
        raise typer.Exit(1)

    try:
        client = APIClient()
        console.print(f"[blue]ℹ[/blue] Cancelling bundle request {request_id}...")

        result = client.cancel_bundle_request(request_id)
        message = result.get("message", "Request cancelled successfully.")

        console.print(f"[green]✓[/green] {message}")

    except Exception as e:
        from leap_bundle.utils.api_client import handle_cli_exception

        handle_cli_exception(e)
