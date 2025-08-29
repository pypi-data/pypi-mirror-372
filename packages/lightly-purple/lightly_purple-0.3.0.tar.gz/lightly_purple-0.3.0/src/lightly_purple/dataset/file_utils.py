"""File manipulation utilities."""

from __future__ import annotations

import shutil
from pathlib import Path

import requests
import xxhash


def download_file_if_does_not_exist(url: str, local_filename: Path) -> None:
    """Download a file from a URL if it does not already exist locally."""
    if local_filename.exists():
        return
    with requests.get(url, stream=True) as r, open(local_filename, "wb") as f:
        shutil.copyfileobj(r.raw, f)


def get_file_xxhash(file_path: Path) -> str:
    """Calculate the xxhash of a file.

    XXHash is a fast non-cryptographic hash function.

    Args:
        file_path: Path to the file.

    Returns:
        The xxhash of the file as a string.
    """
    hasher = xxhash.xxh64()
    with file_path.open("rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()
