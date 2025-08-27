"""Main CLI application."""

import sys

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__

app = typer.Typer(
    name="konecty-cli",
    help="Konecty CLI utilities",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Show information about the CLI."""
    console.print(
        Panel(
            f"[bold blue]Konecty CLI[/bold blue]\n"
            f"Version: {__version__}\n"
            f"Python: {sys.version.split()[0]}",
            title="Information",
        )
    )


@app.command()
def help():
    """Show help information."""
    console.print(app.get_help())


def main():
    console.print(sys.argv)
    if len(sys.argv) == 1:
        sys.argv.append("help")
    console.print(sys.argv)
    app()


if __name__ == "__main__":
    main()
