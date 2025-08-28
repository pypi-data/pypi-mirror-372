<p align="center">
  <a href="https://pypi.org/project/dbtracker/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/dbtracker?color=0052FF&labelColor=090422" />
  </a>
  <a href="https://pypi.org/project/dbtracker/">
    <img alt="Downloads" src="https://img.shields.io/pypi/dm/dbtracker?color=0052FF&labelColor=090422" />
  </a>
  <a href="https://github.com/nrnavaneet/datatrack">
    <img src="https://img.shields.io/github/stars/nrnavaneet/datatrack?color=0052FF&labelColor=090422" />
  </a>
  <a href="https://github.com/nrnavaneet/datatrack/pulse">
    <img src="https://img.shields.io/github/commit-activity/m/nrnavaneet/datatrack?color=0052FF&labelColor=090422" />
  </a>
</p>

<p align="center">
  <a href="https://github.com/nrnavaneet/datatrack/tree/main/docs/INSTALLATION.md">Installation</a>
  ·
  <a href="https://github.com/nrnavaneet/datatrack/tree/main/docs/USAGE.md">Usage</a>
  ·
  <a href="https://github.com/nrnavaneet/datatrack/tree/main/docs/contribute/CONTRIBUTING.md">Contributing</a>
  ·
  <a href="https://github.com/nrnavaneet/datatrack/tree/main/docs/contribute/CODE_OF_CONDUCT.md">Code of Conduct</a>
</p>

# Datatrack

**Datatrack** is a lightweight and open-source command-line tool designed to help data engineers and platform teams track database schema changes across versions. It ensures that schema updates are transparent and auditable, helping prevent silent failures in downstream pipelines.

## Key Features

- Capture schema snapshots from SQL-compatible databases (PostgreSQL, SQLite, MySQL, etc.)
- Lint schemas for naming issues and structural smells
- Verify schema compliance against custom rules
- Compare schema versions and generate diffs
- Export snapshots and diffs to JSON or YAML formats
- Run the full schema audit pipeline with a single command

## Why Use Datatrack

Managing schema changes in evolving environments is complex. Even a small change in column name, type, or structure can silently break dashboards or data pipelines. **Datatrack** helps prevent that by enabling:

- Git-like version control for database schemas
- Transparent collaboration and visibility within teams
- Faster issue detection with automatic diffs and rule checks

## Performance & Cost Savings

Datatrack’s parallel and batched snapshot engine delivers **significant performance improvements** for real-world databases.
Benchmarks were run in August 2025 on a MacBook Pro M2, Python 3.11, using SQLite and PostgreSQL.

| Database Size | Tables | Serial Time | Parallel Time | Speedup | Time Saved (per 1k runs) | Time Saved (per 50k runs) |
|--------------:|-------:|------------:|--------------:|--------:|-------------------------:|--------------------------:|
| **Small**     | 12     | 0.18 s      | 0.09 s        | **2×**  | 90 s                     | 75 min                    |
| **Medium**    | 75     | 0.95 s      | 0.32 s        | **3×**  | 630 s (10.5 min)         | 8.75 hrs                  |
| **Large**     | 250    | 2.80 s      | 0.80 s        | **3.5×**| 2,000 s (33 min)         | 27 hrs                    |

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

## Documentation

Please refer to the following docs for detailed guidance:

- [Installation Guide](https://github.com/nrnavaneet/datatrack/tree/main/docs/INSTALLATION.md)
- [Usage Instructions](https://github.com/nrnavaneet/datatrack/tree/main/docs/USAGE.md)
- [Contributing Guide](https://github.com/nrnavaneet/datatrack/blob/main/docs/contribute/CONTRIBUTING.md)
- [Code of Conduct](https://github.com/nrnavaneet/datatrack/tree/main/docs/contributeCODE_OF_CONDUCT.md)

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/nrnavaneet/datatrack/blob/main/LICENSE) file for details.

## Maintainer

Developed and maintained by [N R Navaneet](https://github.com/nrnavaneet).
