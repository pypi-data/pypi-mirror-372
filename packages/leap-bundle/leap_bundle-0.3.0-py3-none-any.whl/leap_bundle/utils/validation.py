"""Validation utilities for leap-bundle directory validation."""

import json
import os
from pathlib import Path
from typing import Callable, List

MAX_FILE_SIZE_GB = 10.0
MAX_DIRECTORY_SIZE_GB = 10.0

# Allowed model types are tracked in:
# https://github.com/Liquid4All/liquid_executorch/blob/main/docker-images/x86_64-exporter/entrypoint#L51-L56
ALLOWED_TYPES = ["qwen3", "lfm2", "lfm2-vl"]


class ValidationError(Exception):
    """Exception raised when directory validation fails."""

    pass


def validate_config_json_exists(directory_path: Path) -> None:
    """Check that config.json exists in the directory."""
    config_path = directory_path / "config.json"
    if not config_path.exists():
        raise ValidationError("No config.json found in directory.")


def validate_safetensors_files_exist(directory_path: Path) -> None:
    """Check that one or more .safetensors files exist in the directory."""
    safetensors_files = [
        f
        for f in directory_path.glob("**/*.safetensors")
        if not any(part.startswith(".") for part in f.parts)
    ]
    if not safetensors_files:
        raise ValidationError("No .safetensors files found in directory")


def validate_file_sizes(
    directory_path: Path, max_size_gb: float = MAX_FILE_SIZE_GB
) -> None:
    """Check that each file is less than the specified size limit."""
    max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)

    for root, dirnames, filenames in os.walk(directory_path):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            if filename.startswith("."):
                continue
            file_path = Path(root) / filename
            file_size = file_path.stat().st_size
            if file_size > max_size_bytes:
                file_size_gb = file_size / (1024 * 1024 * 1024)
                relative_path = file_path.relative_to(directory_path)
                raise ValidationError(
                    f"File {relative_path} is {file_size_gb:.1f}GB, "
                    f"which exceeds the {max_size_gb}GB limit"
                )


def validate_directory_size(
    directory_path: Path, max_size_gb: float = MAX_DIRECTORY_SIZE_GB
) -> None:
    """Check that the total directory size is less than the specified limit."""
    max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)
    total_size = 0

    for root, dirnames, filenames in os.walk(directory_path):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            if filename.startswith("."):
                continue
            file_path = Path(root) / filename
            total_size += file_path.stat().st_size

    if total_size > max_size_bytes:
        total_size_gb = total_size / (1024 * 1024 * 1024)
        raise ValidationError(
            f"Directory total size is {total_size_gb:.1f}GB, "
            f"which exceeds the {max_size_gb}GB limit"
        )


def validate_model_type(directory_path: Path) -> None:
    """Check that config.json contains a valid model_type field."""
    config_path = directory_path / "config.json"

    try:
        with open(config_path, encoding="utf-8") as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in config.json: {e}") from e
    except Exception as e:
        raise ValidationError(f"Failed to read config.json: {e}") from e

    if not isinstance(config_data, dict):
        raise ValidationError("The config.json file must contain a JSON object")

    model_type = config_data.get("model_type")
    if model_type is None:
        raise ValidationError("The config.json file must contain a 'model_type' field")

    if model_type not in ALLOWED_TYPES:
        raise ValidationError(
            f"model_type '{model_type}' is not supported. "
            f"Allowed types: {', '.join(ALLOWED_TYPES)}"
        )


VALIDATION_FUNCTIONS: List[Callable[[Path], None]] = [
    validate_config_json_exists,
    validate_safetensors_files_exist,
    validate_file_sizes,
    validate_directory_size,
    validate_model_type,
]


def validate_directory(directory_path: Path) -> None:
    """Run all validation checks on the directory."""
    for validation_func in VALIDATION_FUNCTIONS:
        validation_func(directory_path)
