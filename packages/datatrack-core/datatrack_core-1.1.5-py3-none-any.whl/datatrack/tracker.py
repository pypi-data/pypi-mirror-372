import hashlib
import re
from datetime import datetime
from pathlib import Path

import yaml
from sqlalchemy import create_engine, inspect, text

from datatrack.connect import get_connected_db_name, get_saved_connection

EXPORT_BASE_DIR = Path(".databases/exports")


def sanitize_url(url_obj):
    """Remove sensitive credentials from DB URL."""
    return url_obj.set(password=None).set(username=None)


def compute_hash(data: dict) -> str:
    """Compute SHA256 hash of the snapshot content."""
    serialized = yaml.dump(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def save_schema_snapshot(schema: dict, db_name: str) -> Path:
    """Save schema to a YAML snapshot file with metadata."""
    snapshot_dir = EXPORT_BASE_DIR / db_name / "snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_id = f"snapshot_{timestamp}"
    snapshot_file = snapshot_dir / f"{snapshot_id}.yaml"

    # Add metadata
    schema["__meta__"] = {
        "snapshot_id": snapshot_id,
        "timestamp": timestamp,
        "database": db_name,
        "hash": compute_hash(schema),
    }

    with open(snapshot_file, "w") as f:
        yaml.dump(schema, f, sort_keys=False, default_flow_style=False)

    print(f"Snapshot saved at: {snapshot_file}")
    return snapshot_file


def is_valid_table_name(name: str) -> bool:
    """Validate that the table name contains only alphanumeric and underscores."""
    return re.match(r"^\w+$", name) is not None


def snapshot(source: str = None, include_data: bool = False, max_rows: int = 50):
    """Capture a full schema snapshot (with optional data)."""
    if source is None:
        source = get_saved_connection()
        if not source:
            raise ValueError(
                "No DB source provided or saved. Run `datatrack connect` first."
            )

    db_name = get_connected_db_name()
    engine = create_engine(source)
    insp = inspect(engine)

    schema_data = {
        "dialect": engine.dialect.name,
        "url": str(sanitize_url(engine.url)),
        "tables": [],
        "views": [],
        "triggers": [],
        "functions": [],
        "procedures": [],
        "sequences": [],
    }

    if include_data:
        schema_data["data"] = {}

    # In-memory cache for inspection
    cache = {}

    def get_cached(key, fn):
        if key not in cache:
            cache[key] = fn()
        return cache[key]

    import concurrent.futures

    table_names = get_cached("table_names", lambda: insp.get_table_names())

    def fetch_table_data(table_name):
        try:
            if not is_valid_table_name(table_name):
                raise ValueError(f"Invalid table name: {table_name}")
            # Create a new engine/connection for each thread (SQLite safe)
            thread_engine = create_engine(source)
            with thread_engine.connect() as thread_conn:
                query = text(f"SELECT * FROM {table_name} LIMIT :max_rows")  # nosec
                result = thread_conn.execute(query, {"max_rows": max_rows})
                rows = [dict(row) for row in result.fetchall()]
            return (table_name, rows)
        except Exception as e:
            print(f"Could not fetch data for `{table_name}`: {e}")
            return (table_name, [])

    # Tables
    for table_name in table_names:
        columns = get_cached(
            f"columns_{table_name}", lambda: insp.get_columns(table_name)
        )
        pk = get_cached(f"pk_{table_name}", lambda: insp.get_pk_constraint(table_name))
        fks = get_cached(f"fks_{table_name}", lambda: insp.get_foreign_keys(table_name))
        idx = get_cached(f"idx_{table_name}", lambda: insp.get_indexes(table_name))

        table_info = {
            "name": table_name,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                }
                for col in columns
            ],
            "primary_key": pk.get("constrained_columns", []),
            "foreign_keys": [
                {
                    "column": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                }
                for fk in fks
            ],
            "indexes": idx,
        }
        schema_data["tables"].append(table_info)

    # Adaptive parallel/batched data fetch
    if include_data and table_names:
        n_tables = len(table_names)
        if n_tables < 50:
            # Sequential
            for table_name in table_names:
                _, rows = fetch_table_data(table_name)
                schema_data["data"][table_name] = rows
        elif n_tables < 200:
            # Parallel (4 workers)
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                results = executor.map(fetch_table_data, table_names)
                for table_name, rows in results:
                    schema_data["data"][table_name] = rows
        else:
            # Parallel + Batched (8 workers, batch size 50)
            batch_size = 50
            batches = [
                table_names[i : i + batch_size] for i in range(0, n_tables, batch_size)
            ]
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                for batch in batches:
                    results = executor.map(fetch_table_data, batch)
                    for table_name, rows in results:
                        schema_data["data"][table_name] = rows

        # Views
        for view_name in insp.get_view_names():
            definition = insp.get_view_definition(view_name)
            schema_data["views"].append({"name": view_name, "definition": definition})

        # Dialect-specific extras
        dialect = engine.dialect.name.lower()

        if dialect == "mysql":
            with engine.connect() as conn:
                schema_data["triggers"] = [
                    dict(row) for row in conn.execute(text("SHOW TRIGGERS")).fetchall()
                ]
                schema_data["procedures"] = [
                    dict(row)
                    for row in conn.execute(
                        text("SHOW PROCEDURE STATUS WHERE Db = DATABASE()")
                    ).fetchall()
                ]
                schema_data["functions"] = [
                    dict(row)
                    for row in conn.execute(
                        text("SHOW FUNCTION STATUS WHERE Db = DATABASE()")
                    ).fetchall()
                ]

        elif dialect == "postgresql":
            with engine.connect() as conn:
                schema_data["triggers"] = [
                    dict(row)
                    for row in conn.execute(
                        text(
                            """
                    SELECT event_object_table, trigger_name, action_timing, event_manipulation, action_statement
                    FROM information_schema.triggers
                """
                        )
                    ).fetchall()
                ]
                schema_data["procedures"] = [
                    dict(row)
                    for row in conn.execute(
                        text(
                            """
                    SELECT proname, proargnames, prosrc
                    FROM pg_proc
                    JOIN pg_namespace ON pg_proc.pronamespace = pg_namespace.oid
                    WHERE pg_namespace.nspname NOT IN ('pg_catalog', 'information_schema')
                """
                        )
                    ).fetchall()
                ]
                schema_data["sequences"] = [
                    row["sequence_name"]
                    for row in conn.execute(
                        text("SELECT sequence_name FROM information_schema.sequences")
                    ).fetchall()
                ]

        elif dialect == "sqlite":
            with engine.connect() as conn:
                res = conn.execute(
                    text(
                        "SELECT name, type, sql FROM sqlite_master WHERE type IN ('view', 'trigger')"
                    )
                )
                for row in res.fetchall():
                    entry = dict(row)
                    if entry["type"] == "view":
                        schema_data["views"].append(
                            {"name": entry["name"], "definition": entry["sql"]}
                        )
                    elif entry["type"] == "trigger":
                        schema_data["triggers"].append(entry)

    return save_schema_snapshot(schema_data, db_name)
