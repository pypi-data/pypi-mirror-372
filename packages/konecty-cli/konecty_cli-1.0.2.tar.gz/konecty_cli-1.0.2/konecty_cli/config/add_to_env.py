from pathlib import Path

import typer

from ..utils.config import inquire_for_config
from ..utils.console import console

app = typer.Typer()


@app.command(name="add-to-env")
def add_to_env(
    env_path: str | None = typer.Option(
        None, "--env-path", "-e", help="Path to the .env file"
    ),
):
    """Add configuration variables to a .env file."""

    console.print("")

    # Determine the .env file path
    if env_path is None:
        env_file = Path.cwd() / ".env"
    else:
        env_path_obj = Path(env_path)
        if env_path_obj.is_dir():
            env_file = env_path_obj / ".env"
        else:
            env_file = env_path_obj

    console.print(f"[blue]Target .env file: {env_file}[/blue]")

    # Check if .env file exists, create if it doesn't
    if not env_file.exists():
        console.print(f"[yellow]Creating new .env file at {env_file}[/yellow]")
        env_file.parent.mkdir(parents=True, exist_ok=True)
        env_file.touch()

    # Select a configuration
    config = inquire_for_config()
    if not config:
        console.print("[red]No config selected[/red]")
        raise typer.Exit(1)

    console.print(
        f"[yellow]Selected config: {config.name} ({config.type.value})[/yellow]"
    )

    # Get environment variables from config
    env_vars = config.to_env()
    if not env_vars:
        console.print("[yellow]No environment variables to add[/yellow]")
        return

    # Read existing .env file content
    existing_content = ""
    if env_file.exists():
        with open(env_file, "r") as file:
            existing_content = file.read()

    # Check if config was already added
    config_comment = f"#### Konecty config {config.name}"
    if config_comment in existing_content:
        console.print(
            f"[yellow]Config {config.name} already exists in .env file[/yellow]"
        )
        return

    # Prepare new content to append
    new_content = f"\n{config_comment}\n"
    for key, value in env_vars.items():
        new_content += f"{key}={value}\n"

    # Append to .env file
    with open(env_file, "a") as file:
        file.write(new_content)

    # Summary
    console.print(
        f"[green]Added {len(env_vars)} environment variables from config '{config.name}'[/green]"
    )
    for key in env_vars.keys():
        console.print(f"  [blue]+ {key}[/blue]")
