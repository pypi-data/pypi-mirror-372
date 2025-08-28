import re
from pathlib import Path

import yaml

from datatrack.connect import get_connected_db_name


def load_lint_rules():
    with open("schema_rules.yaml") as f:
        rules = yaml.safe_load(f)["rules"]
    return {
        "MAX_NAME_LENGTH": rules.get("max_name_length", 30),
        "AMBIGUOUS_NAMES": set(rules.get("ambiguous_names", [])),
        "GENERIC_TYPES": set(rules.get("generic_types", [])),
        "RESERVED_KEYWORDS": set(rules.get("reserved_keywords", [])),
        "ENFORCE_SNAKE_CASE": rules.get("enforce_snake_case", True),
    }


LINT_RULES = load_lint_rules()


def is_snake_case(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z][a-z0-9_]*", name))


def load_latest_snapshot():
    """
    Load the most recent YAML schema snapshot from exports.
    """
    db_name = get_connected_db_name()
    snap_dir = Path(".databases/exports") / db_name / "snapshots"
    snapshots = sorted(snap_dir.glob("*.yaml"), reverse=True)

    if not snapshots:
        raise ValueError(f"No snapshots found for database '{db_name}'.")

    with open(snapshots[0]) as f:
        return yaml.safe_load(f)


def lint_schema(schema: dict) -> list[str]:
    """
    Lint schema for naming, ambiguity, reserved words, length, casing, and generic types.
    """
    warnings = []

    for table in schema.get("tables", []):
        table_name = table["name"]
        # --- Table name checks ---
        if len(table_name) > LINT_RULES["MAX_NAME_LENGTH"]:
            warnings.append(
                f"Table name '{table_name}' exceeds max length of {LINT_RULES['MAX_NAME_LENGTH']} characters."
                "Consider shortening it (e.g., 'user_activity_log' -> 'activity_log').",
            )

        if LINT_RULES["ENFORCE_SNAKE_CASE"] and not is_snake_case(table_name):
            warnings.append(
                f"Table name '{table_name}' is not in snake_case."
                "Avoid using keywords like 'select', 'table', 'order'.",
            )

        if table_name.lower() in LINT_RULES["RESERVED_KEYWORDS"]:
            warnings.append(
                f"Table name '{table_name}' is a reserved SQL keyword."
                "Use more descriptive names like 'user_logs' or 'product_metrics'.",
            )

        if table_name.lower() in LINT_RULES["AMBIGUOUS_NAMES"]:
            warnings.append(
                f"Table name '{table_name}' is too ambiguous."
                "Use more descriptive names like 'user_logs' or 'product_metrics'.",
            )

        # --- Column checks ---
        for col in table.get("columns", []):
            col_name = col["name"]
            col_type = str(col.get("type", "")).lower()

            if len(col_name) > LINT_RULES["MAX_NAME_LENGTH"]:
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' exceeds max name length."
                    "Use concise names like 'created_at', 'order_total'.",
                )

            if LINT_RULES["ENFORCE_SNAKE_CASE"] and not is_snake_case(col_name):
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' is not in snake_case."
                    "Example: rename 'UserID' to 'user_id'.",
                )

            if col_name.lower() in LINT_RULES["RESERVED_KEYWORDS"]:
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' is a reserved SQL keyword."
                    "Avoid column names like 'from', 'order', 'select'.",
                )

            if col_name.lower() in LINT_RULES["AMBIGUOUS_NAMES"]:
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' has an ambiguous name.",
                )

            normalized_type = re.sub(r"\(.*\)", "", col_type).strip().lower()
            if normalized_type in LINT_RULES["GENERIC_TYPES"]:
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' uses a generic type: {col_type}."
                    "Consider using domain-specific types like 'decimal(10,2)', 'varchar(255)', or 'timestamp with time zone'.",
                )

    return warnings
