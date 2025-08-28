from datetime import datetime
from pathlib import Path

import yaml

from datatrack.connect import get_connected_db_name


def format_timestamp_from_filename(filename: str) -> str:
    try:
        # Extract timestamp like: snapshot_20250708_174233.yaml → 2025-07-08 17:42:33
        timestamp_str = filename.replace("snapshot_", "").replace(".yaml", "")
        dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Invalid format"


def print_history():
    try:
        db_name = get_connected_db_name()
    except Exception as e:
        print(f"[Error] Could not determine connected database: {e}")
        return

    snapshot_dir = Path(f".databases/exports/{db_name}/snapshots")
    if not snapshot_dir.exists():
        print(f"[Error] Snapshot directory does not exist for `{db_name}`.")
        return

    snapshots = sorted(snapshot_dir.glob("snapshot_*.yaml"), reverse=True)
    if not snapshots:
        print(f"[Info] No snapshots found for `{db_name}`.")
        return

    print(f"\nSnapshot History for `{db_name}`:")
    print("=" * 85)
    print(
        f"{'ID':<3} | {'Date & Time':<20} | {'Tables':<6} | {'Views':<6} | {'Triggers':<8} | Filename"
    )
    print("-" * 85)

    for idx, snap_file in enumerate(snapshots):
        timestamp = format_timestamp_from_filename(snap_file.name)
        try:
            with open(snap_file, "r") as f:
                snap_data = yaml.safe_load(f)
                table_count = len(snap_data.get("tables", []))
                view_count = len(snap_data.get("views", []))
                trigger_count = len(snap_data.get("triggers", []))
        except Exception:
            table_count = view_count = trigger_count = "ERR"

        print(
            f"{idx:<3} | {timestamp:<20} | {table_count:<6} | {view_count:<6} | {trigger_count:<8} | {snap_file.name}"
        )
