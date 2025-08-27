"""Main CLI application."""

import sys

import typer
from rich.panel import Panel

from . import __version__
from .aimprove import app as aimprove_app
from .config import app as config_app
from .project import app as project_app
from .utils.console import console

common = {
    "no_args_is_help": True,
    "add_help_option": True,
}

app = typer.Typer(
    name="konecty-cli",
    help="Konecty CLI utilities",
    add_completion=False,
    **common,
)

app.add_typer(config_app, name="config", **common)
app.add_typer(project_app, name="project", **common)
app.add_typer(aimprove_app, name="aimprove", **common)


@app.command(name="version")
def version():
    """Show information about the CLI."""
    python_version = sys.version.split()[0]
    console.print(
        Panel(
            f"Version: {__version__}\nPython: {python_version}",
            subtitle="[bold blue]Konecty CLI[/bold blue]",
            subtitle_align="left",
        )
    )
