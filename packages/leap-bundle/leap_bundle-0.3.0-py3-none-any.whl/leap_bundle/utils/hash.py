"""Hashing utilities for leap-bundle."""

import hashlib
import os
from pathlib import Path
from typing import List


def calculate_directory_hash(directory_path: str) -> str:
    """Calculate SHA256 hash of all files in a directory."""
    path = Path(directory_path)
    if not path.exists() or not path.is_dir():
        raise ValueError(f"Directory does not exist: {directory_path}")

    files: List[Path] = []
    for root, dirnames, filenames in os.walk(path):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            if filename.startswith("."):
                continue
            files.append(Path(root) / filename)

    files.sort()

    hasher = hashlib.sha256()
    for file_path in files:
        relative_path = file_path.relative_to(path)
        hasher.update(str(relative_path).encode("utf-8"))

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

    return hasher.hexdigest()
