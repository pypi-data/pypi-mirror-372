import logging
import os

import click

from zenable_mcp import __version__
from zenable_mcp.commands import check, hook, install, version
from zenable_mcp.logging_config import configure_logging
from zenable_mcp.version_check import check_for_updates


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.pass_context
def cli(ctx, verbose, debug):
    """Zenable - Clean Up Sloppy AI Code and Prevent AI-Created Security Vulnerabilities"""
    # Ensure that ctx.obj exists
    ctx.ensure_object(dict)

    # Store API key in context for subcommands to use
    ctx.obj["api_key"] = os.environ.get("ZENABLE_API_KEY")

    # Configure logging based on flags with colored output
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    configure_logging(log_level, debug=debug)


# Add commands to the CLI group
cli.add_command(version)
cli.add_command(check)
cli.add_command(hook)
cli.add_command(install)


def main():
    """Main entry point"""
    # Check for updates before running the CLI
    check_for_updates(__version__)
    cli()


if __name__ == "__main__":
    main()
