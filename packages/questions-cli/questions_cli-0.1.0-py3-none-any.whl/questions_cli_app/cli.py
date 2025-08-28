import os
from typing import Optional

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

import typer
from questions_cli_app.core import process_csv


app = typer.Typer(add_completion=False)


def _print_version():
    try:
        from importlib.metadata import version, PackageNotFoundError
        v = version("questions-cli")
    except Exception:
        v = "0.1.0"
    typer.echo(v)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    input_csv: Optional[str] = typer.Argument(None, help="Path to input CSV"),
    delimiter: str = typer.Option(",", "--delimiter", "-d", help="CSV delimiter"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Parse & classify/generate without DB writes"),
    limit: int | None = typer.Option(None, "--limit", help="Process only first N rows"),
    subjects_file: Optional[str] = typer.Option(None, "--subjects-file", help="Path to subjects file (csv/yaml/json)"),
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
):
    if version:
        _print_version()
        raise typer.Exit(code=0)
    if ctx.invoked_subcommand is None:
        if not input_csv:
            typer.echo(app.get_help(ctx))
            raise typer.Exit(code=0)
        try:
            process_csv(input_csv, delimiter=delimiter, dry_run=dry_run, limit=limit, subjects_file=subjects_file)
        except Exception as e:
            typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)


@app.command()
def ingest(
    input_csv: str = typer.Argument(..., help="Path to input CSV"),
    delimiter: str = typer.Option(",", "--delimiter", "-d", help="CSV delimiter"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Parse & classify/generate without DB writes"),
    limit: int | None = typer.Option(None, "--limit", help="Process only first N rows"),
    subjects_file: Optional[str] = typer.Option(None, "--subjects-file", help="Path to subjects file (csv/yaml/json)"),
):
    try:
        process_csv(input_csv, delimiter=delimiter, dry_run=dry_run, limit=limit, subjects_file=subjects_file)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()