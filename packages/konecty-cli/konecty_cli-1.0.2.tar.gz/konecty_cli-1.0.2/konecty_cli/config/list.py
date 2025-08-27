import typer
from rich.table import Table

from ..utils.config import assert_config_file
from ..utils.console import console
from .types import Config

app = typer.Typer()


@app.command(name="list", help="List all configurations")
def list_command():
    """List all configurations."""

    console.print("")

    json_config = assert_config_file()

    if len(json_config) == 0:
        console.print("[red]You have no configs yet[/red]")
        return

    table = Table(title="Configs", show_lines=True)
    table.add_column("Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Type", justify="center", style="magenta", no_wrap=True)
    table.add_column("Data", justify="left", no_wrap=True)

    for config in json_config:
        data = Config.from_json(config).get_data()
        data_str = "\n".join(
            [f"[bold green]{key}[/bold green]: {value}" for key, value in data.items()]
        )
        table.add_row(config["name"], config["type"], data_str)

    console.print(table)
