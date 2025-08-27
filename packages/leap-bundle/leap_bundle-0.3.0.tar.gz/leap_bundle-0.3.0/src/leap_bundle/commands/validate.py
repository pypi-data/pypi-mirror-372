"""Validate command for directory validation."""

from pathlib import Path

import typer
from rich.console import Console

from leap_bundle.utils.validation import ValidationError, validate_directory

console = Console()


def validate(
    input_path: str = typer.Argument(..., help="Directory path to validate"),
) -> None:
    """Validate a directory for bundle creation without creating a request."""

    path = Path(input_path)
    if not path.exists():
        console.print(f"[red]✗[/red] Directory does not exist: {input_path}")
        raise typer.Exit(1)

    if not path.is_dir():
        console.print(f"[red]✗[/red] Path is not a directory: {input_path}")
        raise typer.Exit(1)

    try:
        validate_directory(path)
        console.print("[green]✓[/green] Directory validation passed")
        console.print("[green]✓[/green] Directory is ready for bundle creation")
    except ValidationError as e:
        console.print(f"[red]✗[/red] Validation failed: {e}")
        raise typer.Exit(1) from e
