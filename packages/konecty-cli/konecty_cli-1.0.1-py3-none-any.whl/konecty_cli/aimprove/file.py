import subprocess
from pathlib import Path

import typer
from openai import OpenAI
from rich.prompt import Prompt

from ..config.types import ConfigAi, ConfigType
from ..consts import CODING_STYLE_LOCATION, CONDIG_STYLE_URL
from ..utils.config import inquire_for_config
from ..utils.console import console
from .LLM import get_llm
from .types import ImprovedFileResponse

app = typer.Typer()


@app.command(name="file")
def file(
    path: str | None = typer.Option(None, "--path", "-p", help="Path to the file"),
):
    """Improve the file code using AI, tuned with the company's coding style."""
    try:
        if path is None:
            path = Prompt.ask("Enter the path to the file")
            if path.strip() == "":
                console.print("[red]Path cannot be empty[/red]")
                raise typer.Exit(1)

        current_dir = Path.cwd()
        file_path = current_dir / path

        if not file_path.exists():
            console.print(f"[red]File {file_path} does not exist[/red]")
            raise typer.Exit(1)

        if not file_path.is_file():
            console.print(f"[red]Path {file_path} is not a file[/red]")
            raise typer.Exit(1)

        with open(file_path, "r") as file:
            file_content = file.read()

        config: ConfigAi | None = inquire_for_config(type_filter=ConfigType.AI)
        if not config:
            console.print("[red]No AI config found[/red]")
            raise typer.Exit(1)

        llm = get_llm(config)

        improve_result = improve_file(llm, file_content, config)

        if not improve_result:
            console.print("[green]Your code is already perfect! 🎉[/green]")
            raise typer.Exit(0)

        with open(file_path.parent / "improved.py", "w") as file:
            file.write(improve_result.improved_content)

        console.print("[green]Suggested improvements:[/green]")
        console.print(f"[sky_blue1]{improve_result.changes_summary}")

        # Write merge conflict markers directly to the file
        merge_diff = generate_merge_diff(file_content, improve_result.improved_content)
        with open(file_path, "w") as file:
            file.write(merge_diff)

        console.print("\n[grey50]Merge conflict markers have been added to the file.")
        console.print(
            "[grey50]Use your text editor's merge conflict resolution tools to accept/deny changes."
        )
    except KeyboardInterrupt:
        raise typer.Exit(0)


# TODO: Add cache
def download_coding_style():
    """Download the company's coding style from the GitHub Wiki pages and concatenate it into a single file."""
    console.print("[blue]Downloading company's coding style...[/blue]")
    subprocess.run(
        ["curl", CONDIG_STYLE_URL, "-o", CODING_STYLE_LOCATION],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    with open(CODING_STYLE_LOCATION, "r") as file:
        return file.read()


def improve_file(
    llm: OpenAI, file_content: str, config: ConfigAi
) -> ImprovedFileResponse | None:
    """Improve the file code using AI, tuned with the company's coding style."""
    coding_style = download_coding_style()

    prompt = f"""Você é um engenheiro de software sênior, responsável por garantir que todo o código esteja em conformidade com os padrões de codificação da empresa.
Você tem acesso completo à documentação oficial de estilo de código da empresa.

Sua tarefa é analisar o arquivo de código fornecido e retornar **exclusivamente** uma versão corrigida **somente se** houver violações ou não conformidades com os padrões estabelecidos.
Se o código já estiver totalmente conforme as diretrizes, **retorne exatamente `null`**.

### Regras obrigatórias:

* **Não altere** o conteúdo, formato ou estilo do arquivo além do estritamente necessário para corrigir violações das diretrizes.
* Preserve **integralmente** a linguagem, a lógica de negócio, a lógica de debug, a indentação, o espaçamento e o número de linhas do arquivo original.
* Não modifique nomes de variáveis, funções ou estruturas, a menos que violem explicitamente os padrões.
* Não adicione ou remova linhas ou blocos de código sem justificativa técnica relacionada às diretrizes.
* Não faça melhorias subjetivas — apenas alterações objetivamente necessárias segundo as regras do estilo.
* Preserve exatamente o mesmo número de linhas em branco no final do arquivo.
* Não adicione ou remova espaços em branco desnecessários.
* Se for preciso corrigir algo, faça a modificação **mínima possível** para atender ao padrão.
* Sempre responda em **pt-BR**.
* Se não houver ajustes a fazer, retorne **apenas** `null` (sem explicações adicionais).

### Estilo de código da empresa
{coding_style}
    """

    console.print("[green]Improving file...[/green]")
    response = llm.chat.completions.parse(
        model=config.model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": file_content},
        ],
        response_format=ImprovedFileResponse,
        metadata={"source": "konecty-cli/improve-file"},
    )

    result = response.choices[0].message.parsed

    # Normalize content for comparison (remove trailing whitespace but preserve structure)
    original_normalized = normalize_content_for_comparison(file_content)
    improved_normalized = normalize_content_for_comparison(result.improved_content)

    # If the AI returns the same content, consider it already perfect
    if original_normalized == improved_normalized:
        return None

    return result


def normalize_content_for_comparison(content: str) -> str:
    """Normalize content for comparison by handling trailing whitespace and newlines."""
    lines = content.splitlines()

    # Remove trailing empty lines
    while lines and lines[-1].strip() == "":
        lines.pop()

    # Normalize each line (remove trailing whitespace but preserve leading)
    normalized_lines = [line.rstrip() for line in lines]

    return "\n".join(normalized_lines)


def generate_merge_diff(original_content: str, improved_content: str) -> str:
    """Generate a git merge-style diff showing original vs improved content."""
    import difflib

    # Normalize both contents to avoid false positives from whitespace differences
    original_lines = normalize_content_for_comparison(original_content).splitlines(
        keepends=True
    )
    improved_lines = normalize_content_for_comparison(improved_content).splitlines(
        keepends=True
    )

    # Use difflib to get the differences
    matcher = difflib.SequenceMatcher(None, original_lines, improved_lines)

    result = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            # Lines are the same, add them as context
            result.extend(original_lines[i1:i2])
        elif tag == "replace":
            # Lines are different, show both versions
            result.append("<<<<<<< ORIGINAL\n")
            result.extend(original_lines[i1:i2])
            result.append("=======\n")
            result.extend(improved_lines[j1:j2])
            result.append(">>>>>>> IMPROVED\n")
        elif tag == "delete":
            # Lines were removed
            result.append("<<<<<<< ORIGINAL\n")
            result.extend(original_lines[i1:i2])
            result.append("=======\n")
            result.append(">>>>>>> IMPROVED\n")
        elif tag == "insert":
            # Lines were added
            result.append("<<<<<<< ORIGINAL\n")
            result.append("=======\n")
            result.extend(improved_lines[j1:j2])
            result.append(">>>>>>> IMPROVED\n")

    # Preserve the original file's trailing newline behavior
    final_content = "".join(result)

    # If the original had a trailing newline, ensure the result does too
    if original_content.endswith("\n") and not final_content.endswith("\n"):
        final_content += "\n"
    elif not original_content.endswith("\n") and final_content.endswith("\n"):
        final_content = final_content.rstrip("\n")

    return final_content
