import typer

from .create import app as create_app

app = typer.Typer(
    name="project",
    help="Project management",
    add_completion=False,
    no_args_is_help=True,
    add_help_option=True,
)

app.add_typer(
    create_app,
)
