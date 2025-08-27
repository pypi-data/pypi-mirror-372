import json

import inquirer
import typer

from ..config.types import Config, ConfigType
from ..consts import CONFIG_FILE_PATH
from .console import console


def assert_config_file():
    """Assert the config file exists and is a valid json file."""
    if not CONFIG_FILE_PATH.exists():
        CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE_PATH.touch()
        return []

    with open(CONFIG_FILE_PATH, "r") as file:
        try:
            config = json.load(file)
        except json.JSONDecodeError:
            console.print("[red]Config file is not a valid json file[/red]")
            raise typer.Exit(1)

    if not isinstance(config, list):
        console.print("[red]Config file is not a list[/red]")
        raise typer.Exit(1)

    return config


def inquire_for_config(type_filter: ConfigType | None = None):
    """Inquire for a config"""
    configs = assert_config_file()

    if len(configs) == 0:
        console.print("[red]You have no configs yet[/red]")
        raise typer.Exit(1)

    inquire_message = "Select a config"

    if type_filter:
        configs = [config for config in configs if config["type"] == type_filter.value]
        inquire_message += f" of type {type_filter.value}"

    result = inquirer.prompt(
        [
            inquirer.List(
                "config",
                message=inquire_message,
                choices=[config["name"] for config in configs],
            )
        ]
    )

    selected_config = next(
        (config for config in configs if config["name"] == result["config"]), None
    )

    return Config.from_json(selected_config) if selected_config else None
