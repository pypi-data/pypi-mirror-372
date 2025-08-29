#!/usr/bin/env python3
"""
sqlcgen - SQLC Configuration Generator for Python projects

This tool automatically generates sqlc.yaml configuration based on directories
found in the schema/weavesql directory.
"""

import argparse
import sys
from pathlib import Path
from typing import List, NamedTuple


class Database(NamedTuple):
    """Represents a database configuration."""

    name: str  # e.g., "weave", "llmx"
    package: str  # e.g., "weavedb", "llmxdb"


def find_databases(schema_dir: Path) -> List[Database]:
    """
    Find all valid database directories in the schema directory.

    A valid database directory must contain both 'migrations' and 'queries' subdirectories.

    Args:
        schema_dir: Path to the schema directory containing database folders

    Returns:
        List of Database objects sorted by name
    """
    databases = []

    if not schema_dir.exists():
        print(f"Schema directory {schema_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    for entry in sorted(schema_dir.iterdir()):
        if not entry.is_dir():
            continue

        # Skip hidden directories
        if entry.name.startswith("."):
            continue

        # Check if migrations and queries directories exist
        migrations_path = entry / "migrations"
        queries_path = entry / "queries"

        if not migrations_path.exists():
            print(f"Skipping {entry.name}: migrations directory not found")
            continue

        if not queries_path.exists():
            print(f"Skipping {entry.name}: queries directory not found")
            continue

        databases.append(Database(name=entry.name, package=f"{entry.name}db"))

    return databases


def generate_sqlc_config(
    databases: List[Database], output_file: Path, schema_prefix: str = "schema/weavesql"
):
    """
    Generate sqlc.yaml configuration for Python using the sqlc Python plugin.

    Args:
        databases: List of Database objects
        output_file: Path where the generated config should be written
        schema_prefix: Prefix path to schema directory
    """
    # Start with version and plugin configuration
    config_lines = [
        'version: "2"',
        "plugins:",
        "  - name: py",
        "    wasm:",
        "      url: https://downloads.sqlc.dev/plugin/sqlc-gen-python_1.3.0.wasm",
        "      sha256: fbedae96b5ecae2380a70fb5b925fd4bff58a6cfb1f3140375d098fbab7b3a3c",
        "sql:",
    ]

    for db in databases:
        db_config = f'''  - schema: "{schema_prefix}/{db.name}/migrations"
    queries: "{schema_prefix}/{db.name}/queries"
    engine: "postgresql"
    codegen:
      - out: "weave/weavesql/{db.package}"
        plugin: "py"
        options:
          package: "weave.weavesql.{db.package}"
          emit_async_querier: true
          emit_str_enum: true
          emit_sync_querier: true
          query_parameter_limit: 2'''
        config_lines.append(db_config)

    # Write output file
    with open(output_file, "w") as f:
        f.write("\n".join(config_lines) + "\n")

    print(f"Generated {output_file} with {len(databases)} database configurations")
    for db in databases:
        print(f"  - {db.name} -> {db.package}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate sqlc.yaml configuration for Python projects from schema directories"
    )
    parser.add_argument(
        "--schema",
        type=str,
        default="schema/weavesql",
        help="Path to schema directory containing database folders (default: schema/weavesql)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="sqlc.yaml",
        help="Output file path for generated sqlc.yaml (default: sqlc.yaml)",
    )

    args = parser.parse_args()

    # Convert paths
    schema_dir = Path(args.schema)
    output_file = Path(args.output)

    # Find databases
    databases = find_databases(schema_dir)

    if not databases:
        print("No valid database directories found")
        sys.exit(0)

    # Generate configuration
    generate_sqlc_config(databases, output_file, schema_prefix=args.schema)


if __name__ == "__main__":
    main()
