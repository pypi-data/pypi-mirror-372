"""CLI for PolyCLI."""

import click
from pathlib import Path


@click.group()
def cli():
    """PolyCLI - Unified AI agent interface."""
    pass


@cli.group()
def sandbox():
    """Sandbox commands for safe testing."""
    pass


@sandbox.command()
@click.option('--dir', '-d', default='.', help='Directory to initialize')
def init(dir):
    """Initialize a new sandbox project."""
    from .sandbox import init as sandbox_init
    sandbox_init(dir)


@sandbox.command()
@click.option('--input', '-i', help='Input folder to use')
@click.option('--dir', '-d', default='.', help='Project directory')
@click.option('--no-stream', is_flag=True, help='Disable output streaming')
@click.option('--ports', '-p', help='Port mappings (e.g. 8000:8000,5000:5000)')
def run(input, dir, no_stream, ports):
    """Run sandbox in Docker."""
    from .sandbox.runner import run as sandbox_run
    sandbox_run(dir, input, stream=not no_stream, ports=ports)


@cli.command(hidden=True)  # @@@ Easter egg - resume from Claude Code
def chat():
    """Resume from latest Claude Code session."""
    from .chat import run_chat
    run_chat()


if __name__ == "__main__":
    cli()