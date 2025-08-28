# Datatrack - Version Control for Databases

Datatrack is a lightweight and open-source CLI tool that brings Git-like version control to your database schemas. Built for Data Engineers, Analytics Engineers, and Platform Teams, it automates:
	•	Schema snapshots
	•	Diffs across versions
	•	Linting for naming and structure
	•	Verification against custom rules
	•	Exporting to JSON/YAML

Because in modern data systems, your schema is your contract—and when it breaks silently, everything else crumbles.

## Features

- Snapshot schemas from any SQL-compatible DB
- Lint schema naming issues
- Enforce verification rules
- Compare schema snapshots (diff)
- Export to JSON/YAML for auditing or CI
- Full pipeline in one command


## Performance & Cost Savings

Datatrack’s parallel and batched snapshot engine delivers **significant performance improvements** for real-world databases.
Benchmarks were run in August 2025 on a MacBook Pro M2, Python 3.11, using SQLite and PostgreSQL.

| Database Size | Tables | Serial Time | Parallel Time | Speedup | Time Saved (per 1k runs) | Time Saved (per 50k runs) |
|--------------:|-------:|------------:|--------------:|--------:|-------------------------:|--------------------------:|
| Small         | 12     | 0.18 s      | 0.09 s        | 2×      | 90 s                     | 75 min                    |
| Medium        | 75     | 0.95 s      | 0.32 s        | 3×      | 630 s (10.5 min)         | 8.75 hrs                  |
| Large         | 250    | 2.80 s      | 0.80 s        | 3.5×    | 2,000 s (~33 min)        | 27 hrs                    |

### Key Takeaways

- **Snapshot time reduced by 65–75%** for medium and large databases.
- **Scales linearly**: higher workloads → greater savings.
- **Faster developer feedback**: reduced CI/CD wait times, fewer timeouts.
- **Lower infrastructure costs**: less CPU time means direct savings on cloud compute.

### Real-World Impact

For a team running 50,000 large snapshots/month, Datatrack saves ~27 hours of CPU time.
At typical cloud compute rates, this translates into **hundreds of dollars per year** in savings.
The bigger win, however, is **developer productivity and reliability**: faster pipelines, earlier error detection,
and less risk of schema-related outages.


### Datatrack Architecture

```text
+-------------------+
|      User/CLI     |
+-------------------+
          |
          v
+-------------------+
|   Typer CLI App   |  (datatrack/cli.py)
+-------------------+
          |
          v
+-------------------+
|   Command Router  |  (CLI commands: snapshot, diff, lint, verify, export, pipeline)
+-------------------+
          |
          v
+-------------------+
|   Tracker Logic   |  (datatrack/tracker.py)
|-------------------|
| - Introspection   |
| - Caching         |
| - Parallel Fetch  |
| - Batched Fetch   |
+-------------------+
          |
          v
+-------------------+
|   SQLAlchemy ORM  |  (DB connection, inspection)
+-------------------+
          |
          v
+-------------------+
|   Database Layer  |  (PostgreSQL, SQLite, MySQL, etc.)
+-------------------+
          |
          v
+-------------------+
|   Export/History  |  (JSON/YAML, snapshot history)
+-------------------+
          |
          v
+-------------------+
|   CI/CD & Audits  |  (Integration, reporting)
+-------------------+
```

### Pipeline Execution Flow (Mermaid Diagram)
flowchart TD
    A[User/CLI] --> B[Typer CLI App]
    B --> C[Pipeline Command (pipeline run)]
    C --> D1[Snapshot: Save latest schema]
    D1 --> D2[Linting: Check naming, types, ambiguity]
    D2 --> D3[Verify: Apply schema rules (snake_case, reserved words)]
    D3 --> D4[Diff: Compare with previous snapshot]
    D4 --> D5[Export: Save snapshot & diff as JSON]
    D5 --> E[Tracker Logic (parallel/cached introspection)]
    E --> F[SQLAlchemy DB Connection]
    F --> G[Database (PostgreSQL, MySQL, SQLite, etc.)]
    G --> H[Export/History/Reporting]


##  Installation

Option 1: Install from PyPI (production use)
```bash
pip install datatrack-core
```
This is the easiest and recommended way to use datatracker as a CLI tool in your workflows.


Option 2: Install from GitHub (for development)
```bash
git clone https://github.com/nrnavaneet/datatrack.git
cd datatrack
pip install -r requirements.txt
pip install -e .
```
This method is ideal if you want to contribute or modify the tool.

## Helpful Commands

Datatrack comes with built-in help and guidance for every command. Use this to quickly learn syntax and options:
```bash
datatrack --help
or
datatrack -h
```

##  How to Use

### 1. Initialize Tracking

```bash
datatrack init
```

Creates `.datatrack/`, `.databases/`, and optional initial files.


### 2. Connect to a Database

Save your DB connection for future use:

### MySQL

```bash
datatrack connect mysql+pymysql://root:<password>@localhost:3306/<database-name>
```

### PostgreSQL

```bash
datatrack connect postgresql+psycopg2://postgres:<password>@localhost:5432/<database-name>
```

### SQLite

```bash
datatrack connect sqlite:///.databases/<database-name>
```

## 3. Take a Schema Snapshot

```bash
datatrack snapshot
```

Saves the current schema to `.databases/exports/<db_name>/snapshots/`.

## 4. Lint the Schema

```bash
datatrack lint
```

Detects issues in naming and structure.

## 5. Verify Schema Rules

```bash
datatrack verify
```

Validates schema against `schema_rules.yaml`.

## 6. View Schema Differences

```bash
datatrack diff
```

Shows table and column changes between the latest two snapshots.

## 7. Export Snapshots or Diffs

Export latest snapshot as YAML (default)
```bash
datatrack export
```

Explicitly export snapshot as YAML
```bash
datatrack export --type snapshot --format yaml
```
Export latest diff as JSON
```bash
datatrack export --type diff --format json
```

Output is saved in `.databases/exports/<db_name>/`.

## 8. View Snapshot History

```bash
datatrack history
```

Displays all snapshot timestamps and table counts.

## 9. Run the Full Pipeline

```bash
datatrack pipeline run
```

Runs `lint`, `snapshot`, `verify`, `diff`, and `export` together.

For advanced use cases and integration into CI/CD, visit:

**https://github.com/nrnavaneet/datatrack**
