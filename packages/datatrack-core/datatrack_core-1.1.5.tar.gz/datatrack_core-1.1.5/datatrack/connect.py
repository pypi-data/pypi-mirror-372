import re
from pathlib import Path
from urllib.parse import urlparse

import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ArgumentError, OperationalError, SQLAlchemyError

# Config paths
CONFIG_DIR = Path(".datatrack")
DB_LINK_FILE = CONFIG_DIR / "db_link.yaml"


def get_connected_db_name():
    """
    Returns a safe, filesystem-friendly name for the connected database.
    - For SQLite: extracts the file name without extension.
    - For others: uses DB name from URI.
    """
    if not DB_LINK_FILE.exists():
        raise ValueError(
            "No database connection found. Please run `datatrack connect` first."
        )

    with open(DB_LINK_FILE) as f:
        uri = yaml.safe_load(f).get("link", "")
        parsed = urlparse(uri)

        # SQLite special case
        if parsed.scheme.startswith("sqlite"):
            db_path = Path(parsed.path).name
            db_name = db_path.replace(".db", "")
        else:
            db_name = parsed.path.lstrip("/")

        # Sanitize name
        safe_name = re.sub(r"[^\w\-]", "_", db_name)
        if not safe_name:
            raise ValueError("Could not extract a valid database name from URI.")
        return safe_name


def save_connection(link: str):
    """
    Tries to connect to the DB and save the connection only if valid.
    """
    if DB_LINK_FILE.exists():
        print("A database is already connected.")
        print("   Disconnect first using: `datatrack disconnect`\n")
        return

    try:
        engine = create_engine(link)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError as e:
        msg = str(e).lower()
        if "access denied" in msg:
            print("Access denied. Please check your DB username/password.")
        elif "can't connect" in msg or "could not connect" in msg:
            print("Could not connect to server. Is the DB server running?")
        elif "does not exist" in msg:
            print("Database not found. Please create it first or check the name.")
        else:
            print(f"Operational error: {e}")
        return
    except ArgumentError:
        print("Invalid connection string. Please verify format.")
        print("Example (MySQL): mysql+pymysql://root:pass@localhost:3306/dbname")
        print("Example (SQLite): sqlite:///path/to/file.db")
        return
    except ModuleNotFoundError:
        print("Missing driver. Please install required DB driver packages.")
        print("  - MySQL: `pip install pymysql`")
        print("  - PostgreSQL: `pip install psycopg2-binary`")
        return
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

    # Save connection
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(DB_LINK_FILE, "w") as f:
        yaml.dump({"link": link}, f)
    print(f"Successfully connected and saved link:\n   {link}")


def get_saved_connection():
    """
    Returns saved DB URI or None.
    """
    if DB_LINK_FILE.exists():
        with open(DB_LINK_FILE) as f:
            return yaml.safe_load(f).get("link")
    return None


def remove_connection():
    """
    Deletes the saved DB connection.
    """
    if DB_LINK_FILE.exists():
        DB_LINK_FILE.unlink()
        print("Disconnected and removed saved DB link.")
    else:
        print("No active database connection found.")
