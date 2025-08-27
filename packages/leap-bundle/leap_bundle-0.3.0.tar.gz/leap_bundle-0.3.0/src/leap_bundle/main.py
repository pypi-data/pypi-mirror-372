"""Main entry point for the leap-bundle."""

import typer
from rich.console import Console

from leap_bundle.commands.auth import login, logout, whoami
from leap_bundle.commands.cancel import cancel
from leap_bundle.commands.config import config
from leap_bundle.commands.create import create
from leap_bundle.commands.download import download
from leap_bundle.commands.list import list_requests
from leap_bundle.commands.validate import validate

console = Console()

app = typer.Typer(
    name="leap-bundle",
    help="Command line interface for the LEAP (Liquid Edge AI Platform) platform.",
    rich_markup_mode="rich",
)


def version_callback(value: bool) -> None:
    """Show version information."""
    if value:
        from leap_bundle import __version__

        console.print(f"leap-bundle version {__version__}")
        raise typer.Exit()


def help_command(ctx: typer.Context) -> None:
    """Show help information."""
    if ctx.parent:
        console.print(ctx.parent.get_help())
    else:
        console.print("Help information not available.")


app.command("login")(login)
app.command("logout")(logout)
app.command("whoami")(whoami)
app.command("cancel")(cancel)
app.command("config")(config)
app.command("create")(create)
app.command("download")(download)
app.command("list")(list_requests)
app.command("validate")(validate)
app.command("help")(help_command)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """leap-bundle - Command line interface for the LEAP platform."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


if __name__ == "__main__":
    app()
