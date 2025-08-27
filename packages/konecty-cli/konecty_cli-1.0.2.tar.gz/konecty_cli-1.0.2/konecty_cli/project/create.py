import shutil
import subprocess
from pathlib import Path

import inquirer
import typer
from rich.prompt import Prompt

from ..consts import KONECTY_DIR, TEMPLATES_REPO_URL
from ..utils.console import console

app = typer.Typer()

stacks = ["Python", "Typescript", "React"]


@app.command(name="create")
def create(
    name: str | None = typer.Option(None, "--name", "-n", help="Name of the project"),
    stack: str | None = typer.Option(None, "--stack", "-s", help="Stack to use"),
):
    """Create a new project from templates."""
    if name is None:
        name = Prompt.ask("Enter the name of the project")
        if not name.strip():
            console.print("[red]Project name cannot be empty[/red]")
            raise typer.Exit(1)

    if stack is None or stack not in stacks:
        result = inquirer.prompt(
            [
                inquirer.List(
                    "stack",
                    message="Select a stack",
                    choices=stacks,
                )
            ]
        )
        stack = result.get("stack", None)
        if not stack:
            console.print("[red]No stack selected[/red]")
            raise typer.Exit(1)

    # Get current working directory
    project_dir = Path.cwd() / name
    templates_dir = KONECTY_DIR / ".temp_templates"

    if project_dir.exists():
        console.print(
            f"[red]Project '{name}' already exists in current directory[/red]"
        )
        raise typer.Exit(1)

    console.print(f"[yellow]Creating project '{name}' with {stack} stack...[/yellow]")

    try:
        templates_dir = update_repo(templates_dir)

        init_template(templates_dir, stack, project_dir)

        setup_git(project_dir)

        console.print(
            f"[green]Project '{name}' created successfully in {project_dir}[/green]"
        )

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error updating repository: {e.stderr}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error creating project: {e}[/red]")
        raise typer.Exit(1)


def update_repo(repo_dir: Path) -> Path:
    """Update repository by pulling if it exists, otherwise clone it."""
    if repo_dir.exists() and (repo_dir / ".git").exists():
        # Repository exists, pull latest changes
        console.print("[blue]Updating templates repository...[/blue]")
        try:
            subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            console.print("[green]Repository updated successfully[/green]")
        except subprocess.CalledProcessError:
            # If pull fails, remove and re-clone
            console.print("[yellow]Pull failed, re-cloning repository...[/yellow]")
            shutil.rmtree(repo_dir)
            return clone_repo(repo_dir)
    else:
        return clone_repo(repo_dir)

    return repo_dir


def clone_repo(repo_dir: Path) -> Path:
    if repo_dir.exists():
        shutil.rmtree(repo_dir)

    console.print("[blue]Cloning templates repository...[/blue]")
    subprocess.run(
        ["git", "clone", TEMPLATES_REPO_URL, str(repo_dir)],
        capture_output=True,
        text=True,
        check=True,
    )
    return repo_dir


def init_template(temp_dir: Path, stack: str, project_dir: Path):
    # Look for the specific stack template
    stack_template_dir = temp_dir / "projects" / stack.lower()
    if not stack_template_dir.exists():
        console.print(
            f"[red]Template for stack '{stack_template_dir}' not found in repository[/red]"
        )
        raise typer.Exit(1)

    # Copy template to project directory
    console.print(f"[blue]Copying {stack} template...[/blue]")
    shutil.copytree(stack_template_dir, project_dir)


def setup_git(project_dir: Path):
    # Remove .git directory from template if it exists
    template_git_dir = project_dir / ".git"
    if template_git_dir.exists():
        shutil.rmtree(template_git_dir)

    # Initialize git repository in the new project
    console.print("[blue]Initializing git repository...[/blue]")
    subprocess.run(["git", "init"], cwd=project_dir, check=True)
