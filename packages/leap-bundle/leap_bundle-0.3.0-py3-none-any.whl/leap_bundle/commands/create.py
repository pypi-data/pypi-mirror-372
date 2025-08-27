"""Create command for bundle requests."""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from leap_bundle.utils.api_client import APIClient, upload_directory_to_s3
from leap_bundle.utils.config import is_logged_in
from leap_bundle.utils.hash import calculate_directory_hash
from leap_bundle.utils.validation import ValidationError, validate_directory

console = Console()


# TODO: allow force recreate in the future
def create(
    input_path: str = typer.Argument(..., help="Directory path to upload"),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Perform a dry run that validates the input model path without uploading or creating a request",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output result in JSON format for programmatic parsing",
    ),
    # force_recreate: bool = typer.Option(
    #     False, "--force", help="Force recreate even if request exists"
    # ),
) -> None:
    """Create a new bundle request and upload directory."""

    if not is_logged_in():
        if json_output:
            console.print(
                json.dumps(
                    {"error": "You must be logged in. Run 'leap-bundle login' first."}
                )
            )
        else:
            console.print(
                "[red]✗[/red] You must be logged in. Run 'leap-bundle login' first."
            )
        raise typer.Exit(1)

    path = Path(input_path)
    if not path.exists():
        if json_output:
            console.print(
                json.dumps({"error": f"Directory does not exist: {input_path}"})
            )
        else:
            console.print(f"[red]✗[/red] Directory does not exist: {input_path}")
        raise typer.Exit(1)

    if not path.is_dir():
        if json_output:
            console.print(
                json.dumps({"error": f"Path is not a directory: {input_path}"})
            )
        else:
            console.print(f"[red]✗[/red] Path is not a directory: {input_path}")
        raise typer.Exit(1)

    try:
        try:
            validate_directory(path)
            if not json_output:
                console.print("[green]✓[/green] Directory validation passed")
        except ValidationError as e:
            if json_output:
                console.print(json.dumps({"error": f"Validation failed: {e}"}))
            else:
                console.print(f"[red]✗[/red] Validation failed: {e}")
            raise typer.Exit(1) from e

        if not json_output:
            console.print("[blue]ℹ[/blue] Calculating directory hash...")
        input_hash = calculate_directory_hash(str(path.absolute()))

        if dry_run:
            if json_output:
                console.print(
                    json.dumps(
                        {
                            "status": "dry_run_completed",
                            "message": "Dry run mode completed. No request is created.",
                        }
                    )
                )
            else:
                console.print(
                    "[green]✓[/green] Dry run mode completed. No request is created."
                )
            return

        client = APIClient()
        if not json_output:
            console.print("[blue]ℹ[/blue] Submitting bundle request...")

        result = client.create_bundle_request(str(path.absolute()), input_hash, False)

        if result["exists"]:
            if json_output:
                console.print(
                    json.dumps({"error": result["message"], "status": "exists"})
                )
            else:
                console.print(f"[yellow]⚠[/yellow] {result['message']}")
            return

        request_id = result["new_request_id"]
        signed_url = result["signed_url"]

        if not json_output:
            console.print(
                f"[green]✓[/green] Bundle request created with ID: {request_id}"
            )
            console.print("[blue]ℹ[/blue] Starting upload...")
        client.update_bundle_request_status(request_id, "uploading_started")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=json_output,
        ) as progress:
            task = progress.add_task("Uploading directory...", total=None)

            try:
                upload_directory_to_s3(signed_url, str(path.absolute()))
                progress.update(task, description="Upload completed!")

                client.update_bundle_request_status(request_id, "uploading_completed")
                if json_output:
                    console.print(
                        json.dumps({"request_id": request_id, "status": "success"})
                    )
                else:
                    console.print(
                        f"[green]✓[/green] Upload completed successfully! Request ID: {request_id}"
                    )

            except ConnectionError as conn_error:
                client.update_bundle_request_status(
                    request_id,
                    "uploading_failed",
                    f"Upload failed due to connection error: {str(conn_error)}",
                )
                if json_output:
                    console.print(json.dumps({"error": str(conn_error)}))
                else:
                    console.print(f"[red]✗[/red] {conn_error}")
                raise typer.Exit(1) from conn_error
            except Exception as upload_error:
                client.update_bundle_request_status(
                    request_id,
                    "uploading_failed",
                    f"Upload failed: {str(upload_error)}",
                )
                if json_output:
                    console.print(
                        json.dumps({"error": f"Upload failed: {upload_error}"})
                    )
                else:
                    console.print(f"[red]✗[/red] Upload failed: {upload_error}")
                raise typer.Exit(1) from upload_error

    except Exception as e:
        from leap_bundle.utils.api_client import handle_cli_exception

        handle_cli_exception(e, json_mode=json_output)
