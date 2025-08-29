#!/usr/bin/env python3
"""
Tests for the sqlcgen tool.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
import os

# Add the parent directory to the path so we can import sqlcgen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqlcgen


class TestSQLCGen(unittest.TestCase):
    """Test cases for the sqlcgen tool."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.test_dir.cleanup()

    def create_test_schema(self, databases):
        """
        Create a test schema directory structure.

        Args:
            databases: List of database names to create
        """
        schema_dir = self.test_path / "schema" / "weavesql"
        for db_name in databases:
            db_dir = schema_dir / db_name
            (db_dir / "migrations").mkdir(parents=True)
            (db_dir / "queries").mkdir(parents=True)
            # Create dummy files
            (db_dir / "migrations" / "001_init.sql").touch()
            (db_dir / "queries" / "queries.sql").touch()
        return schema_dir

    def test_find_databases_with_valid_structure(self):
        """Test finding databases with valid directory structure."""
        schema_dir = self.create_test_schema(["weave", "llmx", "modex"])

        databases = sqlcgen.find_databases(schema_dir)

        self.assertEqual(len(databases), 3)
        self.assertEqual(databases[0].name, "llmx")
        self.assertEqual(databases[0].package, "llmxdb")
        self.assertEqual(databases[1].name, "modex")
        self.assertEqual(databases[1].package, "modexdb")
        self.assertEqual(databases[2].name, "weave")
        self.assertEqual(databases[2].package, "weavedb")

    def test_find_databases_skips_invalid_directories(self):
        """Test that directories without migrations or queries are skipped."""
        schema_dir = self.create_test_schema(["valid"])

        # Create invalid directories
        (schema_dir / "no_migrations").mkdir()
        (schema_dir / "no_migrations" / "queries").mkdir()

        (schema_dir / "no_queries").mkdir()
        (schema_dir / "no_queries" / "migrations").mkdir()

        (schema_dir / ".hidden").mkdir()
        (schema_dir / ".hidden" / "migrations").mkdir()
        (schema_dir / ".hidden" / "queries").mkdir()

        # Create a file (not a directory)
        (schema_dir / "not_a_dir.txt").touch()

        databases = sqlcgen.find_databases(schema_dir)

        # Should only find the valid database
        self.assertEqual(len(databases), 1)
        self.assertEqual(databases[0].name, "valid")

    def test_find_databases_with_nonexistent_directory(self):
        """Test that nonexistent directory causes exit."""
        nonexistent = self.test_path / "nonexistent"

        with self.assertRaises(SystemExit) as cm:
            sqlcgen.find_databases(nonexistent)

        self.assertEqual(cm.exception.code, 1)

    def test_generate_sqlc_config(self):
        """Test generation of sqlc.yaml configuration."""
        databases = [
            sqlcgen.Database("weave", "weavedb"),
            sqlcgen.Database("llmx", "llmxdb"),
        ]
        output_file = self.test_path / "sqlc.yaml"

        sqlcgen.generate_sqlc_config(databases, output_file)

        # Check that file was created
        self.assertTrue(output_file.exists())

        # Read and verify content
        content = output_file.read_text()

        # Check for required elements
        self.assertIn('version: "2"', content)
        self.assertIn("plugins:", content)
        self.assertIn("name: py", content)
        self.assertIn("sqlc-gen-python_1.3.0.wasm", content)

        # Check for database configurations
        self.assertIn('schema: "schema/weavesql/weave/migrations"', content)
        self.assertIn('queries: "schema/weavesql/weave/queries"', content)
        self.assertIn('package: "weave.weavesql.weavedb"', content)
        self.assertIn('out: "weave/weavesql/weavedb"', content)

        self.assertIn('schema: "schema/weavesql/llmx/migrations"', content)
        self.assertIn('queries: "schema/weavesql/llmx/queries"', content)
        self.assertIn('package: "weave.weavesql.llmxdb"', content)
        self.assertIn('out: "weave/weavesql/llmxdb"', content)

        # Check for options
        self.assertIn("emit_async_querier: true", content)
        self.assertIn("emit_str_enum: true", content)
        self.assertIn("emit_sync_querier: true", content)
        self.assertIn("query_parameter_limit: 2", content)

    def test_generate_sqlc_config_with_custom_schema_prefix(self):
        """Test generation with custom schema prefix."""
        databases = [
            sqlcgen.Database("test", "testdb"),
        ]
        output_file = self.test_path / "sqlc.yaml"

        sqlcgen.generate_sqlc_config(
            databases, output_file, schema_prefix="custom/path"
        )

        content = output_file.read_text()
        self.assertIn('schema: "custom/path/test/migrations"', content)
        self.assertIn('queries: "custom/path/test/queries"', content)

    def test_main_integration(self):
        """Test the main function with real directory structure."""
        schema_dir = self.create_test_schema(["db1", "db2"])
        output_file = self.test_path / "output.yaml"

        # Mock sys.argv
        test_args = [
            "sqlcgen.py",
            "--schema",
            str(schema_dir),
            "--output",
            str(output_file),
        ]

        with patch.object(sys, "argv", test_args):
            sqlcgen.main()

        # Verify output file was created
        self.assertTrue(output_file.exists())

        # Verify content
        content = output_file.read_text()
        self.assertIn("db1", content)
        self.assertIn("db2", content)
        self.assertIn("db1db", content)
        self.assertIn("db2db", content)

    def test_main_with_no_databases(self):
        """Test main function when no valid databases are found."""
        empty_dir = self.test_path / "empty"
        empty_dir.mkdir()
        output_file = self.test_path / "output.yaml"

        test_args = [
            "sqlcgen.py",
            "--schema",
            str(empty_dir),
            "--output",
            str(output_file),
        ]

        with patch.object(sys, "argv", test_args):
            with self.assertRaises(SystemExit) as cm:
                sqlcgen.main()

            # Should exit with code 0 (not an error, just no databases)
            self.assertEqual(cm.exception.code, 0)

        # Output file should not be created
        self.assertFalse(output_file.exists())

    def test_database_namedtuple(self):
        """Test the Database namedtuple."""
        db = sqlcgen.Database("mydb", "mydbpkg")
        self.assertEqual(db.name, "mydb")
        self.assertEqual(db.package, "mydbpkg")

    def test_sorting_of_databases(self):
        """Test that databases are sorted alphabetically."""
        schema_dir = self.create_test_schema(["zebra", "alpha", "beta"])

        databases = sqlcgen.find_databases(schema_dir)

        # Should be sorted alphabetically
        self.assertEqual(databases[0].name, "alpha")
        self.assertEqual(databases[1].name, "beta")
        self.assertEqual(databases[2].name, "zebra")


