# Iterate Skill

Run a single evaluation-improvement-documentation cycle on the matplotlib-chart skill.

## Workflow

### Step 1: Evaluate Current State

1. Read the skill files:
   - `.claude/skills/matplotlib-chart/SKILL.md`
   - `.claude/skills/matplotlib-chart/style-reference.md`
   - `.claude/skills/matplotlib-chart/chart-patterns.md`

2. Run static analysis for style compliance:
   ```bash
   uv run scripts/evaluate_skill.py --check-renders
   ```

3. Note the latest clean-room results directory (`logs/clean-room/latest/`) as the comparison baseline. If no previous run exists, note that this is the first run.

4. Record the "Before" automated check scores.

### Step 2: Identify Improvements

Select **1-2 areas** for improvement. Prioritize in this order:
1. Style compliance gaps (wrong theme, missing despine, incorrect DPI)
2. Pattern inconsistencies (different annotations, missing legend styling)
3. Code quality issues (deprecated API calls, unclear variable names)
4. Missing annotations or visual polish

Do NOT:
- Delete existing patterns
- Change `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")` — this is immutable
- Change `sns.despine(left=True, bottom=True)` — this is immutable
- Make changes that affect more than 3 patterns at once

### Step 3: Propose Changes

Write the proposed changes BEFORE making them. Create a structured evaluation:

```markdown
## Proposed Changes
| Pattern | File | Change | Confidence |
|---------|------|--------|------------|
| P3 | chart-patterns.md | Added rolling window annotation | High |
```

### Step 4: Apply Changes

Make targeted edits to skill files in `.claude/skills/matplotlib-chart/`.

### Step 5: Verify

1. Run static analysis for style compliance:
   ```bash
   uv run scripts/evaluate_skill.py --check-renders
   ```

2. Run the container-based skill test (Claude Code generates charts from minimal prompts in a Docker clean room):
   ```bash
   scripts/chart-test-container.sh --quick
   ```

3. Read the generated PNGs from the timestamped results directory (`logs/clean-room/latest/`) to visually inspect chart quality.

4. Read the generated Python scripts in each results subdirectory to confirm style conventions (`sns.set_theme`, `sns.despine`).

5. Record "After" automated check scores.

6. **Regression detection**: If the container script exits nonzero (any prompt produced zero charts), or generated code is missing `sns.set_theme`/`sns.despine`, halt and explain why.

### Step 6: Document

Determine the next gallery entry number by looking at `docs/gallery/` and create:

1. Create `docs/gallery/NN-description/` folder
2. Copy relevant PNGs from the clean-room results directory (`logs/clean-room/latest/`) into the gallery folder
3. Write `README.md` following this format:

```markdown
# [NN] — [Short Title]

## What Changed
- Bullet points describing skill file edits

## Why
The reasoning / problem this change addresses.

## Automated Checks (Before)
Style compliance: X/Y | Render success: X/Y | DPI correct: X/Y

## Automated Checks (After)
Style compliance: X/Y | Render success: X/Y | DPI correct: X/Y

## Charts Generated
- List of modified chart PNGs

## Agent Notes
What changed and why. What the agent is uncertain about.
```

### Step 7: Commit

Stage all changes and create an atomic commit:
```
📊 feat(skill): [1-sentence description of change]
```

## Autonomous Mode

When invoked with `--iterations N` (max 3):

1. Create a staging branch: `iterate/batch-YYYYMMDD-HHMMSS`
2. Run Steps 1-7 for each iteration, committing after each
3. Between iterations, check if automated scores decreased — if so, HALT
4. After all iterations, produce a summary listing all changes
5. Do NOT merge — leave the staging branch for human review

## Guardrails

- **Max 3 iterations** without human feedback
- **No destructive changes** — add/modify only, never delete patterns
- **Style invariants** — `sns.set_theme()` and `sns.despine()` calls are immutable
- **Rollback** — each iteration is an atomic commit; `git revert` any single one
