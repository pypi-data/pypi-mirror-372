"""Check command for human usage with batch processing."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from zenable_mcp.exit_codes import ExitCode
from zenable_mcp.ide_context import IDEContextDetector, IDEType
from zenable_mcp.utils.files import (
    expand_file_patterns,
    get_relative_paths,
)
from zenable_mcp.utils.mcp_client import (
    ZenableMCPClient,
    parse_conformance_results,
)
from zenable_mcp.utils.zenable_config import filter_files_by_zenable_config

logger = logging.getLogger(__name__)


def detect_files_from_ide_context(base_path: Optional[Path]) -> list[Path]:
    """
    Auto-detect files from IDE context when no patterns are provided.

    Returns:
        List of file paths detected from IDE context
    """
    detector = IDEContextDetector()
    ide_type = detector.detect_context()

    if ide_type.value != "unknown":
        logger.info(f"Detected {ide_type.value} IDE context")

    env_files = detector.get_file_paths()
    if not env_files:
        logger.info("No files detected from IDE context. This could mean:")
        logger.info("  1. No modified files in the git repository")
        logger.info("  2. All modified files are filtered by .gitignore")
        logger.info("  3. All modified files are filtered by Zenable config")
        logger.info("  4. Not in a git repository")
        click.echo(
            "Error: No files specified and none detected from IDE context", err=True
        )
        click.echo(
            "Please provide file patterns or check from a git repository", err=True
        )
        sys.exit(ExitCode.NO_FILES_SPECIFIED)

    # Check if we're using the fallback mechanism (most recently edited file)
    if ide_type == IDEType.UNKNOWN:
        logger.info(
            f"Auto-detected {len(env_files)} file(s) using the fallback mechanism of last modified file"
        )
        # Files are already filtered by zenable config in the fallback mechanism
        file_paths = []
        for file_str in env_files:
            file_path = Path(file_str)
            if file_path.exists():
                file_paths.append(file_path)
            else:
                click.echo(
                    f"Warning: File from IDE context not found: {file_str}",
                    err=True,
                )
        return file_paths
    else:
        logger.info(
            f"Auto-detected {len(env_files)} file(s) from {ide_type.value} IDE context"
        )
        # Convert environment file paths to Path objects
        env_file_paths = []
        for file_str in env_files:
            file_path = Path(file_str)
            if file_path.exists():
                env_file_paths.append(file_path)
            else:
                click.echo(
                    f"Warning: File from IDE context not found: {file_str}",
                    err=True,
                )

        # Filter based on zenable config using the shared utility
        files_before_filter = len(env_file_paths)
        file_paths = filter_files_by_zenable_config(env_file_paths)
        filtered_count = files_before_filter - len(file_paths)

        if filtered_count > 0:
            logger.info(
                f"Filtered out {filtered_count} file(s) based on Zenable config skip patterns"
            )

        # If all files were filtered out, provide a helpful message
        if not file_paths and filtered_count > 0:
            click.echo(
                "All files from IDE context were filtered out by Zenable config skip patterns"
            )
            click.echo("No files to check.")
            sys.exit(ExitCode.SUCCESS)

        return file_paths


def create_header(*lines: str, padding: int = 8) -> str:
    """
    Create a centered header with equal signs.

    Args:
        lines: Text lines to display in the header
        padding: Number of spaces/equals on each side (default 8)

    Returns:
        Formatted header string
    """
    if not lines:
        return ""

    # Find the longest line
    max_length = max(len(line) for line in lines)

    # Total width is padding + max_length + padding
    total_width = padding * 2 + max_length

    # Build the header
    header_lines = []
    header_lines.append("=" * total_width)

    for line in lines:
        # Center each line within the available space
        centered = line.center(max_length)
        # Add padding on both sides
        header_lines.append(" " * padding + centered + " " * padding)

    header_lines.append("=" * total_width)

    return "\n".join(header_lines)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("patterns", nargs=-1, required=False)
@click.option(
    "--exclude",
    multiple=True,
    help="Patterns to exclude from checking",
)
@click.option(
    "--base-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Base directory for pattern matching (defaults to current directory)",
)
@click.pass_context
def check(ctx, patterns, exclude, base_path):
    """Check the provided files against your conformance tests

    Automatically detects files from IDE context when no patterns are provided.
    Supports glob patterns like **/*.py to check all Python files recursively.
    Files are processed in batches of 5 for optimal performance.

    \b
    Examples:
      # Check a single file
      zenable-mcp check example.py
    \b
      # Check all Python files recursively
      zenable-mcp check '**/*.py'
    \b
      # Check multiple patterns
      zenable-mcp check 'src/**/*.js' 'tests/**/*.js'
    \b
      # Exclude test files from checking
      zenable-mcp check '**/*.py' --exclude '**/test_*.py'
    \b
      # Specify base directory for pattern matching
      zenable-mcp check '*.py' --base-path ./src
    """
    api_key = ctx.obj.get("api_key", "")

    if not api_key:
        click.echo("Error: ZENABLE_API_KEY environment variable not set", err=True)
        click.echo("Please set it with: export ZENABLE_API_KEY=your-api-key", err=True)
        sys.exit(ExitCode.MISSING_API_KEY)

    # Display welcome header
    welcome_header = create_header(
        "Welcome to Zenable", "Production-Grade AI Coding Tools"
    )
    click.echo("\n" + welcome_header + "\n")
    click.echo("Detecting files...")

    # Determine which files to check
    file_paths = []

    if not patterns:
        # Auto-detect from IDE context
        file_paths = detect_files_from_ide_context(base_path)
    else:
        # Use provided CLI patterns
        try:
            file_paths = expand_file_patterns(
                list(patterns),
                base_path=base_path,
                exclude_patterns=list(exclude) if exclude else None,
            )
        except Exception as e:
            click.echo(f"Error expanding file patterns: {e}", err=True)
            sys.exit(ExitCode.NO_FILES_FOUND)

    if not file_paths:
        click.echo("No files found matching the specified patterns", err=True)
        sys.exit(ExitCode.NO_FILES_FOUND)

    # Read file contents
    files = []
    for file_path in file_paths:
        try:
            content = file_path.read_text()
            files.append({"path": str(file_path), "content": content})
        except Exception as e:
            click.echo(f"Error reading {file_path}: {e}", err=True)
            continue

    if not files:
        click.echo("No files could be read", err=True)
        sys.exit(ExitCode.FILE_READ_ERROR)

    async def check_files():
        # Store relative paths for use in batch processing
        get_relative_paths(file_paths, base_path)

        try:
            async with ZenableMCPClient(api_key) as client:
                # Process files in batches, showing progress
                results = await client.check_conformance(
                    files, batch_size=5, show_progress=True, ctx=ctx
                )

                # Parse results using the utility function
                all_results, has_errors, has_findings = parse_conformance_results(
                    results
                )

                # Display completion header
                complete_header = create_header("CONFORMANCE CHECK COMPLETE")
                click.echo("\n" + complete_header)

                # Display all results as returned by the MCP server
                if all_results:
                    for result_text in all_results:
                        click.echo("\n" + result_text)

                # Exit with appropriate code based on findings or errors
                if has_errors or has_findings:
                    sys.exit(ExitCode.CONFORMANCE_ISSUES_FOUND)

        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(ExitCode.API_ERROR)

    asyncio.run(check_files())