class TestSQLCGenOutput(unittest.TestCase):
    """Test the actual output format of generated configurations."""

    def test_yaml_structure(self):
        """Test that the generated YAML has the correct structure."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as f:
            databases = [
                sqlcgen.Database("test", "testdb"),
            ]
            output_file = Path(f.name)

            sqlcgen.generate_sqlc_config(databases, output_file)

            # Read and parse line by line to check structure
            lines = output_file.read_text().splitlines()

            # Check indentation and structure
            self.assertEqual(lines[0], 'version: "2"')
            self.assertEqual(lines[1], "plugins:")
            self.assertTrue(lines[2].startswith("  - name:"))

            # Find sql section
            sql_line = next(i for i, line in enumerate(lines) if line == "sql:")
            self.assertTrue(sql_line > 0)

            # Check database configuration starts with proper indentation
            db_start = sql_line + 1
            self.assertTrue(lines[db_start].startswith("  - schema:"))

            # Clean up
            output_file.unlink()

    def test_multiple_databases_formatting(self):
        """Test formatting with multiple databases."""
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as f:
            databases = [
                sqlcgen.Database("first", "firstdb"),
                sqlcgen.Database("second", "seconddb"),
            ]
            output_file = Path(f.name)

            sqlcgen.generate_sqlc_config(databases, output_file)

            content = output_file.read_text()

            # Count database entries
            schema_count = content.count("  - schema:")
            self.assertEqual(schema_count, 2)

            # Verify each database has all required fields
            for db in databases:
                self.assertIn(
                    f'schema: "schema/weavesql/{db.name}/migrations"', content
                )
                self.assertIn(f'queries: "schema/weavesql/{db.name}/queries"', content)
                self.assertIn(f'package: "weave.weavesql.{db.package}"', content)

            # Clean up
            output_file.unlink()


if __name__ == "__main__":
    unittest.main()
