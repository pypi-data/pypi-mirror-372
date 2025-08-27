"""API client utilities for leap-bundle."""

import socket
from typing import Any, Dict, Literal, Optional, cast
from urllib.parse import urlparse

import requests

from leap_bundle.types.create import CreateBundleRequestBody
from leap_bundle.utils.config import get_api_token, get_server_url


class APIClient:
    """Client for LEAP API interactions."""

    def __init__(self) -> None:
        self.server_url = get_server_url()
        self.api_token = get_api_token()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        if not self.api_token:
            raise ValueError(
                "No API token found. Please run 'leap-bundle login' first."
            )

        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def create_bundle_request(
        self, input_path: str, input_hash: str, force_recreate: bool = False
    ) -> Dict[str, Any]:
        """Create a new bundle request."""
        url = f"{self.server_url.rstrip('/')}/api/cli/bundle-requests"
        request_body = CreateBundleRequestBody(
            input_path=input_path, input_hash=input_hash, force_recreate=force_recreate
        )

        response = requests.post(
            url, json=request_body.model_dump(), headers=self._get_headers(), timeout=30
        )

        if response.status_code == 409:
            return {"exists": True, "message": response.json().get("error", "")}
        elif response.status_code == 200:
            return {"exists": False, **response.json()}
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get(
                    "error", f"HTTP {response.status_code} error"
                )
            except ValueError:
                error_msg = f"HTTP {response.status_code} error"
            raise requests.HTTPError(error_msg, response=response)

    def update_bundle_request_status(
        self,
        request_id: str,
        status: Literal["uploading_started", "uploading_completed", "uploading_failed"],
        user_message: Optional[str] = None,
    ) -> None:
        """Update bundle request status via PATCH endpoint.

        :param user_message: this is usually an error message in case of failure.
        """
        url = f"{self.server_url.rstrip('/')}/api/cli/bundle-requests/{request_id}"
        payload: Dict[str, Any] = {"status": status}
        if user_message:
            payload["user_message"] = user_message

        response = requests.patch(
            url, json=payload, headers=self._get_headers(), timeout=30
        )
        response.raise_for_status()

    def list_bundle_requests(self) -> Dict[str, Any]:
        """List bundle requests for the authenticated user."""
        url = f"{self.server_url.rstrip('/')}/api/cli/bundle-requests"

        response = requests.get(url, headers=self._get_headers(), timeout=30)

        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get(
                    "error", f"HTTP {response.status_code} error"
                )
            except ValueError:
                error_msg = f"HTTP {response.status_code} error"
            raise requests.HTTPError(error_msg, response=response)

        return cast(Dict[str, Any], response.json())

    def get_bundle_request(self, request_id: str) -> Dict[str, Any]:
        """Get details for a specific bundle request."""
        url = f"{self.server_url.rstrip('/')}/api/cli/bundle-requests/{request_id}"

        response = requests.get(url, headers=self._get_headers(), timeout=30)

        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get(
                    "error", f"HTTP {response.status_code} error"
                )
            except ValueError:
                error_msg = f"HTTP {response.status_code} error"
            raise requests.HTTPError(error_msg, response=response)

        return cast(Dict[str, Any], response.json())

    def download_bundle_request(self, request_id: str) -> Dict[str, Any]:
        """Get download URL for a completed bundle request."""
        url = f"{self.server_url.rstrip('/')}/api/cli/bundle-requests/{request_id}/download"

        response = requests.post(url, headers=self._get_headers(), timeout=30)

        if response.status_code != 200:
            try:
                error_data = response.json()
                error_msg = error_data.get(
                    "error", f"HTTP {response.status_code} error"
                )
            except ValueError:
                error_msg = f"HTTP {response.status_code} error"
            raise requests.HTTPError(error_msg, response=response)

        return cast(Dict[str, Any], response.json())

    def cancel_bundle_request(self, request_id: str) -> Dict[str, Any]:
        """Cancel a bundle request."""
        url = f"{self.server_url.rstrip('/')}/api/cli/bundle-requests/{request_id}"

        response = requests.delete(url, headers=self._get_headers(), timeout=30)

        if response.status_code not in [200, 404]:
            try:
                error_data = response.json()
                error_msg = error_data.get(
                    "error", f"HTTP {response.status_code} error"
                )
            except ValueError:
                error_msg = f"HTTP {response.status_code} error"
            raise requests.HTTPError(error_msg, response=response)

        result: Dict[str, Any] = response.json()
        return result

    def validate_token(self, token: str) -> bool:
        """Validate API token with the LEAP platform."""
        try:
            url = f"{self.server_url.rstrip('/')}/api/cli/login"
            response = requests.post(url, json={"api_token": token}, timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False


def upload_directory_to_s3(
    signed_url_data: Dict[str, Any], directory_path: str
) -> None:
    """Upload directory to S3 using signed URL."""
    import os
    from pathlib import Path

    path = Path(directory_path)
    url = signed_url_data["url"]
    fields = signed_url_data["fields"]

    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        if hostname:
            socket.getaddrinfo(hostname, None)
    except (socket.gaierror, OSError) as e:
        raise ConnectionError(
            f"Cannot access AWS services. Please ensure you can reach {hostname}. "
            f"Check your internet connection and DNS settings. Error: {e}"
        ) from e

    for root, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            if filename.startswith("."):
                continue
            file_path = Path(root) / filename
            relative_path = file_path.relative_to(path)

            form_data = fields.copy()
            form_data["key"] = form_data["key"].replace(
                "${filename}", str(relative_path)
            )

            with open(file_path, "rb") as f:
                files = {"file": f}
                response = requests.post(url, data=form_data, files=files, timeout=600)
                response.raise_for_status()


def extract_error_message(response: requests.Response) -> str:
    """Extract error message from HTTP response, preferring server-provided error field."""
    try:
        error_data = response.json()
        return str(error_data.get("error", f"HTTP {response.status_code} error"))
    except ValueError:
        return f"HTTP {response.status_code} error"


def handle_cli_exception(e: Exception, json_mode: bool = False) -> None:
    """Handle CLI exceptions with proper error message extraction and display."""
    import json

    import typer
    from rich.console import Console

    console = Console()

    if hasattr(e, "response") and e.response is not None:
        error_message = extract_error_message(e.response)
        if json_mode:
            console.print(json.dumps({"error": error_message}))
        else:
            console.print(f"[red]✗[/red] {error_message}")
    else:
        if json_mode:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]✗[/red] Error: {e}")
    raise typer.Exit(1) from e


def download_from_s3(signed_url: str, output_path: str) -> None:
    """Download file from S3 using signed URL."""
    from pathlib import Path

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(signed_url, timeout=300)
    response.raise_for_status()

    with open(output_file, "wb") as f:
        f.write(response.content)
