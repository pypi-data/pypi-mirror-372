import os
from typing import Optional

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

import typer
from questions_cli_app.core import process_csv
from questions_cli_app import config


app = typer.Typer(add_completion=False)


def _print_version():
    try:
        from importlib.metadata import version, PackageNotFoundError
        v = version("questions-cli")
    except Exception:
        v = "0.1.0"
    typer.echo(v)


def _select_mongo_uri(use_prod: bool, use_dev: bool) -> None:
    if use_prod and use_dev:
        typer.secho("Choose only one of --prod or --dev", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    if use_prod:
        if not config.MONGO_URI_PROD:
            typer.secho("MONGO_URI_PROD not set in environment/config", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
        os.environ["MONGO_URI"] = config.MONGO_URI_PROD
    elif use_dev:
        if not config.MONGO_URI_DEV:
            typer.secho("MONGO_URI_DEV not set in environment/config", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)
        os.environ["MONGO_URI"] = config.MONGO_URI_DEV


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    input_csv: Optional[str] = typer.Argument(None, help="Path to input CSV"),
    delimiter: str = typer.Option(",", "--delimiter", "-d", help="CSV delimiter"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Parse & classify/generate without DB writes"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Process only first N rows"),
    subjects_file: Optional[str] = typer.Option(None, "--subjects-file", help="Path to subjects file (csv/yaml/json)"),
    version: bool = typer.Option(False, "--version", help="Show version and exit"),
    prod: bool = typer.Option(False, "--prod", help="Use prod Mongo URI from config"),
    dev: bool = typer.Option(False, "--dev", help="Use dev Mongo URI from config"),
):
    if version:
        _print_version()
        raise typer.Exit(code=0)
    if ctx.invoked_subcommand is None:
        if not input_csv:
            typer.echo(app.get_help(ctx))
            raise typer.Exit(code=0)
        try:
            _select_mongo_uri(prod, dev)
            process_csv(input_csv, delimiter=delimiter, dry_run=dry_run, limit=limit, subjects_file=subjects_file)
        except Exception as e:
            typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)


@app.command()
def ingest(
    input_csv: str = typer.Argument(..., help="Path to input CSV"),
    delimiter: str = typer.Option(",", "--delimiter", "-d", help="CSV delimiter"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Parse & classify/generate without DB writes"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Process only first N rows"),
    subjects_file: Optional[str] = typer.Option(None, "--subjects-file", help="Path to subjects file (csv/yaml/json)"),
    prod: bool = typer.Option(False, "--prod", help="Use prod Mongo URI from config"),
    dev: bool = typer.Option(False, "--dev", help="Use dev Mongo URI from config"),
):
    try:
        _select_mongo_uri(prod, dev)
        process_csv(input_csv, delimiter=delimiter, dry_run=dry_run, limit=limit, subjects_file=subjects_file)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()