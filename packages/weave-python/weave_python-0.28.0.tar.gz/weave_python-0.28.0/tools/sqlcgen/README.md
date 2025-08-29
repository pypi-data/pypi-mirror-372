# sqlcgen - SQLC Configuration Generator for Python

This tool automatically generates `sqlc.yaml` configuration for Python projects based on directories found in the
schema/weavesql directory.

## Usage

From the `weave-python` directory:

```bash
python tools/sqlcgen/sqlcgen.py [options]
```

### Options

- `--schema`: Path to schema directory containing database folders (default: "schema/weavesql")
- `--output`: Output file path for generated sqlc.yaml (default: "sqlc.yaml")

### Examples

Generate configuration:

```bash
python tools/sqlcgen/sqlcgen.py
```

Use custom schema directory:

```bash
python tools/sqlcgen/sqlcgen.py --schema ../custom/schema --output custom-sqlc.yaml
```

## How it Works

1. Scans the schema directory for subdirectories
2. For each subdirectory that contains both `migrations/` and `queries/` folders:
    - Creates an SQLC configuration entry
    - Sets the package name as `{dirname}db` (e.g., `weave` → `weavedb`)
    - Sets the output directory as `weave/weavesql/{package}`
3. Generates a complete `sqlc.yaml` with all discovered databases

## Example Structure

Given this structure:

```
schema/weavesql/
├── weave/
│   ├── migrations/
│   └── queries/
└── llmx/
    ├── migrations/
    └── queries/
```

The tool will generate configurations for:

- `weave` → package `weavedb`, output to `weave/weavesql/weavedb`
- `llmx` → package `llmxdb`, output to `weave/weavesql/llmxdb`

## Generated Configuration

The tool generates sqlc.yaml with:

- The sqlc Python plugin (sqlc-gen-python_1.3.0)
- Both sync and async querier generation
- String enum support
- Query parameter limit of 2

## Integration with CI/CD

This tool is used in the GitHub Actions workflow to dynamically generate sqlc.yaml before running `sqlc generate`:

```yaml
- name: Generate sqlc configuration
  run: python tools/sqlcgen/sqlcgen.py

- name: Generate sql schema
  run: sqlc generate
```

## Using with Task

The project includes a Taskfile for common operations:

```bash
# Generate sqlc configuration
task generate-sqlc-config

# Generate all code (sqlc config + sqlc generate)
task generate

# Run tests for sqlcgen
task test-sqlcgen

# Clean generated files
task clean

# Show all available tasks
task --list
```

## Requirements

- Python 3.7+
- No external dependencies (uses only Python standard library)