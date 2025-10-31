<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.0 → 2.0.0
Modified Principles:
  - Principle III: "Test-First Discipline (NON-NEGOTIABLE)" → "CLI-First Design"
    Removed: Mandatory TDD requirement
    Added: CLI design and Python best practices focus
Added Sections:
  - Python-specific quality standards
  - CLI design principles
Removed Sections:
  - Test-First Discipline (replaced with optional testing guidance)
Templates Requiring Updates:
  ✅ plan-template.md - Updated Constitution Check gates, added Python CLI context
  ✅ spec-template.md - User story & acceptance criteria requirements (no changes needed)
  ✅ tasks-template.md - Removed test-first requirement, made tests optional
Follow-up TODOs: None
-->

# Spec Kit Constitution

## Core Principles

### I. Clarity Over Brevity

Every specification, plan, and task document MUST prioritize understandability over conciseness. Code,
templates, and prompts shall be explicit and self-documenting. Ambiguity is a defect.

**Non-negotiable rules:**

- All placeholders MUST include inline examples or guidance comments
- Template instructions MUST state what to do, not assume familiarity
- Error messages MUST include actionable remediation steps
- No acronyms without first-use expansion in user-facing content

**Rationale:** Users span experience levels; implicit knowledge creates barriers. Explicit guidance
reduces cognitive load, accelerates onboarding, and prevents misinterpretation that cascades into
implementation errors.

### II. User Story Independence

Each user story defined in specifications MUST be independently testable, implementable, and
deliverable as a vertical slice of functionality. No user story shall depend on another for basic
validation.

**Non-negotiable rules:**

- Every user story MUST have explicit priority labeling (P1, P2, P3, etc.)
- Every user story MUST include acceptance criteria in Given-When-Then format
- Every user story MUST document how it delivers standalone value
- Task breakdowns MUST organize work by user story to enable parallel development

**Rationale:** Independent stories enable incremental delivery, reduce integration risk, allow parallel
team work, and provide clear rollback boundaries. Prioritization ensures MVP focus and aligns effort
with business value.

### III. CLI-First Design

All features MUST be accessible via command-line interface. The CLI is the primary interface;
any additional interfaces (API, GUI) are secondary. Design for composability and scriptability.

**Non-negotiable rules:**

- Every feature MUST expose a CLI command or subcommand
- CLI commands MUST follow standard UNIX conventions (stdin/stdout/stderr)
- All commands MUST support `--help` flag with clear usage documentation
- Output MUST support both human-readable and machine-parseable formats (JSON, etc.)
- Exit codes MUST follow standard conventions (0=success, non-zero=error with meaningful codes)

**Rationale:** CLI-first ensures automation capability, scriptability, and composability with other
tools. It forces clear interface design and enables testing without complex UI setup. Git config
management requires precise, repeatable operations best expressed through command-line interfaces.

### IV. Template Consistency

All templates (spec, plan, tasks, checklists) MUST maintain structural and semantic consistency.
Changes to one template that affect related templates MUST propagate to maintain coherence.

**Non-negotiable rules:**

- Constitution changes MUST trigger template alignment review
- Placeholder conventions MUST be uniform (`[ALL_CAPS_IDENTIFIER]`)
- Section ordering MUST follow logical dependency flow (setup → requirements → implementation)
- Examples in templates MUST reflect actual project patterns, not abstract placeholders

**Rationale:** Consistency reduces decision fatigue, enables automation, prevents drift between
artifacts, and ensures predictable tooling behavior across features.

### V. Specification Completeness

Feature specifications MUST be complete before planning begins. Plans MUST be complete before task
generation. Tasks MUST be complete before implementation. No phase-skipping without explicit
documentation of risk acceptance.

**Non-negotiable rules:**

- Specifications MUST pass checklist validation before `/speckit.plan` execution
- Plans MUST include Constitution Check results before task generation
- Tasks MUST map to user stories and design artifacts before `/speckit.implement`
- Any "NEEDS CLARIFICATION" marker blocks downstream phases until resolved

**Rationale:** Incomplete upstream artifacts cause rework, scope creep, and implementation churn.
Forcing completeness at each gate ensures decisions are made deliberately with full context, not
reactively during coding.

## Quality Standards

### Documentation Quality

- All templates MUST include ACTION REQUIRED markers for user-replaceable content
- All prompts MUST specify their inputs, outputs, and execution context
- All placeholders MUST be replaced or explicitly marked as deferred with justification
- All examples MUST use realistic project data, not generic "foo/bar" abstractions

### Code Quality (Python-specific)

- All file paths in task descriptions MUST be absolute and concrete
- All dependencies MUST be versioned explicitly in `pyproject.toml` or `requirements.txt`
- All error handling MUST include logging with structured context
- All breaking changes MUST increment version according to semantic versioning
- Python code MUST follow PEP 8 style guidelines
- Type hints MUST be used for all public functions and methods
- Docstrings MUST be provided for all modules, classes, and public functions (Google or NumPy style)

### CLI Quality

- All CLI commands MUST have comprehensive help text
- Error messages MUST be actionable and suggest next steps
- Commands MUST be composable (output of one can be input to another)
- Configuration MUST support environment variables and config files
- Sensitive data (credentials, tokens) MUST never be logged or displayed without explicit user consent

### Testing (Optional but Recommended)

While not mandatory, testing is strongly encouraged:

- Unit tests for core business logic and utilities
- Integration tests for CLI commands end-to-end
- Fixtures for common test data and scenarios
- Use pytest as the testing framework when tests are written

## Development Workflow

### Phase Gates

1. **Specification Gate**: Checklist must pass before planning
2. **Constitution Gate**: Plan must pass Constitution Check before tasks
3. **Design Gate**: Tasks must reference concrete design artifacts (contracts, data models)
4. **Implementation Gate**: CLI interface must be designed before implementation begins

### Amendment Process

Constitution changes require:

1. Version increment with documented rationale (MAJOR/MINOR/PATCH decision)
2. Sync Impact Report prepended as HTML comment to constitution file
3. Template consistency validation across plan, spec, tasks, and command prompts
4. Update of LAST_AMENDED_DATE to change date (ISO 8601 format)

### Complexity Justification

Any violation of core principles MUST be documented in the "Complexity Tracking" section of the
implementation plan with:

- Specific principle violated
- Business/technical reason requiring violation
- Mitigation strategy to minimize impact
- Revisit timeline for remediation

## Governance

This constitution supersedes all other development practices. Conflicts between this document and
external guidance resolve in favor of constitution unless explicitly amended.

**Compliance Requirements:**

- All phases (`/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`) MUST
  validate against applicable principles
- All code reviews MUST check Constitution Check compliance in plan documents
- All template updates MUST verify consistency with constitution principles
- Complexity justifications MUST be reviewed during feature retrospectives

**Enforcement:**

- Constitution violations discovered during `/speckit.analyze` are CRITICAL severity
- Amendments require explicit version increment and propagation validation
- Template drift (inconsistency across spec/plan/tasks templates) blocks feature approval

**Versioning Policy:**

- MAJOR: Principle removal, redefinition, or new non-negotiable constraint
- MINOR: New principle added, section expanded, new quality gate introduced
- PATCH: Clarification, wording improvement, typo fix, example refinement

**Version**: 2.0.0 | **Ratified**: 2025-10-31 | **Last Amended**: 2025-10-31
