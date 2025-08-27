"""Authentication commands for leap-bundle."""

import requests
import typer
from rich.console import Console

from leap_bundle.utils.config import (
    clear_api_token,
    get_api_token,
    get_server_url,
    is_logged_in,
    set_api_token,
)

console = Console()
app = typer.Typer()


def validate_api_token(token: str) -> bool:
    """Validate API token with the LEAP platform."""
    try:
        server_url = get_server_url()
        api_url = f"{server_url.rstrip('/')}/api/cli/login"
        response = requests.post(api_url, json={"api_token": token}, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        console.print(f"[red]✗[/red] Failed to validate API token: {e}")
        return False


@app.command("login")
def login(
    api_token: str = typer.Argument(..., help="API token for LEAP platform"),
) -> None:
    """Login to LEAP platform."""
    if is_logged_in():
        current_token = get_api_token()

        if current_token == api_token:
            console.print(
                "[yellow]⚠[/yellow] You are already logged in with the same API token."
            )
            return
        else:
            console.print(
                "[yellow]⚠[/yellow] You are already logged in with a different API token."
            )
            if not typer.confirm(
                "Do you want to log out and log in with the new token?"
            ):
                console.print("[blue]ℹ[/blue] Login cancelled.")
                return

            clear_api_token()

    console.print("[blue]ℹ[/blue] Validating API token...")
    if not validate_api_token(api_token):
        console.print(
            "[red]✗[/red] Invalid API token. Please check your token and try again."
        )
        raise typer.Exit(1)

    try:
        set_api_token(api_token)
        console.print("[green]✓[/green] Successfully logged in to LEAP platform!")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to save login credentials: {e}")
        raise typer.Exit(1) from None


@app.command("logout")
def logout() -> None:
    """Logout from LEAP platform."""
    if not is_logged_in():
        console.print("[blue]ℹ[/blue] You are not currently logged in.")
        return

    try:
        clear_api_token()
        console.print("[green]✓[/green] Successfully logged out from LEAP platform!")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to clear login credentials: {e}")
        raise typer.Exit(1) from None


@app.command("whoami")
def whoami() -> None:
    """Show current user information."""
    if not is_logged_in():
        console.print(
            "[red]✗[/red] You are not logged in. Run 'leap-bundle login' first."
        )
        raise typer.Exit(1)

    try:
        api_token = get_api_token()
        server_url = get_server_url()
        api_url = f"{server_url.rstrip('/')}/api/cli/whoami"

        response = requests.get(
            api_url, headers={"Authorization": f"Bearer {api_token}"}, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            console.print(f"[green]✓[/green] Logged in as: {data['email']}")
        else:
            error_data = (
                response.json()
                if response.headers.get("content-type", "").startswith(
                    "application/json"
                )
                else {}
            )
            error_message = error_data.get("error", "Failed to get user information")
            console.print(f"[red]✗[/red] {error_message}")
            raise typer.Exit(1)
    except requests.RequestException as e:
        console.print(f"[red]✗[/red] Failed to connect to server: {e}")
        raise typer.Exit(1) from None
    except typer.Exit:
        raise  # Re-raise typer.Exit without handling it
    except Exception as e:
        console.print(f"[red]✗[/red] Unexpected error: {e}")
        raise typer.Exit(1) from None
