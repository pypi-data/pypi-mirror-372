"""Cat command implementation with comprehensive file handling and safety mechanisms."""

import os
import glob
import fnmatch
from pathlib import Path
from typing import List, Optional, Tuple, Set

from .config import Config
from .utils import format_header, get_file_size, is_text_file


def collect_files(patterns: List[str], exclude_patterns: List[str] = None, base_path: Path = None) -> List[Path]:
    """Collect files matching patterns, excluding those matching exclude patterns."""
    if base_path is None:
        base_path = Path.cwd()
    
    exclude_patterns = exclude_patterns or []
    files = set()
    
    # Change to base directory for glob operations
    original_cwd = Path.cwd()
    try:
        os.chdir(base_path)
        
        # Collect files matching include patterns
        for pattern in patterns:
            # Handle special case for current directory
            if pattern == ".":
                pattern = "*"
            
            try:
                # Use glob.glob with recursive=True for ** patterns
                matches = glob.glob(pattern, recursive=True)
                
                for match_str in matches:
                    match_path = Path(match_str)
                    if match_path.is_file():
                        # Convert to absolute path relative to base_path
                        abs_path = (base_path / match_path).resolve()
                        files.add(abs_path)
                        
            except Exception as e:
                # Skip invalid patterns gracefully
                print(f"Warning: Could not process pattern '{pattern}': {e}")
                continue
        
        # Filter out excluded files
        if exclude_patterns:
            files = _filter_excluded_files(files, exclude_patterns, base_path)
        
    finally:
        # Always restore original working directory
        os.chdir(original_cwd)
    
    return sorted(list(files))


def _filter_excluded_files(files: Set[Path], exclude_patterns: List[str], base_path: Path) -> Set[Path]:
    """Filter out files matching exclude patterns."""
    excluded_files = set()
    
    for exclude_pattern in exclude_patterns:
        try:
            # Get all paths matching the exclude pattern
            exclude_matches = glob.glob(exclude_pattern, recursive=True)
            
            for exclude_match_str in exclude_matches:
                exclude_path = (base_path / exclude_match_str).resolve()
                
                if exclude_path.is_file():
                    excluded_files.add(exclude_path)
                elif exclude_path.is_dir():
                    # Exclude all files within the directory
                    for file_path in files.copy():
                        try:
                            # Check if file is within excluded directory
                            file_path.relative_to(exclude_path)
                            excluded_files.add(file_path)
                        except ValueError:
                            # file_path is not within exclude_path, skip
                            continue
            
            # Also handle exclude patterns that match files directly
            for file_path in files.copy():
                try:
                    # Convert absolute path back to relative for pattern matching
                    relative_path = file_path.relative_to(base_path)
                    relative_str = str(relative_path).replace('\\', '/')  # Normalize separators
                    
                    # Use fnmatch for shell-style pattern matching
                    if fnmatch.fnmatch(relative_str, exclude_pattern):
                        excluded_files.add(file_path)
                    # Also check just the filename
                    elif fnmatch.fnmatch(relative_path.name, exclude_pattern):
                        excluded_files.add(file_path)
                        
                except ValueError:
                    # file_path is not relative to base_path, skip
                    continue
                    
        except Exception as e:
            print(f"Warning: Could not process exclude pattern '{exclude_pattern}': {e}")
            continue
    
    return files - excluded_files


