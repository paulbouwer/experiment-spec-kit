---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Constitution Alignment**:

- **CLI-First Design**: All features must expose CLI commands with proper help text, UNIX conventions,
  and support for both human-readable and machine-parseable output formats.
- **User Story Independence**: Tasks are organized by user story to enable independent implementation.
  Each story phase can be developed, tested, and delivered separately.
- **Specification Completeness**: This file should only be generated after plan.md passes Constitution Check.
- **Clarity Over Brevity**: All task descriptions include exact file paths and concrete actions.

**Tests**: Tests are OPTIONAL but recommended. If you choose to write tests, organize them logically
(unit tests for core logic, integration tests for CLI commands) and use pytest as the testing framework.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Python CLI project**: `src/[package_name]/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume Python CLI project - adjust based on plan.md structure
- Use absolute paths from repository root (e.g., `src/gitconfig/cli/commands/get.py`)

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create Python project structure per implementation plan in src/[package_name]/
- [ ] T002 Initialize pyproject.toml with dependencies (click/typer, gitpython)
- [ ] T003 [P] Configure linting (ruff/flake8), formatting (black), and type checking (mypy)
- [ ] T004 [P] Create README.md with installation and usage instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T005 Create CLI entry point in src/[package_name]/\_\_main\_\_.py
- [ ] T006 Setup CLI framework (click/typer) in src/[package_name]/cli/main.py
- [ ] T007 Implement error handling and logging infrastructure
- [ ] T008 Create configuration management (env vars, config files)
- [ ] T009 [P] Setup base models in src/[package_name]/core/models.py
- [ ] T010 [P] Add --help support and version command

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own - e.g., "Run `[command] --help` and verify output"]

### Implementation for User Story 1

- [ ] T011 [P] [US1] Create [Entity1] model in src/[package_name]/core/models.py
- [ ] T012 [P] [US1] Implement core logic in src/[package_name]/core/[feature].py
- [ ] T013 [US1] Create CLI command in src/[package_name]/cli/commands/[command].py
- [ ] T014 [US1] Add command to main CLI router in src/[package_name]/cli/main.py
- [ ] T015 [US1] Add validation and error handling with user-friendly messages
- [ ] T016 [US1] Add logging for user story 1 operations
- [ ] T017 [US1] Add --help documentation for the command

### Tests for User Story 1 (OPTIONAL - include if writing tests) ⚠️

- [ ] T018 [P] [US1] Unit test for core logic in tests/unit/test_[feature].py
- [ ] T019 [P] [US1] Integration test for CLI command in tests/integration/test_cli_[command].py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Implementation for User Story 2

- [ ] T020 [P] [US2] Create [Entity] model in src/[package_name]/core/models.py
- [ ] T021 [P] [US2] Implement core logic in src/[package_name]/core/[feature].py
- [ ] T022 [US2] Create CLI command in src/[package_name]/cli/commands/[command].py
- [ ] T023 [US2] Add command to CLI router and integrate with User Story 1 (if needed)
- [ ] T024 [US2] Add validation, error handling, and --help documentation

### Tests for User Story 2 (OPTIONAL - include if writing tests) ⚠️

- [ ] T025 [P] [US2] Unit test for core logic in tests/unit/test_[feature].py
- [ ] T026 [P] [US2] Integration test for CLI command in tests/integration/test_cli_[command].py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create [Entity] model in src/[package_name]/core/models.py
- [ ] T028 [P] [US3] Implement core logic in src/[package_name]/core/[feature].py
- [ ] T029 [US3] Create CLI command in src/[package_name]/cli/commands/[command].py
- [ ] T030 [US3] Add command to CLI router with full documentation

### Tests for User Story 3 (OPTIONAL - include if writing tests) ⚠️

- [ ] T031 [P] [US3] Unit test for core logic in tests/unit/test_[feature].py
- [ ] T032 [P] [US3] Integration test for CLI command in tests/integration/test_cli_[command].py

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests (if requested) in tests/unit/
- [ ] TXXX Security hardening
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
