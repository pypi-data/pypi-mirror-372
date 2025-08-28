"""
Datatrack CLI

A command-line interface for tracking, validating, and exporting database schemas.
Built using Typer, this CLI helps teams manage schema evolution
with version control principles, automated linting, and verification rules.

Main Features:
--------------
- init          : Initialize Datatrack in the current directory
- connect       : Save a database connection string
- disconnect    : Remove saved connection
- test-connection: Verify if the saved database connection works
- snapshot      : Capture schema snapshots (with optional row samples)
- diff          : Compare latest two schema snapshots
- lint          : Run schema quality checks (naming, types, etc.)
- verify        : Validate schema against custom rules
- history       : Show schema snapshot history timeline
- export        : Export snapshots or diffs (JSON/YAML)
- pipeline      : Run snapshot → diff → lint → verify in one step
"""

import os
from pathlib import Path

import typer
import yaml

from datatrack import connect as connect_module
from datatrack import diff as diff_module
from datatrack import exporter, history, linter, pipeline
from datatrack import test_connection as test_module
from datatrack import tracker, verifier

app = typer.Typer(
    help="Datatrack: Schema tracking CLI",
    add_help_option=False,
    invoke_without_command=True,
)

CONFIG_DIR = ".datatrack"
CONFIG_FILE = "config.yaml"


@app.command()
def init():
    """
    Initialize Datatrack in the current directory.
    """
    config_path = Path(CONFIG_DIR)
    if config_path.exists():
        typer.echo("Datatrack is already initialized.")
        raise typer.Exit()

    # Create .datatrack directory
    config_path.mkdir(parents=True, exist_ok=True)

    # Default config contents
    default_config = {
        "project_name": "my-datatrack-project",
        "created_by": os.getenv("USER") or "unknown",
        "version": "0.1",
        "sources": [],
    }

    with open(config_path / CONFIG_FILE, "w") as f:
        yaml.dump(default_config, f)

    typer.echo("Datatrack initialized in .datatrack/")


