import json

import inquirer
import typer
from rich.prompt import Prompt

from ..consts import CONFIG_FILE_PATH
from ..utils.config import assert_config_file
from ..utils.console import console
from .types import ConfigAi, ConfigKonecy, ConfigMongo, ConfigType

app = typer.Typer()


@app.command(name="create")
def create(
    name: str | None = typer.Option(
        None, "--name", "-n", help="Name of the configuration"
    ),
    type: ConfigType | None = typer.Option(
        None, "--type", "-t", help="Type of the configuration"
    ),
):
    """Create a new configuration."""

    console.print("")

    if name is None:
        name = Prompt.ask("Enter the config name")
        if name == "":
            console.print("[red]Name cannot be empty[/red]")
            raise typer.Exit(1)

    if type is None:
        result = inquirer.prompt(
            [
                inquirer.List(
                    "type",
                    message="Select a type",
                    choices=[config_type.name for config_type in ConfigType],
                )
            ]
        )
        type = result.get("type", None)
        if not type:
            console.print("[red]No type selected[/red]")
            raise typer.Exit(1)

    console.print(f"[blue]Adding config {name} of type {type}...")

    json_config = assert_config_file()

    config_with_same_name = next(
        (config for config in json_config if config["name"] == name), None
    )
    if config_with_same_name:
        console.print(f"[red]Config {name} already exists[/red]")
        raise typer.Exit(1)

    new_config = get_new_config(name, type)
    json_config.append(new_config.to_dict())

    with open(CONFIG_FILE_PATH, "w") as file:
        json.dump(json_config, file, indent=4)

    console.print(f"[green]Config {name} of type {type} added successfully[/green]")


def get_new_config(name: str, type: ConfigType):
    match type:
        case ConfigType.KONECTY.name:
            new_config = ConfigKonecy(name=name, type=ConfigType.KONECTY)
            new_config.konecty_url = Prompt.ask("Konecty URL")
            new_config.konecty_token = Prompt.ask("Konecty Token")
        case ConfigType.MONGO.name:
            new_config = ConfigMongo(name=name, type=ConfigType.MONGO)
            new_config.mongo_url = Prompt.ask("Mongo URL")
        case ConfigType.AI.name:
            new_config = ConfigAi(name=name, type=ConfigType.AI)
            new_config.api_key = Prompt.ask("OpenAI API Key")
        case _:
            console.print("[red]Invalid config type[/red]")
            raise typer.Exit(1)
    return new_config
