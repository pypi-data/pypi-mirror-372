"""
File handling utilities for LeVibes
"""

import os
import uuid
from pathlib import Path
from typing import List
from ..config import SUPPORTED_IMAGE_FORMATS


def get_image_paths(directory: str) -> List[str]:
    """
    Get all image file paths from a directory.

    Args:
        directory: Path to the directory containing images

    Returns:
        List of image file paths
    """
    return [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.lower().endswith(SUPPORTED_IMAGE_FORMATS)
    ]


def create_unique_output_dir(base_dir: str) -> str:
    """
    Create a unique output directory with UUID.

    Args:
        base_dir: Base directory path

    Returns:
        Path to the created unique directory
    """
    unique_dir = os.path.join(base_dir, str(uuid.uuid4()))
    os.makedirs(unique_dir, exist_ok=True)
    return unique_dir


def ensure_directory_exists(path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists
    """
    os.makedirs(path, exist_ok=True)
