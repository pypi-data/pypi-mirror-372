"""Configuration handling for CodeCanopy."""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union


class Config:
    """Configuration management for CodeCanopy."""

    DEFAULT_CONFIG = {
        "ignore": [
            "node_modules",
            ".git",
            "dist",
            "build",
            ".next",
            "__pycache__",
            "*.egg-info",
            ".pytest_cache",
            ".mypy_cache",
        ],
        "default_depth": 3,
        "header_format": "=== {path} ===",
        "max_file_size": "100KB",
        "focus_dirs": [],
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config(config_path)

    def load_config(self, config_path: Optional[str] = None):
        """Load configuration from file."""
        if config_path is None:
            # Look for .codecanopy.json in current directory and parent directories
            current_dir = Path.cwd()
            for parent in [current_dir] + list(current_dir.parents):
                potential_config = parent / ".codecanopy.json"
                if potential_config.exists():
                    config_path = str(potential_config)
                    break

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    if isinstance(user_config, dict):
                        self.config.update(user_config)
                    else:
                        print(
                            f"Warning: Config file {config_path} does not contain a valid JSON object"
                        )
            except (json.JSONDecodeError, IOError, UnicodeDecodeError) as e:
                print(f"Warning: Could not load config file {config_path}: {e}")

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def parse_size(self, size_str: Union[str, int, None]) -> int:
        """Parse size string like '100KB' to bytes."""
        if size_str is None or size_str == "":
            return float("inf")

        if isinstance(size_str, int):
            return size_str

        if not isinstance(size_str, str):
            return float("inf")

        # Remove whitespace and convert to uppercase
        size_str = size_str.strip().upper()

        if not size_str:
            return float("inf")

        # Handle pure numbers (assume bytes)
        if size_str.isdigit():
            return int(size_str)

        # Parse size with unit
        match = re.match(r"^(\d+(?:\.\d+)?)\s*(KB|MB|GB|K|M|G|B)?$", size_str)
        if not match:
            return float("inf")

        number = float(match.group(1))
        unit = match.group(2) or "B"

        # Convert to bytes based on unit
        multipliers = {
            "B": 1,
            "K": 1024,
            "KB": 1024,
            "M": 1024 * 1024,
            "MB": 1024 * 1024,
            "G": 1024 * 1024 * 1024,
            "GB": 1024 * 1024 * 1024,
        }

        return int(number * multipliers.get(unit, 1))
