# Quickstart Guide: Git Config CLI

## Prerequisites

- Python 3.11 or newer installed (`python3 --version`).
- Git installed and available on `PATH`.
- `uv` package manager installed (`pip install uv` or follow the [uv installation guide](https://docs.astral.sh/uv/installation/)).

## Project Setup

```bash
# Clone the repository
git clone <repo-url>
cd git-config-cli

# Create and activate virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (resolves via pyproject.toml)
uv pip install -e .

# Verify CLI is available
gitcfg --help
```

## Configuration Metadata Refresh

```bash
# Regenerate category metadata after editing metadata files
gitcfg list-categories --format json > /tmp/categories.json
```

## Common Workflows

### View consolidated configuration

```bash
gitcfg view
```

- Displays Rich-formatted table with scope-aware highlighting.
- Use `--format json` to export data for automation.

### View configuration for a single category

```bash
gitcfg view --category user-identity
```

### Filter by keyword (case-insensitive)

```bash
gitcfg view --search email
```

### Set values with guidance

```bash
# Set your global email
gitcfg set user.email "dev@example.com" --scope global

# Interactive mode (prompts for value and scope)
gitcfg set user.name --interactive
```

### Unset values

```bash
# Remove the local override of user.email
gitcfg unset user.email --scope local
```

### Explore categories/bundles

```bash
gitcfg list-categories
```

## Development Tips

- Run `uv pip install -e .[dev]` to include optional dev dependencies (e.g., pytest, ruff).
- Execute `pytest` to run unit and integration tests once they are implemented.
- Use `uv lock` to refresh lock files after dependency updates.
- Follow the data model in `specs/001-git-config-cli/data-model.md` to ensure CLI output matches JSON schema.
