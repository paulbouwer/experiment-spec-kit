# Tasks: Git Config CLI

**Input**: Design documents from `/specs/001-git-config-cli/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Constitution Alignment**:

- **CLI-First Design**: All features expose Typer-powered commands with rich terminal output, JSON export, and conventional exit codes.
- **User Story Independence**: Tasks are grouped per user story so each increment can ship and be tested on its own.
- **Specification Completeness**: Generated after plan.md passed the Constitution Check.
- **Clarity Over Brevity**: Every task lists concrete file paths and expected actions.

**Tests**: Optional but encouraged. Place unit tests under `tests/unit/` and CLI integration tests under `tests/integration/` using pytest.

**Organization**: Tasks run sequentially by phase, then by user story priority. Items tagged `[P]` can proceed in parallel once their phase prerequisites finish.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Task operates on independent files and can run in parallel.
- **[Story]**: `US1`, `US2`, `US3`, `US4` map to spec user stories.
- Include exact repository paths in each description.

## Path Conventions

- Package root: `src/gitcfg/`
- CLI commands: `src/gitcfg/cli/commands/`
- Core logic & models: `src/gitcfg/core/`
- UI helpers: `src/gitcfg/ui/`
- Utilities: `src/gitcfg/utils/`
- Tests: `tests/unit/` and `tests/integration/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish project metadata, package skeleton, and developer tooling baseline.

