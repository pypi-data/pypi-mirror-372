import json

import typer
from rich.prompt import Prompt

from ..consts import CONFIG_FILE_PATH
from ..utils.config import assert_config_file, inquire_for_config
from ..utils.console import console
from .types import Config, ConfigType

app = typer.Typer()


@app.command(name="edit")
def edit(
    name: str | None = typer.Option(
        None, "--name", "-n", help="Name of the configuration to edit"
    ),
):
    """Edit an existing configuration."""

    console.print("")

    # Get the config to edit
    if name is None:
        # Use the utility function to inquire for a config
        config_to_edit = inquire_for_config()
        if not config_to_edit:
            console.print("[red]No config selected[/red]")
            raise typer.Exit(1)
    else:
        # Find config by name
        json_config = assert_config_file()
        config_data = next(
            (config for config in json_config if config["name"] == name), None
        )
        if not config_data:
            console.print(f"[red]Config {name} not found[/red]")
            raise typer.Exit(1)
        config_to_edit = Config.from_json(config_data)

    console.print(
        f"[yellow]Editing config: {config_to_edit.name} ({config_to_edit.type.value})"
    )

    # Edit the config based on its type
    edited_config = edit_config_fields(config_to_edit)

    # Update the config file
    json_config = assert_config_file()

    # Find and replace the config
    for i, config in enumerate(json_config):
        if config["name"] == edited_config.name:
            json_config[i] = edited_config.to_dict()
            break

    with open(CONFIG_FILE_PATH, "w") as file:
        json.dump(json_config, file, indent=4)

    console.print(f"[green]Config {edited_config.name} updated successfully[/green]")


def edit_config_fields(config: Config) -> Config:
    """Edit the fields of a config based on its type"""
    console.print("\n[yellow]Press Enter to keep current value, or type new value")

    config.name = Prompt.ask("Config Name", default=config.name)

    match config.type:
        case ConfigType.KONECTY:
            current_url = getattr(config, "konecty_url", "")
            current_token = getattr(config, "konecty_token", "")

            new_url = Prompt.ask("Konecty URL", default=current_url)
            new_token = Prompt.ask("Konecty Token", default=current_token)

            config.konecty_url = new_url
            config.konecty_token = new_token

        case ConfigType.MONGO:
            current_url = getattr(config, "mongo_url", "")

            new_url = Prompt.ask("Mongo URL", default=current_url)
            config.mongo_url = new_url

        case ConfigType.AI:
            current_api_key = getattr(config, "api_key", "")
            new_api_key = Prompt.ask("API Key", default=current_api_key)
            config.api_key = new_api_key

        case _:
            console.print("[red]Invalid config type[/red]")
            raise typer.Exit(1)

    return config
