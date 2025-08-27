"""List command for bundle requests."""

from typing import Optional

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from leap_bundle.types.list import (
    BundleRequestResponse,
    GetBundleRequestDetailsResponse,
    GetBundleRequestsResponse,
)
from leap_bundle.utils.api_client import APIClient
from leap_bundle.utils.config import is_logged_in

console = Console()


def display_request_details(request: BundleRequestResponse) -> None:
    """Display details for a single bundle request."""
    console.print("[green]✓[/green] Request Details:")
    console.print(f"  ID:         {request.external_id}")
    console.print(f"  Input Path: {request.input_path}")
    console.print(f"  Status:     {request.status}")
    console.print(f"  Creation:   {request.created_at}")
    console.print(
        f"  Update:     {request.created_at}"
    )  # Note: API doesn't return updated_at
    if request.user_message:
        console.print(f"  Notes:      {request.user_message}")


def display_requests_table(requests: list[BundleRequestResponse]) -> None:
    """Display a table of bundle requests."""
    table = Table(title="Bundle Requests (50 most recent)")
    table.add_column("ID", style="cyan")
    table.add_column("Input Path", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Creation", style="blue")
    table.add_column("Notes", style="magenta")

    for request in requests:
        table.add_row(
            str(request.external_id),
            request.input_path,
            request.status,
            request.created_at,
            request.user_message or "",
        )

    console.print(table)
    console.print(f"[green]✓[/green] Found {len(requests)} bundle requests.")


def list_requests(
    request_id: Optional[str] = typer.Argument(
        None, help="Optional request ID to get details for a specific request"
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output result in JSON format for programmatic parsing (only for specific request queries)",
    ),
) -> None:
    """List bundle requests or get details for a specific request."""

    if not is_logged_in():
        console.print(
            "[red]✗[/red] You must be logged in. Run 'leap-bundle login' first."
        )
        raise typer.Exit(1)

    try:
        client = APIClient()

        if request_id:
            if not json_output:
                console.print(
                    f"[blue]ℹ[/blue] Fetching details for request {request_id}..."
                )
            raw_result = client.get_bundle_request(request_id)

            try:
                request_details_response = (
                    GetBundleRequestDetailsResponse.model_validate(raw_result)
                )
                if json_output:
                    import json

                    request_data = request_details_response.request
                    console.print(
                        json.dumps(
                            {
                                "request_id": request_data.external_id,
                                "input_path": request_data.input_path,
                                "status": request_data.status,
                                "created_at": request_data.created_at,
                                "user_message": request_data.user_message,
                            }
                        )
                    )
                else:
                    display_request_details(request_details_response.request)
            except ValidationError as e:
                if json_output:
                    import json

                    console.print(
                        json.dumps(
                            {"error": f"Invalid response format from server: {e}"}
                        )
                    )
                else:
                    console.print("[red]✗[/red] Invalid response format from server:")
                    console.print(f"  {e}")
                raise typer.Exit(1) from None

        else:
            if json_output:
                console.print(
                    "[red]✗[/red] --json flag is only supported when querying a specific request ID"
                )
                raise typer.Exit(1)

            console.print("[blue]ℹ[/blue] Fetching bundle requests...")
            raw_result = client.list_bundle_requests()

            # Parse and validate the response
            try:
                requests_response = GetBundleRequestsResponse.model_validate(raw_result)
                requests = requests_response.requests
            except ValidationError as e:
                console.print("[red]✗[/red] Invalid response format from server:")
                console.print(f"  {e}")
                raise typer.Exit(1) from None

            if not requests:
                console.print("[yellow]⚠[/yellow] No bundle requests found.")
                return

            display_requests_table(requests)

    except Exception as e:
        from leap_bundle.utils.api_client import handle_cli_exception

        handle_cli_exception(e)