@app.command()
def snapshot(
    include_data: bool = typer.Option(
        False,
        "--include-data",
        help="Include sample table data in the snapshot (default: False)",
    ),
    max_rows: int = typer.Option(
        100,
        "--max-rows",
        help="Maximum number of rows to capture per table (only if --include-data is used)",
    ),
):
    """
    Capture the current schema state from the connected database and save a snapshot.
    """
    source = connect_module.get_saved_connection()
    if not source:
        typer.echo(
            "No database connection found. Please run 'datatrack connect <db_uri>' first."
        )
        raise typer.Exit(code=1)

    typer.echo("\nCapturing schema snapshot from source...")

    try:
        snapshot_path = tracker.snapshot(
            source, include_data=include_data, max_rows=max_rows
        )
        typer.secho(
            "Snapshot successfully captured and saved.\n", fg=typer.colors.GREEN
        )
        typer.echo(f"Saved at: {snapshot_path}\n")
    except Exception as e:
        typer.secho(f"Error capturing snapshot: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def diff():
    """
    Compare latest two snapshots and show schema differences.
    """
    try:
        old, new = diff_module.load_snapshots()
        diff_module.diff_schemas(old, new)
    except Exception as e:
        typer.secho(f"{str(e)}", fg=typer.colors.RED)


@app.command()
def verify():
    """
    Check schema against configured rules (e.g. snake_case, reserved words).
    """
    typer.echo("\nVerifying schema...\n")

    try:
        schema = verifier.load_latest_snapshot()
        rules = verifier.load_rules()
        violations = verifier.verify_schema(schema, rules)

        if not violations:
            typer.secho("All schema rules passed!\n", fg=typer.colors.GREEN)
        else:
            for v in violations:
                typer.secho(v, fg=typer.colors.RED)
            raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"Error during verification: {str(e)}\n", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("history")
def history_command():
    """View schema snapshot history timeline"""
    history.print_history()
    print()


@app.command()
def export(
    type: str = typer.Option("snapshot", help="Export type: snapshot or diff"),
    format: str = typer.Option("json", help="Output format: json or yaml"),
):
    """
    Export latest snapshot or diff as JSON/YAML.
    Saves to default path in .databases/exports/
    """
    typer.echo(f"\nExporting {type} as {format}...\n")

    try:
        if type == "snapshot":
            exporter.export_snapshot(fmt=format)
            output_file = f".databases/exports/latest_snapshot.{format}"
        elif type == "diff":
            exporter.export_diff(fmt=format)
            output_file = f".databases/exports/latest_diff.{format}"
        else:
            typer.secho(
                "Invalid export type. Use 'snapshot' or 'diff'.", fg=typer.colors.RED
            )
            raise typer.Exit(code=1)

        typer.secho(f"Exported to {output_file}", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"Export failed: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def lint():
    """
    Run non-blocking schema quality checks (naming,types, etc).
    """
    typer.echo("\n Running schema linter...\n")

    try:
        schema = linter.load_latest_snapshot()
        warnings = linter.lint_schema(schema)

        if not warnings:
            typer.secho("No linting issues found!\n", fg=typer.colors.GREEN)
        else:
            for w in warnings:
                typer.secho(w, fg=typer.colors.YELLOW)
            raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"Error during linting: {str(e)}\n", fg=typer.colors.RED)
        raise typer.Exit(code=1)


app.add_typer(pipeline.app, name="pipeline")


@app.command()
def connect(link: str = typer.Argument(..., help="Database connection URI")):
    """
    Save the database connection link for future commands.
    """
    connect_module.save_connection(link)


@app.command()
def disconnect():
    """
    Remove the saved database connection link.
    """
    connect_module.remove_connection()


@app.command("test-connection")
def test_connection():
    """
    Test if the saved database connection works.
    """
    result = test_module.test_connection()
    if "failed" in result.lower() or "no connection" in result.lower():
        typer.secho(result, fg=typer.colors.RED)
        raise typer.Exit(code=1)
    else:
        typer.secho(result, fg=typer.colors.GREEN)


@app.callback()
def main(
    help: bool = typer.Option(
        False, "--help", "-h", is_eager=True, help="Show this message and exit."
    )
):
    if help:
        banner = """
        ██████╗   █████╗ ████████╗ █████╗ ████████╗██████╗   █████╗   ██████╗ ██╗  ██╗
        ██╔══██╗ ██╔══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗ ██╔══██╗ ██╔════╝ ██║ ██╔╝
        ██║  ██║ ███████║   ██║   ███████║   ██║   ██████╔╝ ███████║ ██║      █████╔╝
        ██║  ██║ ██╔══██║   ██║   ██╔══██║   ██║   ██╔══██╗ ██╔══██║ ██║      ██╔═██╗
        ██████╔╝ ██║  ██║   ██║   ██║  ██║   ██║   ██║  ██║ ██║  ██║ ╚██████╗ ██║  ██╗
        ╚═════╝  ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═╝  ╚═╝  ╚═════╝ ╚═╝  ╚═╝

                        “Version Control for Your Database Schema”
        """
        typer.echo(banner)

        typer.echo("USAGE:")
        typer.echo("  datatrack <command> [options]\n")

        typer.echo("COMMANDS:")
        typer.echo(
            "  init                 Initialize Datatrack config in the current directory."
        )
        typer.echo(
            "  connect              Connect to a database and save the connection string."
        )
        typer.echo("  disconnect           Remove the saved database connection.")
        typer.echo(
            "  snapshot             Capture a schema snapshot and save it to disk."
        )
        typer.echo("  SNAPSHOT OPTIONS:")
        typer.echo(" --include-data      Include row data in the snapshot.")
        typer.echo(
            " --max-rows <int>    Limit number of rows per table (used with --include-data)."
        )
        typer.echo("  diff                 Compare the latest two schema snapshots.")
        typer.echo("  lint                 Run a basic linter to flag schema smells.")
        typer.echo(
            "  verify               Apply custom schema verification rules from config."
        )
        typer.echo(
            "  export               Export latest snapshot or diff as JSON/YAML."
        )
        typer.echo("  history              View schema snapshot history.")
        typer.echo(
            "  pipeline run         Run snapshot, diff, lint, and verify in one step."
        )
        typer.echo("  help                 Show this help message.\n")

        typer.echo("EXPORT OPTIONS:")
        typer.echo(
            "  --type [snapshot|diff]     Type of export to generate (default: snapshot)"
        )
        typer.echo("  --format [json|yaml]       Output format (default: json)\n")

        typer.echo("EXAMPLES:")
        typer.echo("  # Connect to PostgreSQL:")
        typer.echo(
            "  datatrack connect postgresql+psycopg2://postgres:pass123@localhost:5433/testdb"
        )
        typer.echo("\n  # Connect to MySQL:")
        typer.echo(
            "  datatrack connect mysql+pymysql://root:pass123@localhost:3306/testdb"
        )
        typer.echo("\n  # Connect to SQLite:")
        typer.echo("  datatrack connect sqlite:///.databases/example.db")
        typer.echo("\n  # Take a snapshot:")
        typer.echo("  datatrack snapshot")
        typer.echo("\n  # Show differences between last 2 snapshots:")
        typer.echo("  datatrack diff")
        typer.echo("\n  # Export latest snapshot as YAML:")
        typer.echo("  datatrack export --type snapshot --format yaml")
        typer.echo("\n  # Export latest diff as JSON:")
        typer.echo("  datatrack export --type diff --format json")
        typer.echo("\n  # Lint the schema:")
        typer.echo("  datatrack lint")
        typer.echo("\n  # Verify with custom rules:")
        typer.echo("  datatrack verify")
        typer.echo("\n  # Show snapshot history:")
        typer.echo("  datatrack history")
        typer.echo("\n  # Run full pipeline (snapshot + diff + lint + verify):")
        typer.echo("  datatrack pipeline run\n")

        typer.echo("NOTES:")
        typer.echo(" • Datatrack supports PostgreSQL and MySQL (via SQLAlchemy URIs).")
        typer.echo(
            " • Snapshots are saved under `.databases/exports/<db_name>/snapshots/`."
        )
        typer.echo(
            " • Use a `schema_rules.yaml` file to define custom rules for verification."
        )
        typer.echo(
            " • Ideal for teams integrating schema change tracking in CI/CD pipelines.\n"
        )

        typer.echo("Documentation: https://github.com/nrnavaneet/datatrack")
        raise typer.Exit()


if __name__ == "__main__":
    app()
