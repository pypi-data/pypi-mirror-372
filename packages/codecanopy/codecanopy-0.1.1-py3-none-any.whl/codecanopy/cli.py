"""Main CLI interface for CodeCanopy."""

import click
import sys
from pathlib import Path

from .config import Config
from .tree import TreeGenerator
from .cat import CatGenerator


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """CodeCanopy - Give LLMs perfect context about your codebase."""
    if ctx.invoked_subcommand is None:
        click.echo("CodeCanopy - Give LLMs perfect context about your codebase")
        click.echo("\nCommands:")
        click.echo("  tree    Show directory structure")
        click.echo("  cat     Show file contents")
        click.echo("\nUse --help with any command for more information.")


@main.command()
@click.option(
    "--focus",
    multiple=True,
    help="Focus directories (full depth). Can be used multiple times.",
)
@click.option(
    "--ignore",
    multiple=True,
    help="Ignore directories/files. Can be used multiple times.",
)
@click.option("--depth", type=int, help="Global depth limit (default: 3)")
@click.option("--no-files", is_flag=True, help="Hide files, show only directories")
@click.option("--config", help="Config file path (default: .codecanopy.json)")
@click.argument("path", required=False, default=".")
def tree(focus, ignore, depth, no_files, config, path):
    """Show directory structure with selective depth control.

    PATH: Directory to analyze (default: current directory)

    Examples:
      codecanopy tree --focus src --ignore node_modules
      codecanopy tree --depth 2 --no-files
      codecanopy tree /path/to/project --focus src,lib
    """

    try:
        # Validate path
        root_path = Path(path).resolve()
        if not root_path.exists():
            click.echo(f"Error: Path '{path}' does not exist.", err=True)
            sys.exit(1)
        if not root_path.is_dir():
            click.echo(f"Error: Path '{path}' is not a directory.", err=True)
            sys.exit(1)

        # Load configuration
        cfg = Config(config)

        # Generate tree
        generator = TreeGenerator(cfg)

        ignore_patterns = list(ignore) if ignore else None
        focus_dirs = list(focus) if focus else None

        result = generator.generate(
            root_path=root_path,
            focus_dirs=focus_dirs,
            ignore_patterns=ignore_patterns,
            global_depth=depth,
            show_files=not no_files,
        )

        click.echo(result)

    except KeyboardInterrupt:
        click.echo("\nOperation cancelled.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("patterns", nargs=-1, required=False)  # Made optional
@click.option(
    "--exclude",
    multiple=True,
    help="Exclude file patterns (adds to config excludes). Can be used multiple times.",
)
@click.option(
    "--no-ignore", 
    is_flag=True, 
    help="Ignore default excludes from config"
)
@click.option(
    "--header", help="Header format template. Available: {path}, {filename}, {dir}"
)
@click.option("--no-headers", is_flag=True, help="Skip file headers")
@click.option("--max-size", help="Skip files larger than size (e.g., 100KB, 1MB)")
@click.option(
    "--max-lines", 
    type=int, 
    help="Truncate files to max lines (per file)"
)
@click.option(
    "--max-output", 
    help="Stop processing when total output exceeds size (e.g., 10MB)"
)
@click.option(
    "--truncate-mode", 
    type=click.Choice(["head", "tail", "middle"]), 
    default="head",
    help="How to truncate large files (default: head)"
)
@click.option("--config", help="Config file path (default: .codecanopy.json)")
@click.argument(
    "base_path",
    type=click.Path(
        exists=True,       # Must exist
        file_okay=False,   # Don't allow files
        dir_okay=True,     # Allow directories only
        readable=True,     # Must be readable
        resolve_path=True, # Convert to absolute path
        path_type=Path,    # Return as pathlib.Path object
    ),
    default=".",
    required=False,
)
def cat(patterns, exclude, no_ignore, header, no_headers, max_size, max_lines, max_output, truncate_mode, config, base_path):
    """Show file contents with headers.

    PATTERNS: File patterns to include (supports glob patterns). 
              If no patterns provided, defaults to all files recursively.
    BASE_PATH: Directory to search in (defaults to current directory).

    Examples:
      codecanopy cat                        # Show all files in current directory
      codecanopy cat /path/to/project       # Show all files in specified directory
      codecanopy cat . "src/**/*.py"        # Show Python files in src/
      codecanopy cat /project "*.js" "*.ts" # Show JS/TS files in /project
      codecanopy cat . "**/*" --exclude "*test*"  # All files, exclude tests
    """

    try:
        # base_path is now automatically validated and converted by Click
        # No need for manual validation since Click handles it
        
        # Load configuration
        cfg = Config(config)

        # Handle default patterns - if no patterns provided, show all files recursively
        if not patterns:
            patterns = ["**/*"]

        # Handle exclude patterns
        if no_ignore:
            # Only use user-provided excludes
            exclude_patterns = list(exclude) if exclude else []
        else:
            # Combine config excludes with user excludes (standard behavior)
            config_excludes = cfg.get("ignore", [])
            user_excludes = list(exclude) if exclude else []
            exclude_patterns = config_excludes + user_excludes

        # Generate output
        generator = CatGenerator(cfg)

        result = generator.generate(
            patterns=list(patterns),
            exclude_patterns=exclude_patterns,
            header_format=header,
            show_headers=not no_headers,
            max_file_size=max_size,
            max_lines=max_lines,
            max_output=max_output,
            truncate_mode=truncate_mode,
            base_path=base_path,
        )

        click.echo(result)

    except KeyboardInterrupt:
        click.echo("\nOperation cancelled.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)



@main.command()
def version():
    """Show version information."""
    from . import __version__

    click.echo(f"CodeCanopy version {__version__}")


if __name__ == "__main__":
    main()
