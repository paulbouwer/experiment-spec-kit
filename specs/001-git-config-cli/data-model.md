# Data Model: Git Config CLI

## Overview

The data model captures Git configuration entries across scopes, associated metadata, and grouping structures required to render the CLI view and perform set/unset operations. All entities are represented as Pydantic models to leverage validation and serialization.

## Entities

### ConfigScope (Enum)

- **Values**: `system`, `global`, `local`
- **Description**: Represents the scope from which a configuration entry originates. Ordered by precedence (system < global < local).

### ScopeMetadata

- **Fields**:
  - `scope: ConfigScope`
  - `path: Path` — absolute path to the config file providing the value
  - `is_writable: bool` — indicates whether the CLI can modify values at this scope
- **Validation Rules**:
  - `path` must exist for scopes detected in `git config --list --show-origin`
  - `is_writable` defaults to `False` when the CLI lacks write permissions

### ConfigEntry

- **Fields**:
  - `key: str` — dot-delimited identifier (`section.name`), validated via regex `^[A-Za-z0-9.\-]+$`
  - `value: str` — raw string value (preserve whitespace and quotes)
  - `scope: ConfigScope`
  - `origin: Path` — file path from `--show-origin`
  - `category_id: str` — identifier referencing `ConfigCategory.id`
  - `is_active: bool` — true when this entry is the effective value for the key (highest precedence among scopes)
  - `overridden_by: list[ConfigScope]` — scopes that override this entry (empty when `is_active`)
  - `annotations: list[str]` — optional messages (e.g., “Value inherited from global scope”)
- **Validation Rules**:
  - `category_id` must reference a defined category
  - `origin` must be canonicalized to avoid duplicates
  - `overridden_by` cannot contain scopes lower or equal in precedence than `scope`

### EffectiveConfig

- **Fields**:
  - `key: str`
  - `active_entry: ConfigEntry`
  - `all_entries: list[ConfigEntry]` — sorted low-to-high precedence
- **Purpose**: Aggregates entries for a key to simplify rendering layered views and determining effective values.

### ConfigCategory

- **Fields**:
  - `id: str` — slug (e.g., `user-identity`)
  - `name: str`
  - `description: str`
  - `keys: list[str]` — canonical keys included in the category
  - `related_categories: list[str]` — optional hints for navigation
- **Default Categories**:
  - `user-identity`: `user.name`, `user.email`, `user.signingkey`
  - `core-behavior`: `core.editor`, `core.autocrlf`, `core.ignorecase`
  - `remote-settings`: `remote.*`, `branch.*`
  - `credential-management`: `credential.helper`, `credential.useHttpPath`
  - `safety`: `commit.gpgSign`, `pull.rebase`
- **Validation Rules**:
  - `keys` entries use wildcard support (`remote.*`) via glob matching
  - No duplicate `id`

### CategoryBundle

- **Fields**:
  - `id: str`
  - `name: str`
  - `description: str`
  - `categories: list[ConfigCategory]`
- **Purpose**: Provides higher-level grouping (“Starter Identity Setup”) to surface recommended combinations or flows.

### ConfigSnapshot

- **Fields**:
  - `scopes: dict[ConfigScope, ScopeMetadata]`
  - `entries: list[ConfigEntry]`
  - `effective_map: dict[str, EffectiveConfig]`
  - `generated_at: datetime`
- **Purpose**: Represents the CLI’s current view of Git configuration, enabling consistent rendering, filtering, and JSON export.
- **Validation Rules**:
  - `effective_map` must contain every unique key present in `entries`
  - `entries` keys must be unique per `(key, scope)` combination

### SetRequest

- **Fields**:
  - `key: str`
  - `value: str`
  - `scope: ConfigScope`
- **Validation Rules**:
  - `scope` must be writable
  - `key` must conform to Git key format
  - Provide hooks to validate value suggestions (e.g., email format for `user.email`)

### UnsetRequest

- **Fields**:
  - `key: str`
  - `scope: ConfigScope`
- **Validation Rules**:
  - Entry must exist at requested scope before execution

## Relationships

- `ConfigSnapshot.entries` references many `ConfigEntry` objects.
- `ConfigEntry.category_id` links to `ConfigCategory` for grouping.
- `ConfigCategory` items can be organized into optional `CategoryBundle` objects presented in help/education flows.
- `EffectiveConfig.active_entry` ensures the CLI can highlight effective values, with `all_entries` preserving scope layering for tooltips and drill-down views.

## Data Flow

1. **Acquisition**: Run `git config --list --show-scope --show-origin` and parse output into raw tuples.
2. **Normalization**:
   - Map scope strings (`system`, `global`, `local`) to `ConfigScope`.
   - Derive `category_id` using category metadata (exact or wildcard matches).
3. **Aggregation**:
   - Build `EffectiveConfig` per unique key with precedence ordering.
   - Mark `is_active` and populate `overridden_by` lists.
4. **Presentation**:
   - Serialize `ConfigSnapshot` for CLI view (Rich tables) and JSON export.
   - Provide filtered slices based on scope/category/keyword queries.
5. **Mutation**:
   - Validate `SetRequest`/`UnsetRequest`, execute git command, refresh `ConfigSnapshot`.

## Validation & Error Handling

- Detect conflicting encodings by checking for duplicate keys with identical scope and origin.
- Highlight unsupported binary values (Git treats as strings; CLI should flag probable misuse).
- Fail fast if Git executable is unavailable or returns non-zero exit code, surfacing actionable error messages.
- When category metadata lacks an entry for a key, assign fallback category `uncategorized` with descriptive text explaining manual categorization options.
