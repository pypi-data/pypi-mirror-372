"""
Validation utilities for LeVibes
"""

import os
from pathlib import Path
from ..config import SUPPORTED_IMAGE_FORMATS


def is_valid_directory(path: str, min_images: int = 1) -> bool:
    """
    Check if a directory exists and contains enough image files.

    Args:
        path: Path to the directory
        min_images: Minimum number of images required

    Returns:
        True if directory is valid, False otherwise
    """
    if not os.path.exists(path) or not os.path.isdir(path):
        return False

    image_files = [
        file
        for file in os.listdir(path)
        if file.lower().endswith(SUPPORTED_IMAGE_FORMATS)
    ]

    return len(image_files) >= min_images


def validate_output_directory(path: str) -> bool:
    """
    Check if output directory can be created or already exists.

    Args:
        path: Path to the output directory

    Returns:
        True if directory is valid for output, False otherwise
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False
