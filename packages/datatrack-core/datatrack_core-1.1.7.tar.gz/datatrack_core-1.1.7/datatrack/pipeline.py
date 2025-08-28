"""
DataTrack CLI Pipeline
----------------------

Executes the full schema validation workflow:

Steps:
  1. Snapshot: Save latest schema from DB
  2. Linting: Run design lint rules (naming, ambiguity, types)
  3. Verify: Enforce schema rules (snake_case, reserved, data structure)
  4. Diff: Compare current vs previous snapshot
  5. Export: Save outputs to disk (.json format)

Artifacts are saved in: .databases/exports/

Author: N R Navaneet
"""

import typer
from rich.console import Console
from rich.table import Table

from datatrack.connect import get_connected_db_name, get_saved_connection
from datatrack.diff import diff_schemas, load_snapshots
from datatrack.exporter import export_diff, export_snapshot
from datatrack.linter import lint_schema
from datatrack.linter import load_latest_snapshot as load_lint_snapshot
from datatrack.tracker import snapshot
from datatrack.verifier import load_latest_snapshot as load_ver_snapshot
from datatrack.verifier import load_rules, verify_schema

app = typer.Typer()

# Step result summary
step_summary = {}

# Export directory (hardcoded in current architecture)
EXPORT_PATH = ".databases/exports/"

console = Console()


def prompt_to_continue(step_name: str) -> bool:
    return typer.confirm(
        f"[{step_name}] failed. Do you want to continue?",
        default=False,
    )


def print_summary(summary: dict):
    table = Table(title="DataTrack: Schema Workflow", show_lines=True)
    table.add_column("Step", style="bold", justify="left")
    table.add_column("Result", justify="left")
    for step, result in summary.items():
        table.add_row(step, result)
    console.print(table)


def print_artifact_paths():
    table = Table(title="Saved Artifacts", show_lines=True)
    table.add_column("Artifact", style="bold", justify="left")
    table.add_column("Path", justify="left")
    table.add_row(
        "Snapshot directory",
        f"{EXPORT_PATH}{get_connected_db_name()}/snapshots/",
    )
    table.add_row(
        "Diff output",
        f"{EXPORT_PATH}{get_connected_db_name()}/latest_diff.json",
    )
    table.add_row("Exported files", f"{EXPORT_PATH} (e.g., snapshot.json, diff.json)")
    console.print(table)


@app.command("run")
def run_pipeline(
    verbose: bool = typer.Option(True, help="Enable detailed output"),
    strict: bool = typer.Option(False, help="Fail pipeline on lint warnings"),
):
    # 1. Snapshot
    print("\n[1] Snapshotting schema...")
    source = get_saved_connection()
    if not source:
        step_summary["1. Snapshot"] = "✖ No DB connection"
        raise typer.Exit(code=1)

    try:
        snapshot(source)
        step_summary["1. Snapshot"] = "✔ Success"
    except Exception as e:
        step_summary["1. Snapshot"] = "✖ Error"
        print(f"Snapshot failed: {e}")
        raise typer.Exit(code=1)

    # 2. Linting
    print("\n[2] Linting schema...")
    try:
        schema = load_lint_snapshot()
        lint_warnings = lint_schema(schema)
        if lint_warnings:
            for w in lint_warnings:
                print(f"  - {w}")
            if strict:
                step_summary["2. Linting"] = f"✖ {len(lint_warnings)} Warnings"
                print_summary(step_summary)
                raise typer.Exit(code=1)
            else:
                step_summary["2. Linting"] = f"⚠ {len(lint_warnings)} Warnings"
                if not prompt_to_continue("Linting"):
                    print_summary(step_summary)
                    raise typer.Exit(code=1)
        else:
            step_summary["2. Linting"] = "✔ Clean"
    except Exception as e:
        step_summary["2. Linting"] = "✖ Error"
        print(f"Linting failed: {e}")
        if not prompt_to_continue("Linting"):
            raise typer.Exit(code=1)

    # 3. Verification
    print("\n[3] Verifying schema...")
    try:
        schema = load_ver_snapshot()
        rules = load_rules()
        violations = verify_schema(schema, rules)
        if violations:
            for v in violations:
                print(f"  - {v}")
            step_summary["3. Verify"] = f"✖ {len(violations)} Violations"
            if not prompt_to_continue("Verification"):
                print_summary(step_summary)
                raise typer.Exit(code=1)
        else:
            step_summary["3. Verify"] = "✔ OK"
    except Exception as e:
        step_summary["3. Verify"] = "✖ Error"
        print(f"Verification failed: {e}")
        if not prompt_to_continue("Verification"):
            raise typer.Exit(code=1)

    # 4. Diff
    print("\n[4] Computing diff...")
    try:
        old, new = load_snapshots()
        diff_schemas(old, new)
        step_summary["4. Diff"] = "✔ Applied"
    except Exception as e:
        step_summary["4. Diff"] = "✖ Skipped"
        print(f"Diff error: {e}")
        if not prompt_to_continue("Diff"):
            print_summary(step_summary)
            raise typer.Exit(code=1)

    # 5. Export
    print("\n[5] Exporting...")
    try:
        export_snapshot(fmt="json")
        export_diff(fmt="json")
        step_summary["5. Export"] = "✔ Saved"
    except Exception as e:
        step_summary["5. Export"] = "✖ Failed"
        print(f"Export error: {e}")
        print_summary(step_summary)
        raise typer.Exit(code=1)

    # Final UI + Paths
    print_summary(step_summary)
    print_artifact_paths()
