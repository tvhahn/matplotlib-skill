---
description: Run a single evaluation-improvement-documentation cycle on the matplotlib skill. Creates gallery entries and atomic commits.
argument-hint: [--iterations N] [--quick] [focus area]
disable-model-invocation: true
allowed-tools: Bash(uv run *), Bash(scripts/*), Bash(git *), Bash(mkdir *), Bash(cp *), Bash(ls *), Bash(docker *)
---

# Iterate Skill

Run a single evaluation-improvement-documentation cycle on the matplotlib skill.

## Guardrails

- **Max 3 iterations** without human feedback
- **No destructive changes** — add/modify only, never delete patterns
- **Style invariants** — `sns.set_theme()` and `sns.despine()` calls are immutable
- **Rollback** — each iteration is an atomic commit; `git revert` any single one

## Current State

**Evaluation score:**
!`uv run scripts/evaluate_skill.py 2>&1 || true`

**Latest clean-room runs:**
!`ls -1t logs/clean-room/ 2>/dev/null | head -5 || echo "No runs yet"`

**Current gallery entries:**
!`ls -1d gallery-archive/[0-9]* 2>/dev/null | tail -5 || echo "None"`

**Git branch:**
!`git branch --show-current`

**Recent commits:**
!`git log --oneline -3`

## Arguments

Parse `$ARGUMENTS` for:
- `--iterations N` (1-3): Run N cycles on a staging branch, merging at the end. Default: 1 (no branch).
- `--quick`: Use `--quick` flag for chart-test-container.sh (3 prompts instead of 5).
- Remaining text: Focus area hint (e.g., "tick marks", "P9 spelling"). Prioritize this in Step 2.

${ARGUMENTS ? `**User input:** ${ARGUMENTS}` : ""}

## Workflow

### Step 1: Evaluate Current State

1. Read the skill files:
   - `.claude/skills/matplotlib/SKILL.md`
   - `.claude/skills/matplotlib/style-reference.md`
   - The pattern files in `.claude/skills/matplotlib/patterns/`

2. Review the injected evaluation score above — note any failures or style compliance gaps.

3. If previous clean-room results exist (`logs/clean-room/latest/`), read each PNG and perform a **Visual Evaluation** (see protocol in Step 5 item 3). Record visual observations as the qualitative baseline.

### Step 2: Identify Improvements

Select **1-2 areas** for improvement. If a focus area was provided in arguments, prioritize it. Otherwise prioritize in this order:
1. Style compliance gaps flagged by evaluate_skill.py
2. Visual issues identified during Step 1 evaluation (layout, readability, color, spacing)
3. Pattern inconsistencies (different annotations, missing legend styling)
4. Code quality issues (deprecated API calls, unclear variable names)
5. Visual polish and refinements

If a pattern shows inconsistent visual quality across recent runs,
consider running `/variation-analysis PN` for targeted quality checks
instead of ad-hoc fixes.

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
| P3 | patterns/P3-time-series.md | Added rolling window annotation | High |
```

### Step 4: Apply Changes

Make targeted edits to skill files in `.claude/skills/matplotlib/`.

### Step 5: Verify

1. Run static analysis for style compliance:
   ```bash
   uv run scripts/evaluate_skill.py --check-renders
   ```

2. Run the container-based skill test (Claude Code generates charts from minimal prompts in a Docker clean room):
   ```bash
   scripts/chart-test-container.sh --quick
   ```

3. **Visual Evaluation** — for each generated PNG, perform this sequence IN ORDER.
   Write your observations into the gallery README (Step 6).

   **Observe:** Describe what you see in 2-3 sentences. Layout, colors, text,
   spacing, composition. No judgments yet — just describe what is there.

   **Compare:** Open style-reference.md and note any gaps:
   - Typography: readable labels, proper font sizing?
   - Color: colorblind-accessible palette, consistent with spec?
   - Layout: balanced whitespace, aligned elements?
   - Annotations: present, well-positioned, dimgrey?
   - Legends: framed, white background, light grey border?
   - Despined whitegrid: does the overall aesthetic come through?

   **Judge:** Beyond the spec, apply your own taste:
   - Would you put this chart in a published paper without changes?
   - What's the first thing that catches your eye — good or bad?
   - Is anything cluttered, misaligned, or hard to read?
   - What one change would most improve this chart?

   **Verdict:** Rate each chart: PUBLISH | POLISH | REWORK

4. Read the generated Python scripts in each results subdirectory to confirm style conventions (`sns.set_theme`, `sns.despine`).

5. Record "After" automated check scores.

6. **Regression detection**: If the container script exits nonzero (any prompt produced zero charts), or generated code is missing `sns.set_theme`/`sns.despine`, halt and explain why.

7. When all automated checks pass, visual evaluation becomes the primary driver of improvement. The evaluate_skill.py score is the floor, not the ceiling. Use your Visual Evaluation verdicts to identify what to improve in the next iteration.

### Step 6: Document

Determine the next gallery entry number by looking at `gallery-archive/` and create:

1. Create `gallery-archive/NN-description/` folder
2. Copy relevant PNGs from the clean-room results directory (`logs/clean-room/latest/`) into the gallery folder
3. Write `README.md` following `docs/gallery/TEMPLATE.md`. Include all Visual Evaluation
   observations from Step 5 in the appropriate sections.

### Step 7: Commit

Stage all changes and create an atomic commit:
```
📊 feat(skill): [1-sentence description of change]
```

## Autonomous Mode

When `--iterations N` is provided (max 3):

1. Create a staging branch: `iterate/batch-YYYYMMDD-HHMMSS`
2. Run Steps 1-7 for each iteration, committing after each
3. Between iterations, check if automated scores decreased — if so, HALT
4. After all iterations, merge the staging branch back to master:
   - `git checkout master && git merge <branch>`
   - Delete the staging branch: `git branch -d <branch>`
5. Produce a final summary listing all changes, the score progression,
   and a reminder that each iteration is an atomic commit revertible
   with `git revert <hash>`

## Error Handling

- **Docker not running:** If `scripts/chart-test-container.sh` fails with a Docker connection error, report the error and halt. Do not retry.
- **Eval score decreases:** If the "After" automated score is lower than the "Before" score, revert the skill file changes (`git checkout -- .claude/skills/`) and halt with an explanation.
- **Chart generation fails:** If the container script exits nonzero, inspect the logs in `logs/clean-room/latest/` for the root cause before deciding whether to fix or halt.
- **No changes needed:** If the evaluation score is perfect and visual evaluation shows all PUBLISH verdicts, report "no improvements identified" and skip Steps 3-7.

## Example Usage

```bash
# Single iteration, full test suite
/iterate-skill

# Quick iteration focused on a specific area
/iterate-skill --quick P9 title consistency

# Three autonomous iterations
/iterate-skill --iterations 3

# Quick autonomous run focused on tick marks
/iterate-skill --iterations 2 --quick tick marks
```
