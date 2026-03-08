---
description: Audit project documentation for drift against source code and fix discrepancies
---

Your task is to audit project documentation against the actual source code, find discrepancies, and fix them.

## Phase 1: Gather ground truth

Scan these source locations (in parallel where possible):

| What | How |
|------|-----|
| Unit test files | Glob `tests/unit/test_*.py` |
| Dev scripts | Glob `dev/*.py` |
| Parser files | Glob `src/emails/parsers/*_parser.py` (exclude `__init__.py`, `common_parser.py`, `etransfer_parser.py`) |
| Config files | Glob `src/emails/config/*.json` |
| Category list | Read `src/emails/config/categories.json` — count entries, note the full list |
| Slash commands | Glob `.claude/commands/*.md` — read frontmatter `description` from each |
| Spec directories | Glob `docs/specs/*/` — list directory names |
| Source modules | Glob `src/emails/*.py` |

## Phase 2: Read current documentation

Read these doc files:
- `docs/TESTS.md`
- `docs/ARCHITECTURE.md`
- `docs/specs/INDEX.md`
- `docs/guides/slash-commands.md`
- `CLAUDE.md`

## Phase 3: Compare and identify drift

Perform each of these checks explicitly:

### TESTS.md
1. Compare unit test files on disk vs the **Unit Tests** table — find missing or stale rows
2. Compare dev scripts on disk vs the **Dev Scripts Reference** table — find missing or stale rows

### ARCHITECTURE.md
3. Compare category count in `categories.json` vs the number stated in the "N predefined categories" text
4. Compare category names in `categories.json` vs the blockquote category list
5. Compare parser files on disk vs the **Parser Capabilities** table
6. Compare config files on disk vs the **Configuration** table
7. Review the DynamoDB schema table against attribute names used in `src/emails/transaction_db.py`

### specs/INDEX.md
8. Compare spec directories on disk vs the spec registry table

### CLAUDE.md
9. Verify all `@docs/...` references point to files that exist
10. Check if any important doc files in `docs/` are not referenced

### docs/guides/slash-commands.md
11. Check if any new category-management or doc-management slash commands exist that should be documented

### Semantic review
12. Read recent git log (`git log --oneline -20`) and assess whether any recent changes introduced features not reflected in ARCHITECTURE.md prose sections

## Phase 4: Fix discrepancies

### Auto-fix (apply without asking):
- Add missing rows to tables (read the source file to write a brief description)
- Remove stale rows from tables (files that no longer exist)
- Update category count numbers
- Update category blockquote list
- Add missing spec entries to INDEX.md

### Ask the user (via `AskUserQuestion`):
- Prose-level changes — new sections needed in ARCHITECTURE.md
- Ambiguous cases where the right fix isn't obvious
- Removing or restructuring existing content

### Print summary at the end:
- List each fix applied with file and section
- List any items flagged for user attention
- Note docs that are fully up to date
