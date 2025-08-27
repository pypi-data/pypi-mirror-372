import click

from zenable_mcp import __version__


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
def version():
    """Show the zenable-mcp version"""
    click.echo(__version__)
