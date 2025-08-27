"""Download command for bundle requests."""

from pathlib import Path
from urllib.parse import unquote, urlparse

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from leap_bundle.utils.api_client import APIClient, download_from_s3
from leap_bundle.utils.config import is_logged_in

console = Console()

doc_link_utm_params = {
    "utm_source": "leapbundle",
    "utm_medium": "cli",
}
doc_link = f"https://leap.liquid.ai/docs?{'&'.join(f'{k}={v}' for k, v in sorted(doc_link_utm_params.items()))}"


def download(
    request_id: str = typer.Argument(..., help="Bundle request ID to download"),
    output_path: str = typer.Option(
        ".", "--output-path", help="Directory path to download files to"
    ),
) -> None:
    """Download completed bundle request output."""

    if not is_logged_in():
        console.print(
            "[red]✗[/red] You must be logged in. Run 'leap-bundle login' first."
        )
        raise typer.Exit(1)

    output_dir = Path(output_path)
    if not output_dir.exists():
        console.print(f"[red]✗[/red] Output directory does not exist: {output_path}")
        raise typer.Exit(1)

    if not output_dir.is_dir():
        console.print(f"[red]✗[/red] Output path is not a directory: {output_path}")
        raise typer.Exit(1)

    try:
        client = APIClient()
        console.print(
            f"[blue]ℹ[/blue] Requesting download for bundle request {request_id}..."
        )

        result = client.download_bundle_request(request_id)
        signed_url = result["signed_url"]
        parsed_url = urlparse(signed_url)
        output_file = Path(unquote(parsed_url.path)).name
        if not output_file or output_file == "/":
            output_file = f"bundle-{request_id}.bundle"

        console.print(
            f"[green]✓[/green] Download URL obtained for request {request_id}"
        )

        console.print(f"[blue]ℹ[/blue] Download URL: {signed_url}")
        console.print(
            "[blue]ℹ[/blue] If the download fails, you can manually retry using the above URL within 10 hours."
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading bundle output...", total=None)

            try:
                download_from_s3(signed_url, str(output_file))
                progress.update(task, description="Download completed!")

                console.print(
                    f"[green]✓[/green] Download completed successfully! File saved to: {output_file}"
                )
                console.print(
                    f"[blue]ℹ[/blue] Your model bundle is ready for deployment with the LEAP Edge SDK: {doc_link}"
                )

            except Exception as download_error:
                console.print(f"[red]✗[/red] Download failed: {download_error}")
                raise typer.Exit(1) from download_error

    except Exception as e:
        from leap_bundle.utils.api_client import handle_cli_exception

        handle_cli_exception(e)
