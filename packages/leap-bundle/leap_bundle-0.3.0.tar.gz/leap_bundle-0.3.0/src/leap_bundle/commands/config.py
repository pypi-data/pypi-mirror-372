"""Configuration commands for leap-bundle."""

import typer
from rich.console import Console

from leap_bundle.utils.config import get_config_file_path, load_config, set_server_url

console = Console()
app = typer.Typer()


@app.command("config")
def config(
    server: str = typer.Option(
        None, "--server", help="Set the server URL", hidden=True
    ),
) -> None:
    """Configure leap-bundle settings."""
    if server:
        set_server_url(server)
        console.print(f"[green]✓[/green] Server URL set to: {server}")
    else:
        config_path = get_config_file_path()
        console.print(f"[blue]ℹ[/blue] Config file location: {config_path}")

        config_data = load_config()
        if config_data:
            console.print("\n[blue]Current configuration:[/blue]")
            for key, value in config_data.items():
                if key != "api_token":
                    console.print(f"  {key}: {value}")
        else:
            console.print("\n[yellow]No configuration found.[/yellow]")
