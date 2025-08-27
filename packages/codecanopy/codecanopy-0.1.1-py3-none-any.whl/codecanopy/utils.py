"""Shared utilities for CodeCanopy."""

import fnmatch
import glob
import os
from pathlib import Path
from typing import List, Set

import pathspec

def should_ignore(path: Path, ignore_patterns: List[str]) -> bool:
    """Check if path should be ignored based on patterns."""
    if not ignore_patterns:
        return False

    path_str = str(path)
    name = path.name

    # Handle relative path from current directory
    try:
        relative_path = path.relative_to(Path.cwd())
        relative_str = str(relative_path)
    except ValueError:
        relative_str = path_str

    # Create pathspec object for gitignore-style patterns
    try:
        spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns)

        # Check if path matches any ignore pattern
        if (
            spec.match_file(path_str)
            or spec.match_file(name)
            or spec.match_file(relative_str)
        ):
            return True
    except Exception:
        # Fallback to simple pattern matching if pathspec fails
        pass

    # Additional simple pattern matching
    for pattern in ignore_patterns:
        # Handle different path representations
        if (
            fnmatch.fnmatch(name, pattern)
            or fnmatch.fnmatch(path_str, pattern)
            or fnmatch.fnmatch(relative_str, pattern)
        ):
            return True

        # Handle directory patterns (e.g., "node_modules" should match "path/node_modules/")
        if pattern.endswith("/") and name == pattern[:-1]:
            return True
        if not pattern.endswith("/") and (
            name == pattern or path_str.endswith("/" + pattern)
        ):
            return True

    return False


def get_file_size(path: Path) -> int:
    """Get file size in bytes."""
    try:
        return path.stat().st_size
    except (OSError, AttributeError):
        return 0


def format_header(template: str, path: Path, base_path: Path = None) -> str:
    """Format header template with path information."""
    try:
        if base_path:
            relative_path = path.relative_to(base_path)
        else:
            relative_path = path
    except ValueError:
        # If path is not relative to base_path, use absolute path
        relative_path = path

    # Handle parent directory formatting
    parent_dir = str(relative_path.parent) if relative_path.parent != Path(".") else ""

    return template.format(
        path=str(relative_path).replace("\\", "/"),  # Normalize path separators
        filename=path.name,
        dir=parent_dir.replace("\\", "/") if parent_dir else "",
    )


def is_text_file(path: Path, max_check_bytes: int = 8192) -> bool:
    """Check if file is likely a text file."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(max_check_bytes)

            # Empty file is considered text
            if not chunk:
                return True

            # Check for null bytes (strong indicator of binary)
            if b"\0" in chunk:
                return False

            # Check for high ratio of non-printable characters
            printable_chars = sum(
                1 for byte in chunk if 32 <= byte <= 126 or byte in (9, 10, 13)
            )
            ratio = printable_chars / len(chunk)

            # If more than 95% printable characters, consider it text
            return ratio > 0.95

    except (IOError, OSError, UnicodeDecodeError):
        return False
