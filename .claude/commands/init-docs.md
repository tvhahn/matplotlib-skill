---
description: Initialize project documentation from templates
---

Your task is to generate a documentation suite for this project by scanning the codebase and producing four interconnected doc files. Follow each phase in order.

## Phase 1: Gather project data

Scan these locations in parallel and note your findings:

| What | How |
|------|-----|
| Source modules | Glob `src/**/*.py` — note module names, classes, functions, imports |
| Test files | Glob `tests/**/*.py` — note test classes, coverage areas |
| Dev scripts | Glob `dev/*.py` — read docstrings for purpose |
| Dev examples | Glob `dev/examples/*.py` — read docstrings for purpose |
| Slash commands | Glob `.claude/commands/*.md` — read frontmatter `description` from each |
| Spec directories | Glob `docs/specs/*/` — read titles and status from each spec |
| Config files | Read `pyproject.toml` — note dependencies, project metadata |
| Environment | Read `.env.example` or scan source for `os.environ` / `os.getenv` calls |
| Existing docs | Read `CLAUDE.md`, `docs/guides/*.md` — understand what's already documented |

## Phase 2: Generate `docs/ARCHITECTURE.md`

Create this file with these sections:

1. **System Overview** — ASCII diagram showing data flow from inputs through processing modules to outputs
2. **Module sections** — One section per `src/` subpackage. Each section has:
   - File table: `| File | Purpose | Key Classes/Functions |`
   - Design notes explaining non-obvious decisions
3. **Anatomy of a [Primary Operation]** — Numbered walkthrough of the main pipeline's steps
4. **Controlled Vocabulary** — Table of any Enum classes: `| Enum | Values | Purpose |`
5. **Validation Checks** — Table: `| Check | Severity | What It Catches |`
6. **External Integrations** — Table: `| Service | Library | Usage |`
7. **Design Decisions** — Bullet list of key architectural choices with rationale
8. **Configuration** — Table: `| Setting | Location | Notes |` covering env vars and CLI flags

## Phase 3: Generate `docs/TESTS.md`

Create this file with these sections:

1. **Quick Start** — `uv run pytest` commands (all tests, single file, verbose)
2. **Unit Tests** — Table: `| File | Tests | Coverage |` with brief descriptions of what each test file covers
3. **Test Data & Fixtures** — List any test data files, fixtures, factory functions
4. **Dev Scripts Reference** — Table: `| Script | Purpose | Usage |` for files in `dev/`
5. **Dev Examples (Cookbook)** — Table: `| Script | Purpose | Usage |` for files in `dev/examples/` with note about `--execute` flag if applicable

## Phase 4: Generate `docs/specs/INDEX.md`

Create a spec registry table:

```
| Spec | Title | Status | Date |
|------|-------|--------|------|
```

Populate from the spec directories found in Phase 1. Read each spec's frontmatter or header for title and status.

## Phase 5: Generate `docs/guides/slash-commands.md`

Create this file with:

1. **Quick Reference** — Table: `| Command | Description |` for all commands found in Phase 1
2. **Grouped sections** by category (Development Workflow, Code Generation, Analysis, Documentation, Utility) — each command gets a paragraph explaining when/how to use it

## Rules

- Use consistent markdown formatting: ATX headers, pipe tables, fenced code blocks
- Keep tables aligned with consistent column widths
- Use relative paths from the project root in all file references
- Do not invent information — only document what you find in the source code
- If a section would be empty (e.g., no Enum classes found), omit it
- After creating all files, report what you generated
