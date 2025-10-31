# Research Summary: Git Config CLI

## Decision Log

### Decision: Use `rich` for terminal UI rendering

- **Rationale**: `rich` provides high-level abstractions for colorized output, tree/table layouts, and interactive prompts that align with the "pretty CLI" requirement inspired by charmbracelet and Claude Code. It is mature, well-documented, and works seamlessly across Linux, macOS, and Windows terminals.
- **Alternatives considered**:
  - `textual`: richer UI framework but introduces an app loop model that is heavier than needed for a CLI-focused tool.
  - `blessed`/`curses`: low-level control requiring significant custom rendering effort.
  - Plain ANSI formatting: would require bespoke layout code and lack reusable components.

### Decision: Build CLI with `typer`

- **Rationale**: `typer` layers on top of Click with type hints, auto-generated help, and nested command support. It enforces good UX for `--help` and integrates well with Python dataclasses/Pydantic.
- **Alternatives considered**:
  - `click`: solid foundation but more boilerplate; Typer already uses Click underneath.
  - `argparse`: standard library but limited in subcommand ergonomics and help formatting.
  - `python-fire`: fast scaffolding but less control over UX and help text.

### Decision: Manage dependencies with `uv`

- **Rationale**: `uv` meets the requirement for modern package management with fast dependency resolution, built-in virtualenv management, and lock file generation. It integrates nicely with `pyproject.toml` and can export requirements for CI pipelines.
- **Alternatives considered**:
  - `poetry`: popular but slower dependency resolution and heavier runtime dependency.
  - `pip-tools`: excellent for pinning but still relies on pip + venv generic workflow.
  - Raw `pip` + `venv`: lightweight but lacks lockfile and reproducibility features expected for this tool.

### Decision: Invoke native `git` commands via subprocess

- **Rationale**: Using `git config` directly honors the instruction to "leverage the git commands" and guarantees parity with Gitʼs behavior. It avoids discrepancies that can occur with libraries that re-implement config parsing.
- **Alternatives considered**:
  - `gitpython`: convenient but adds large dependency surface and lags behind git feature parity.
  - Manual parsing of `.gitconfig`: fragile because Git merges multiple files with include rules and precedence.

### Decision: Define config "bundles" via curated metadata

- **Rationale**: Bundling related keys (e.g., user identity, core behavior, remotes) creates a guided experience. Metadata will live in `core/categories.py` mapping keys to categories with descriptions and recommended combinations.
- **Alternatives considered**:
  - Pure prefix-based grouping: simple but misses relationships (e.g., `credential.helper` vs `credential.useHttpPath`).
  - User-defined categories only: flexible but fails the guidance requirement from the spec.
  - Hard-coded per-command grouping: leads to duplication and harder evolution.

### Decision: Represent effective configuration with layered model

- **Rationale**: A layered model (system → global → local) with flags for "active" vs "overridden" directly supports the UI requirement to highlight precedence. This mirrors Gitʼs own precedence rules.
- **Alternatives considered**:
  - Flat list with scope column: harder to read and reason about overrides.
  - Tree per scope without merge indicators: fails requirement to show which value is active when multiple scopes define the same key.

## Open Questions Resolved

No outstanding clarifications remain; all specification requirements have concrete technical answers.