- [X] T001 Create `pyproject.toml` with `gitcfg` project metadata, Typer/Rich/Pydantic dependencies, and `dev` optional-dependencies for pytest and ruff.
- [X] T002 [P] Create package directories and placeholder modules (`src/gitcfg/__init__.py`, `src/gitcfg/__main__.py`, `src/gitcfg/cli/__init__.py`, `src/gitcfg/cli/commands/__init__.py`, `src/gitcfg/core/__init__.py`, `src/gitcfg/ui/__init__.py`, `src/gitcfg/utils/__init__.py`).
- [X] T003 [P] Add repo-level developer ergonomics (`ruff.toml`, `pytest.ini`, update `.gitignore`) aligned with plan.md quickstart guidance.
- [X] T004 [P] Update `README.md` root section to reference quickstart instructions from `specs/001-git-config-cli/quickstart.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Wire core infrastructure required by every user story before feature work begins.

- [X] T101 Implement Typer application bootstrap in `src/gitcfg/cli/app.py` exposing root command and shared options.
- [X] T102 [P] Wire module entry point in `src/gitcfg/__main__.py` to invoke the Typer app.
- [X] T103 [P] Build subprocess utilities in `src/gitcfg/utils/subprocess_helper.py` to execute git commands with error handling and timeouts.
- [X] T104 Define Pydantic models from `data-model.md` in `src/gitcfg/core/models.py` and ensure JSON serialization helpers exist.
- [X] T105 [P] Capture category metadata tables in `src/gitcfg/core/categories.py`, including wildcard matching helpers and bundle definitions.
- [X] T106 [P] Create shared Rich presentation utilities in `src/gitcfg/ui/themes.py` and `src/gitcfg/ui/formatters.py` for consistent styling.
- [X] T107 Establish logging/error scaffolding in `src/gitcfg/utils/validators.py` (input validation) and shared exceptions in `src/gitcfg/core/exceptions.py`.
- [X] T108 [P] Document CLI contract stubs in `specs/001-git-config-cli/contracts/cli-interface.md` to match foundational command signatures.

**Checkpoint**: Foundation ready – user story implementation may proceed.

---

## Phase 3: User Story 1 - View Consolidated Git Configuration (Priority: P1) 🎯 MVP

**Goal**: Deliver the rich `gitcfg view` experience showing layered scopes, categories, and descriptions.

**Independent Test**: Run `gitcfg view --format table` inside a repo with scoped overrides and confirm Rich table highlights active values, origins, and category groupings. Verify `gitcfg view --format json` emits the EffectiveConfig schema.

### Implementation for User Story 1

- [X] T201 Implement git config read pipeline in `src/gitcfg/core/git_config.py` leveraging subprocess helper to gather scoped output.
- [X] T202 [P] Parse git output into data models in `src/gitcfg/core/parser.py`, populating `ConfigEntry`, `EffectiveConfig`, and override metadata.
- [X] T203 [P] Build category resolution and bundle summaries in `src/gitcfg/core/categories.py`, ensuring uncategorized fallback behavior.
- [X] T204 Compose Rich table renderer in `src/gitcfg/ui/tables.py` to visualize categories, scopes, and overrides.
- [X] T205 [P] Add JSON serialization/export helper in `src/gitcfg/ui/formatters.py` for `ConfigSnapshot` responses.
- [X] T206 Implement `view` command in `src/gitcfg/cli/commands/view.py` with options for `--format`, `--category`, `--scope`, and `--search` (filters stubbed until US4).
- [X] T207 Register `view` command inside `src/gitcfg/cli/app.py` and ensure `--help` text matches contracts.
- [X] T208 Provide error messaging for missing git contexts (outside repo) within `src/gitcfg/core/git_config.py` and propagate to CLI.

### Tests for User Story 1 (OPTIONAL)

- [X] T209 [P] [US1] Unit tests for parser behavior in `tests/unit/test_parser.py` covering scope precedence and wildcard categories.
- [X] T210 [US1] Integration test for `gitcfg view` in `tests/integration/test_cli_view.py` using temporary git repo fixtures.

**Checkpoint**: `gitcfg view` command delivers core MVP functionality.

---

## Phase 4: User Story 2 - Set Configuration Values (Priority: P2)

**Goal**: Allow developers to set configuration keys at selected scopes with guidance and immediate feedback.

**Independent Test**: Run `gitcfg set user.email dev@example.com --scope global` and confirm git global config updates, CLI response highlights change, and subsequent `gitcfg view` reflects new value.

### Implementation for User Story 2

- [ ] T301 Extend mutation support in `src/gitcfg/core/git_config.py` with `set_value` handling scope detection, permissions, and refresh.
- [ ] T302 [P] Add value validation hooks in `src/gitcfg/utils/validators.py` (e.g., email format, known keys) and integrate with categories metadata.
- [ ] T303 [P] Implement interactive prompting helpers in `src/gitcfg/ui/formatters.py` (or new `prompts.py`) for optional guided flows.
- [ ] T304 Create `set` command in `src/gitcfg/cli/commands/set.py` supporting positional `key`, optional `value`, `--scope`, and `--interactive` flags.
- [ ] T305 Update `src/gitcfg/cli/app.py` to include `set` command and ensure help text describes scope restrictions and confirmation output.
- [ ] T306 Refresh `specs/001-git-config-cli/contracts/cli-interface.md` to capture final argument/option names and responses for `set`.

### Tests for User Story 2 (OPTIONAL)

- [ ] T307 [P] [US2] Unit tests for set validation and scope enforcement in `tests/unit/test_set_validators.py`.
- [ ] T308 [US2] Integration test for `gitcfg set` in `tests/integration/test_cli_set.py` covering global vs local precedence.

**Checkpoint**: `gitcfg set` command operates independently with validation and feedback.

---

## Phase 5: User Story 3 - Unset Configuration Values (Priority: P3)

**Goal**: Enable removal of scoped configuration values with clear success/error messaging.

**Independent Test**: Run `gitcfg unset user.email --scope local` in a repo with overrides and confirm only the local key is removed while global remains.

### Implementation for User Story 3

- [ ] T401 Implement `unset_value` in `src/gitcfg/core/git_config.py` reusing subprocess helper and ensuring no-op handling when key absent.
- [ ] T402 [P] Enhance validators in `src/gitcfg/utils/validators.py` to guard against unsetting non-existent or read-only scopes.
- [ ] T403 Create `unset` command in `src/gitcfg/cli/commands/unset.py` mirroring contracts documented in phase 1.
- [ ] T404 Register `unset` command in `src/gitcfg/cli/app.py` with descriptive help and successful completion messaging.
- [ ] T405 Update CLI contracts file to capture unset response payloads and error cases.

### Tests for User Story 3 (OPTIONAL)

- [ ] T406 [P] [US3] Unit tests for unset safeguards in `tests/unit/test_unset_validators.py`.
- [ ] T407 [US3] Integration test for `gitcfg unset` in `tests/integration/test_cli_unset.py` verifying scope-specific removal.

**Checkpoint**: CRUD operations (view, set, unset) function independently.

---

## Phase 6: User Story 4 - Search and Filter Configuration (Priority: P4)

**Goal**: Provide keyword, scope, and category filters to streamline navigation of large configuration sets.

**Independent Test**: Execute `gitcfg view --scope global --search email --category user-identity` and confirm filtered output matches query parameters in both table and JSON modes.

### Implementation for User Story 4

- [ ] T501 Extend filter logic in `src/gitcfg/core/parser.py` or new `filters.py` to support scope/category/keyword queries against `ConfigSnapshot`.
- [ ] T502 [P] Update `src/gitcfg/ui/tables.py` to render filtered summaries while preserving layout and color semantics.
- [ ] T503 Enhance `src/gitcfg/cli/commands/view.py` to wire filter options, handle empty results, and surface helpful messages.
- [ ] T504 Refresh contracts documentation for filter capabilities and option defaults.

### Tests for User Story 4 (OPTIONAL)

- [ ] T505 [P] [US4] Unit tests for filter predicates in `tests/unit/test_filters.py`.
- [ ] T506 [US4] Integration test for combined filters in `tests/integration/test_cli_view_filters.py`.

**Checkpoint**: Advanced filtering enhances MVP without breaking prior stories.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, documentation, and final validation after story completion.

- [ ] T601 [P] Audit Rich theming and accessibility in `src/gitcfg/ui/themes.py`, ensuring color choices meet contrast expectations.
- [ ] T602 [P] Expand root `README.md` and `specs/001-git-config-cli/quickstart.md` with end-to-end usage examples and troubleshooting tips.
- [ ] T603 [P] Add end-to-end smoke script under `scripts/demo_gitcfg.sh` to showcase core flows.
- [ ] T604 Run `uv pip install -e .[dev]`, `ruff check src tests`, and `pytest` to validate the project before release.
- [ ] T605 Finalize changelog or release notes snippets under `docs/CHANGELOG.md` (create file if needed) summarizing feature readiness.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 → Phase 2**: Foundation work begins only after setup artifacts land.
- **Phase 2 → User Stories**: All user stories depend on the foundational Typer app, data models, and UI utilities.
- **User Stories**: Can proceed in priority order or in parallel once dependencies satisfied; none require future stories to start.
- **Phase 7**: Runs after desired user stories reach checkpoints.

### User Story Dependencies

- **US1**: First deliverable; unlocks config visualization used by later stories.
- **US2**: Depends on foundational git mutation support; integrates with US1 refresh pipeline but otherwise independent.
- **US3**: Shares infrastructure with US2; can develop after mutation scaffolding exists.
- **US4**: Extends US1 view command; begins after view command baseline is stable.

### Parallel Opportunities

- `[P]` tasks within the same phase avoid file conflicts and can be split across contributors.
- Tests marked `[P]` can be implemented concurrently with peer tasks once primary logic is ready.
- Different user stories may proceed in parallel post-foundation if targeted files do not collide (e.g., US2 set command vs US3 unset command).

### Implementation Strategy

1. Complete Phase 1 and Phase 2 sequentially to establish the CLI framework and data model.
2. Ship User Story 1 as the MVP; validate view pipelines thoroughly.
3. Layer in User Stories 2 and 3 for mutation capabilities, ensuring each passes its independent tests before merging.
4. Add User Story 4 filters last as an enhancement for power users.
5. Use Phase 7 to harden, document, and verify the CLI prior to release.
