# -*- coding: utf-8 -*-
# src/homemade_mcp/__main__.py
"""Minimal CLI entrypoint for Homemade-MCP.

Commands are intentionally limited to keep the project lightweight. This CLI is
primarily for quick sanity checks and version display.
"""

import typer
from . import __version__

app = typer.Typer(help="Homemade MCP CLI")


@app.command()
def hello():
    """Say hello."""
    typer.echo("01001000 01100101 01101100 01101100 01101111")


@app.command()
def version():
    """Show version."""
    typer.echo(__version__)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
