"""
Schema Rule Verifier for Datatrack

Validates schema snapshots against custom rules including:
- snake_case naming enforcement
- reserved keyword avoidance
- structural integrity of table data
"""

import re
from pathlib import Path

import yaml

from datatrack.connect import get_connected_db_name

# Default rule configuration if schema_rules.yaml is not found or invalid
DEFAULT_RULES = {
    "enforce_snake_case": True,
    "reserved_keywords": {
        "select",
        "from",
        "table",
        "drop",
        "insert",
        "update",
        "delete",
        "create",
        "alter",
        "rename",
        "join",
        "where",
        "group",
        "by",
        "having",
        "order",
        "limit",
        "offset",
        "union",
        "intersect",
        "except",
        "as",
        "on",
        "in",
        "not",
        "is",
        "null",
        "and",
        "or",
        "like",
        "between",
        "exists",
    },
}


def load_latest_snapshot() -> dict:
    """
    Load the most recent YAML snapshot for the connected database.

    Returns:
        dict: Snapshot data.

    Raises:
        ValueError: If no snapshot exists.
    """
    db_name = get_connected_db_name()
    snap_dir = Path(".databases/exports") / db_name / "snapshots"
    snapshots = sorted(snap_dir.glob("*.yaml"), reverse=True)

    if not snapshots:
        raise ValueError(f"No snapshots found for database '{db_name}'.")

    with open(snapshots[0]) as f:
        return yaml.safe_load(f)


def load_rules() -> dict:
    """
    Load rules from `schema_rules.yaml` or return defaults.

    Returns:
        dict: Rules including `enforce_snake_case` and `reserved_keywords`.
    """
    rules_path = Path("schema_rules.yaml")
    if rules_path.exists():
        try:
            with open(rules_path) as f:
                config = yaml.safe_load(f)
            enforce_snake = config.get("rules", {}).get("enforce_snake_case", True)
            reserved = config.get("rules", {}).get("reserved_keywords", [])

            # Ensure types are correct
            if not isinstance(reserved, (list, set)):
                reserved = []
            return {
                "enforce_snake_case": bool(enforce_snake),
                "reserved_keywords": set(str(k).lower() for k in reserved),
            }
        except Exception as e:
            print(f"[WARNING] Failed to load rules: {e}. Using defaults.")

    return {
        "enforce_snake_case": DEFAULT_RULES["enforce_snake_case"],
        "reserved_keywords": set(DEFAULT_RULES["reserved_keywords"]),
    }


def is_snake_case(name: str) -> bool:
    """
    Validate if name follows snake_case pattern.

    Args:
        name (str): Identifier to validate.

    Returns:
        bool: True if snake_case, else False.
    """
    return bool(re.fullmatch(r"[a-z0-9_]+", name))


def verify_schema(schema: dict, rules: dict) -> list[str]:
    """
    Apply rule-based verification on schema and data.

    Args:
        schema (dict): Parsed YAML snapshot.
        rules (dict): Rule configuration.

    Returns:
        list[str]: List of schema/data violations.
    """
    violations = []

    enforce_snake = rules.get("enforce_snake_case", True)
    reserved = set(str(k).lower() for k in rules.get("reserved_keywords", set()))

    tables = schema.get("tables", [])
    data_section = schema.get("data", {})

    for table in tables:
        table_name = table.get("name", "")
        columns = table.get("columns", [])
        col_names = {col.get("name", "") for col in columns if col.get("name")}

        # --- Table Name Validation ---
        if enforce_snake and not is_snake_case(table_name):
            violations.append(f"Table name not snake_case: {table_name}")
        if table_name.lower() in reserved:
            violations.append(f"Table name uses reserved word: {table_name}")

        # --- Column Name Validation ---
        for col in columns:
            col_name = col.get("name", "")
            if enforce_snake and not is_snake_case(col_name):
                violations.append(f"{table_name}.{col_name} not snake_case")
            if col_name.lower() in reserved:
                violations.append(f"{table_name}.{col_name} uses reserved word")

        # --- Row Data Validation ---
        if table_name in data_section:
            rows = data_section[table_name]
            if not isinstance(rows, list):
                violations.append(
                    f"Data for table `{table_name}` is not a list of rows."
                )
                continue

            for idx, row in enumerate(rows):
                if not isinstance(row, dict):
                    violations.append(
                        f"Row {idx} in `{table_name}` is not a dictionary."
                    )
                    continue

                row_keys = set(row.keys())
                missing_keys = col_names - row_keys
                extra_keys = row_keys - col_names

                if missing_keys:
                    violations.append(
                        f"Table `{table_name}` row {idx} missing keys: {sorted(missing_keys)}"
                    )
                if extra_keys:
                    violations.append(
                        f"Table `{table_name}` row {idx} has unknown keys: {sorted(extra_keys)}"
                    )
        else:
            if data_section:
                violations.append(
                    f"No data found for table `{table_name}` in snapshot."
                )

    return violations