class CatGenerator:
    """Generate concatenated file contents with comprehensive safety mechanisms."""

    def __init__(self, config: Config):
        self.config = config

    def generate(
        self,
        patterns: List[str],
        exclude_patterns: List[str] = None,
        header_format: str = None,
        show_headers: bool = True,
        max_file_size: str = None,
        max_lines: int = None,
        max_output: str = None,
        truncate_mode: str = "head",
        base_path: Path = None,
    ) -> str:
        """Generate concatenated file contents with safety limits and truncation."""

        if base_path is None:
            base_path = Path.cwd()

        # Handle default patterns - if no patterns provided, show all files recursively
        if not patterns:
            patterns = ["**/*"]

        # Get configuration values with defaults
        header_format = header_format or self.config.get("header_format", "=== {path} ===")
        max_size_str = max_file_size or self.config.get("max_file_size", "")
        
        # Parse size limits
        try:
            max_size_bytes = self.config.parse_size(max_size_str)
        except (ValueError, TypeError):
            max_size_bytes = float("inf")

        # Parse max output size
        max_output_str = max_output or self.config.get("max_output", "")
        try:
            max_output_bytes = self.config.parse_size(max_output_str)
        except (ValueError, TypeError):
            max_output_bytes = float("inf")

        # Get default max_lines from config
        max_lines = max_lines or self.config.get("max_lines", None)

        # Collect files using the improved glob-based function
        try:
            files = collect_files(patterns, exclude_patterns, base_path)
        except Exception as e:
            return f"Error collecting files: {e}"

        if not files:
            return "No files found matching the specified patterns."

        # Process files with safety limits
        output_lines = []
        processed_count = 0
        total_output_size = 0
        skipped_files = {"binary": 0, "too_large": 0, "errors": 0}

        for file_path in files:
            try:
                # Check if we've exceeded total output limit
                if total_output_size > max_output_bytes:
                    output_lines.append(f"\n[Output limit exceeded ({self._format_size(max_output_bytes)}), stopping...]")
                    break

                # Check file size
                file_size = get_file_size(file_path)
                if file_size > max_size_bytes:
                    if show_headers:
                        header = format_header(header_format, file_path, base_path)
                        output_lines.append(header)
                    output_lines.append(f"[File too large: {self._format_size(file_size)}, skipped]")
                    output_lines.append("")
                    skipped_files["too_large"] += 1
                    continue

                # Check if file is text
                if not is_text_file(file_path):
                    if show_headers:
                        header = format_header(header_format, file_path, base_path)
                        output_lines.append(header)
                    output_lines.append("[Binary file, skipped]")
                    output_lines.append("")
                    skipped_files["binary"] += 1
                    continue

                # Add header
                if show_headers:
                    header = format_header(header_format, file_path, base_path)
                    output_lines.append(header)

                # Add file content with smart truncation
                try:
                    content, was_truncated = self._read_file_content(
                        file_path, max_lines, truncate_mode
                    )
                    
                    if content:
                        output_lines.append(content)
                        if was_truncated:
                            truncation_info = self._get_truncation_info(file_path, max_lines, truncate_mode)
                            output_lines.append(f"[{truncation_info}]")
                        
                        processed_count += 1
                        
                        # Track output size (rough estimate)
                        total_output_size += len(content.encode('utf-8'))
                    else:
                        output_lines.append("[Empty file]")
                        processed_count += 1
                    
                except (IOError, OSError, UnicodeDecodeError) as e:
                    output_lines.append(f"[Error reading file: {e}]")
                    skipped_files["errors"] += 1

                # Add separator between files (but not after the last file)
                output_lines.append("")

            except Exception as e:
                output_lines.append(f"[Error processing {file_path}: {e}]")
                output_lines.append("")
                skipped_files["errors"] += 1

        # Generate summary
        if processed_count == 0:
            reasons = []
            if skipped_files["binary"] > 0:
                reasons.append(f"{skipped_files['binary']} binary")
            if skipped_files["too_large"] > 0:
                reasons.append(f"{skipped_files['too_large']} too large")
            if skipped_files["errors"] > 0:
                reasons.append(f"{skipped_files['errors']} errors")
            
            reason_str = ", ".join(reasons) if reasons else "unknown reasons"
            return f"No files could be processed (skipped: {reason_str})."

        # Remove the last empty line if present
        if output_lines and output_lines[-1] == "":
            output_lines.pop()

        # Add summary if files were skipped
        if any(skipped_files.values()):
            total_skipped = sum(skipped_files.values())
            summary_parts = []
            if skipped_files["binary"] > 0:
                summary_parts.append(f"{skipped_files['binary']} binary")
            if skipped_files["too_large"] > 0:
                summary_parts.append(f"{skipped_files['too_large']} too large")
            if skipped_files["errors"] > 0:
                summary_parts.append(f"{skipped_files['errors']} errors")
            
            summary = f"Processed {processed_count} files, skipped {total_skipped} ({', '.join(summary_parts)})"
            output_lines.append("")
            output_lines.append(f"[{summary}]")

        return "\n".join(output_lines)

    def _read_file_content(self, file_path: Path, max_lines: int = None, truncate_mode: str = "head") -> Tuple[str, bool]:
        """Read file content with smart truncation options."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                if max_lines is None:
                    content = f.read().rstrip()
                    return content, False
                
                lines = f.readlines()
                total_lines = len(lines)
                
                if total_lines <= max_lines:
                    content = ''.join(lines).rstrip()
                    return content, False
                
                # Apply truncation based on mode
                if truncate_mode == "head":
                    selected_lines = lines[:max_lines]
                elif truncate_mode == "tail":
                    selected_lines = lines[-max_lines:]
                elif truncate_mode == "middle":
                    # Show half from start, half from end with separator
                    half = max_lines // 2
                    remaining = max_lines - half
                    separator = ["...\n[middle content omitted]\n...\n"]
                    selected_lines = lines[:half] + separator + lines[-remaining:]
                else:
                    # Default to head if invalid mode
                    selected_lines = lines[:max_lines]
                
                content = ''.join(selected_lines).rstrip()
                return content, True
                
        except Exception as e:
            return f"[Error reading file: {e}]", False

    def _get_truncation_info(self, file_path: Path, max_lines: int, truncate_mode: str) -> str:
        """Get truncation information message."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                total_lines = sum(1 for _ in f)
            
            if truncate_mode == "head":
                return f"Truncated: showing first {max_lines} of {total_lines} lines"
            elif truncate_mode == "tail":
                return f"Truncated: showing last {max_lines} of {total_lines} lines"
            elif truncate_mode == "middle":
                return f"Truncated: showing first/last {max_lines} of {total_lines} lines"
            else:
                return f"Truncated: showing {max_lines} of {total_lines} lines"
        except:
            return f"Truncated: showing {max_lines} lines"

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == float("inf"):
            return "unlimited"
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"