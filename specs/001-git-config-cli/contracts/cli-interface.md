# CLI Contracts: Git Config CLI

## Overview

All commands are implemented with Typer and conform to UNIX CLI principles. Commands support `--help`, exit codes (0 success, non-zero for errors), and provide both human-readable (Rich) and JSON outputs.

### Application Lifecycle

- Root entrypoint `gitcfg` wires a shared Typer context storing the active `rich` console and verbose flag.
- `--verbose` elevates logging to DEBUG and surfaces executed git commands via the subprocess helper.
- Global styling derives from a centralized Rich theme to keep scope colors and status messaging consistent.

## Common Options

- `--scope [system|global|local]`: Target scope for set/unset operations and optional filter for view.
- `--format [pretty|json]`: Output style for view-like commands. Defaults to `pretty` (Rich tables); `json` returns machine-parseable data identical to the `ConfigSnapshot` schema.
- `--verbose`: When enabled, displays diagnostic messages (git commands executed, timing, and file paths).
- `--help`: Shows usage information and examples.

## Command: `gitcfg view`

- **Purpose**: Display consolidated Git configuration across scopes with visual grouping and precedence indicators.
- **Usage**: `gitcfg view [--scope system|global|local] [--category <id>] [--search <keyword>] [--format pretty|json]`
- **Arguments**: None.
- **Options**:
  - `--scope`: Filter results to one scope; defaults to showing all scopes layered.
  - `--category`: Limits output to a specific `ConfigCategory.id` (e.g., `user-identity`).
  - `--search`: Case-insensitive substring filter matching keys or values.
  - `--format`: See common options.
- **Successful Output (pretty)**:
  - Rich table with columns: Category, Key, Active Value, Scope, Overrides, Description, Origin.
  - Color coding per scope (system=cyan, global=green, local=magenta) and strike-through for overridden values.
- **Successful Output (json)**:
  - Serialized `ConfigSnapshot` (scopes, entries, effective_map) limited by filters.
- **Errors**:
  - Exit code `2` when git command fails (e.g., git not installed). Message: `Unable to read git configuration: <stderr>`.
  - Exit code `3` for invalid category (message guides user to `gitcfg list-categories`).
  - Exit code `4` when run outside a repository and `--scope local` requested (message: `Local scope unavailable outside a Git repository`).

## Command: `gitcfg set`

- **Purpose**: Write a Git configuration key/value pair at the specified scope with guided prompts.
- **Usage**: `gitcfg set <key> <value> [--scope system|global|local] [--interactive]`
- **Arguments**:
  - `key` (required): Git configuration key (e.g., `user.email`).
  - `value` (required): Value to assign. Quoting preserved as passed.
- **Options**:
  - `--scope`: Target scope; defaults to `global`. Validated for writability.
  - `--interactive`: When set, prompts for value and scope with suggestions (useful when `value` omitted).
  - `--dry-run`: Display command that would run without applying changes.
- **Successful Output (pretty)**:
  - Confirmation banner showing key, value, scope, origin path.
  - Updated snippet from `gitcfg view --scope <scope> --search <key>` to verify change.
- **Successful Output (json)**:
  - `{ "status": "updated", "scope": "global", "key": "user.email", "origin": "~/.gitconfig" }`
- **Errors**:
  - Exit code `2` when scope not writable (message references permission fix).
  - Exit code `3` for invalid key format (message includes regex and example).
  - Exit code `4` when git returns non-zero; show stderr.
  - Exit code `5` when local scope requested outside repository (align with view error).

## Command: `gitcfg unset`

- **Purpose**: Remove a Git configuration key from the specified scope with clear confirmation.
- **Usage**: `gitcfg unset <key> [--scope system|global|local] [--force]`
- **Arguments**:
  - `key` (required): Git configuration key to remove.
- **Options**:
  - `--scope`: Scope to remove from; defaults to `local` when inside repo, else `global`.
  - `--force`: Skip confirmation prompt (useful for scripting).
  - `--dry-run`: Show pending removal without executing.
- **Successful Output (pretty)**:
  - Confirmation message stating removal and showing next effective value (if any).
  - Visual diff between previous snapshot and new effective value.
- **Successful Output (json)**:
  - `{ "status": "removed", "key": "user.email", "scope": "local", "fallback_scope": "global" }`
- **Errors**:
  - Exit code `2` when key does not exist at target scope (message: `No value found for user.email at local scope`).
  - Exit code `3` for git failure; include stderr.

## Command: `gitcfg list-categories`

- **Purpose**: Provide documentation of config bundles/categories and recommended property groupings.
- **Usage**: `gitcfg list-categories [--format pretty|json]`
- **Arguments**: None.
- **Options**:
  - `--format`: See common options.
- **Successful Output (pretty)**:
  - Rich table listing Category Name, Description, Included Keys, Suggested Next Steps.
  - Additional callouts for bundles (e.g., “Starter Identity Setup” showing recommended order: set `user.name` → `user.email` → `commit.gpgSign`).
- **Successful Output (json)**:
  - `{ "categories": [...], "bundles": [...] }` matching `ConfigCategory` and `CategoryBundle` schemas.
- **Errors**:
  - Exit code `2` for unexpected failures when loading metadata (should be rare; message instructs filing an issue).

## JSON Schema Reference

JSON output conforms to the Pydantic models defined in `data-model.md`. Key contracts:

- `ConfigSnapshot` structure for `view` command.
- `ConfigCategory` and `CategoryBundle` payloads for `list-categories` command.
- Mutation responses (`set`, `unset`) return status objects with `status`, `key`, `scope`, and contextual fields (e.g., `origin`, `fallback_scope`).
