"""Tree command implementation."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set

from .config import Config
from .utils import should_ignore


class TreeGenerator:
    """Generate directory tree structure."""

    def __init__(self, config: Config):
        self.config = config

    def generate(
        self,
        root_path: Path = None,
        focus_dirs: List[str] = None,
        ignore_patterns: List[str] = None,
        global_depth: int = None,
        show_files: bool = False,
    ) -> str:
        """Generate tree structure."""

        if root_path is None:
            root_path = Path.cwd()

        focus_dirs = focus_dirs or self.config.get("focus_dirs", [])
        ignore_patterns = ignore_patterns or self.config.get("ignore", [])
        global_depth = global_depth or self.config.get("default_depth", 3)

        # Convert focus_dirs to set of Path objects - handle both relative and absolute paths
        focus_paths = set()
        for focus_dir in focus_dirs:
            if os.path.isabs(focus_dir):
                focus_path = Path(focus_dir)
            else:
                focus_path = root_path / focus_dir

            if focus_path.exists() and focus_path.is_dir():
                focus_paths.add(focus_path.resolve())

        lines = []
        lines.append(f"{root_path.name}/")

        self._generate_tree_recursive(
            root_path,
            lines,
            "",
            focus_paths,
            ignore_patterns,
            global_depth,
            show_files,
            current_depth=0,
        )

        return "\n".join(lines)

    def _generate_tree_recursive(
        self,
        path: Path,
        lines: List[str],
        prefix: str,
        focus_paths: Set[Path],
        ignore_patterns: List[str],
        global_depth: int,
        show_files: bool,
        current_depth: int = 0,
    ):
        """Recursively generate tree structure."""

        # Determine depth limit for this path
        path_resolved = path.resolve()
        is_focused = self._is_path_focused(path_resolved, focus_paths)

        if is_focused:
            depth_limit = float("inf")  # No limit for focused directories
        else:
            depth_limit = global_depth

        if current_depth >= depth_limit:
            return

        try:
            entries = list(path.iterdir())
        except (PermissionError, OSError):
            return

        # Filter out ignored entries
        filtered_entries = []
        for entry in entries:
            if not should_ignore(entry, ignore_patterns):
                filtered_entries.append(entry)

        # Separate directories and files
        directories = [entry for entry in filtered_entries if entry.is_dir()]
        files = (
            [entry for entry in filtered_entries if entry.is_file()]
            if show_files
            else []
        )

        # Sort entries
        directories.sort(key=lambda x: x.name.lower())
        files.sort(key=lambda x: x.name.lower())

        all_entries = directories + files

        for i, entry in enumerate(all_entries):
            is_last_entry = i == len(all_entries) - 1

            # Determine the tree symbols
            if is_last_entry:
                current_prefix = "└── "
                next_prefix = prefix + "    "
            else:
                current_prefix = "├── "
                next_prefix = prefix + "│   "

            # Add focus indicator
            focus_indicator = ""
            if entry.is_dir():
                entry_resolved = entry.resolve()
                if self._is_path_focused(entry_resolved, focus_paths):
                    focus_indicator = "  [focused]"
                elif current_depth + 1 >= global_depth and not is_focused:
                    focus_indicator = f"  [depth: {global_depth}]"

            # Add trailing slash for directories
            entry_display = f"{entry.name}/" if entry.is_dir() else entry.name
            lines.append(f"{prefix}{current_prefix}{entry_display}{focus_indicator}")

            # Recurse into directories
            if entry.is_dir():
                self._generate_tree_recursive(
                    entry,
                    lines,
                    next_prefix,
                    focus_paths,
                    ignore_patterns,
                    global_depth,
                    show_files,
                    current_depth + 1,
                )

    def _is_path_focused(self, path_resolved: Path, focus_paths: Set[Path]) -> bool:
        """Check if a path is focused or contains a focused path."""
        for focus_path in focus_paths:
            # Check if path is exactly a focus path
            if path_resolved == focus_path:
                return True
            # Check if path is a parent of a focus path
            try:
                focus_path.relative_to(path_resolved)
                return True
            except ValueError:
                continue
        return False
