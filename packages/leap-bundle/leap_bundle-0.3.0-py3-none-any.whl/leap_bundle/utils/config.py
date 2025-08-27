"""Configuration utilities for leap-bundle."""

import os
from pathlib import Path
from typing import Optional

import yaml


def get_config_file_path() -> Path:
    """Get the path to the leap-bundle config file."""
    return Path.home() / ".liquid-leap"


def load_config() -> dict[str, str]:
    """Load configuration from the config file."""
    config_path = get_config_file_path()
    if not config_path.exists():
        return {}

    try:
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except (yaml.YAMLError, OSError):
        return {}


def save_config(config: dict[str, str]) -> None:
    """Save configuration to the config file."""
    config_path = get_config_file_path()

    config_with_version = {"version": 1, **config}

    try:
        with open(config_path, "w") as f:
            yaml.safe_dump(config_with_version, f, default_flow_style=False)

        os.chmod(config_path, 0o600)
    except OSError:
        pass


def is_logged_in() -> bool:
    """Check if the user is currently logged in."""
    config = load_config()
    return bool(config.get("api_token"))


def get_api_token() -> Optional[str]:
    """Get the stored API token."""
    config = load_config()
    return config.get("api_token")


def get_server_url() -> str:
    """Get the configured server URL."""
    config = load_config()
    return config.get("server_url", "https://leap.liquid.ai")


def set_server_url(url: str) -> None:
    """Store the server URL in the config file."""
    config_path = get_config_file_path()
    config_exists = config_path.exists()

    config = load_config()
    config["server_url"] = url
    save_config(config)

    if not config_exists:
        from rich.console import Console

        console = Console()
        console.print(f"[blue]ℹ[/blue] Config file created at: {config_path}")


def set_api_token(token: str) -> None:
    """Store the API token in the config file."""
    config_path = get_config_file_path()
    config_exists = config_path.exists()

    config = load_config()
    config["api_token"] = token
    save_config(config)

    if not config_exists:
        from rich.console import Console

        console = Console()
        console.print(f"[blue]ℹ[/blue] Config file created at: {config_path}")


def clear_api_token() -> None:
    """Remove the API token from the config file."""
    config = load_config()
    if "api_token" in config:
        del config["api_token"]
        save_config(config)
