import json
from pathlib import Path

import yaml

from datatrack.connect import get_connected_db_name

DB_LINK_FILE = Path(".datatrack/db_link.yaml")


def get_export_dir(db_name):
    path = Path(f".databases/exports/{db_name}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_snapshot_dir(db_name):
    path = Path(f".databases/exports/{db_name}/snapshots")
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_latest_snapshots(n=2):
    db_name = get_connected_db_name()
    snap_dir = get_snapshot_dir(db_name)
    snapshots = sorted(snap_dir.glob("*.yaml"), reverse=True)
    if len(snapshots) < n:
        raise ValueError(
            f"Not enough snapshots found for {db_name}. Found {len(snapshots)}, need {n}.",
        )

    data = []
    for s in snapshots[:n]:
        with open(s) as f:
            data.append(yaml.safe_load(f))
    return data


def export_snapshot(fmt="json", output_path=None):
    latest = load_latest_snapshots(n=1)[0]

    if output_path is None:
        db_name = get_connected_db_name()
        output_path = get_export_dir(db_name) / f"latest_snapshot.{fmt}"
    else:
        output_path = Path(output_path)

    _write_to_file(latest, output_path, fmt)
    print(f"Snapshot exported to {output_path}")


def export_diff(fmt="json", output_path=None):
    snap_new, snap_old = load_latest_snapshots(n=2)
    diff = _generate_diff(snap_old, snap_new)

    if output_path is None:
        db_name = get_connected_db_name()
        output_path = get_export_dir(db_name) / f"latest_diff.{fmt}"
    else:
        output_path = Path(output_path)

    _write_to_file(diff, output_path, fmt)
    print(f"Diff exported to {output_path}")


def _generate_diff(old, new):
    diff_result = {"added_tables": [], "removed_tables": [], "changed_tables": {}}

    old_tables = {t["name"]: t for t in old["tables"]}
    new_tables = {t["name"]: t for t in new["tables"]}

    added = set(new_tables) - set(old_tables)
    removed = set(old_tables) - set(new_tables)
    common = set(new_tables) & set(old_tables)

    for t in added:
        diff_result["added_tables"].append(t)
    for t in removed:
        diff_result["removed_tables"].append(t)

    for t in common:
        old_cols = {c["name"]: c["type"] for c in old_tables[t]["columns"]}
        new_cols = {c["name"]: c["type"] for c in new_tables[t]["columns"]}

        added_cols = set(new_cols) - set(old_cols)
        removed_cols = set(old_cols) - set(new_cols)
        modified = {
            c: {"from": old_cols[c], "to": new_cols[c]}
            for c in (set(old_cols) & set(new_cols))
            if old_cols[c] != new_cols[c]
        }

        if added_cols or removed_cols or modified:
            diff_result["changed_tables"][t] = {
                "added_columns": sorted(added_cols),
                "removed_columns": sorted(removed_cols),
                "modified_columns": modified,
            }

    return diff_result


def _write_to_file(data, path, fmt):
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt not in {"json", "yaml"}:
        raise ValueError(f"Unsupported format: {fmt}")

    with open(path, "w") as f:
        if fmt == "json":
            json.dump(data, f, indent=2)
        else:
            yaml.dump(data, f)
