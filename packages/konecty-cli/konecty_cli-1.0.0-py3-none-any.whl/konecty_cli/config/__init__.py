import typer

from .add_to_env import app as add_to_env_app
from .create import app as create_app
from .edit import app as edit_app
from .list import app as list_app

app = typer.Typer(
    name="config",
    help="Configuration management",
    add_completion=False,
    no_args_is_help=True,
    add_help_option=True,
)

app.add_typer(
    add_to_env_app,
)

app.add_typer(
    create_app,
)

app.add_typer(
    edit_app,
)

app.add_typer(
    list_app,
)
