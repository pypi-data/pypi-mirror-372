import typer

from .file import app as file_app

app = typer.Typer(
    name="aimprove",
    help="AI improve",
    add_completion=False,
    no_args_is_help=True,
    add_help_option=True,
)

app.add_typer(
    file_app,
)
