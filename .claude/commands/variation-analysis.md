---
description: Run parallel clean-room variation analysis on a single chart pattern with dataset variety — each parallel run uses a different prompt from the pool.
argument-hint: P1..P9 [--prompt "..."] [--rounds N]
disable-model-invocation: false
allowed-tools: Bash(uv run *), Bash(scripts/*), Bash(git *), Bash(mkdir *), Bash(cp *), Bash(ls *), Bash(docker *)
---

# Variation Analysis (Quality Consistency)

Run parallel clean-room quality checks on a single chart pattern.
Each round runs 3 parallel clean rooms with **different prompts from the pool**,
then evaluates whether all outputs maintain Tim's visual identity and meet
the quality bar. Fixes are applied between rounds if quality issues are found.

Because each run uses a different dataset, comparisons focus on
**visual quality and identity** — data-handling code (column names, filtering,
sorting) is expected to differ and is excluded.

## Guardrails

- **Max rounds configurable** — `--rounds N` (default 3, max 5). If the final round still shows quality issues, halt and report.
- **No destructive changes** — add/modify only, never delete patterns
- **Style invariants** — `sns.set_theme()` and `sns.despine()` calls are immutable
- **Rollback** — each round's fixes are committed; `git revert` any single one
- **Single pattern** — this command targets exactly one pattern per invocation

## Current State

**Current pattern code:**
!`ls .claude/skills/matplotlib/patterns/`

**Current gallery entries:**
!`ls -1d gallery-archive/[0-9]* 2>/dev/null | tail -5 || echo "None"`

**Git branch:**
!`git branch --show-current`

**Recent commits:**
!`git log --oneline -3`

## Arguments

Parse `$ARGUMENTS` for:
- **Pattern identifier** (required): `P1`..`P9` or a pattern name (e.g., "violin", "heatmap")
- `--prompt "..."` (optional): Override — uses this single prompt for ALL runs (disables dataset variety)
- `--rounds N` (optional, default 3, max 5): Number of rounds to run (minimum 2 for baseline + validation)

${ARGUMENTS ? `**User input:** ${ARGUMENTS}` : ""}

## Workflow

### Step 1: Identify Pattern and Prompt Pool

1. Parse the pattern from `$ARGUMENTS`. Map names to numbers if needed:
   - P1: horizontal bar, P2: violin, P3: time series, P4: PR/ROC
   - P5: lollipop/dumbbell, P6: vertical bar, P7: heatmap, P8: multi-panel, P9: decision boundary

2. Read the current pattern code from the matching file in `.claude/skills/matplotlib/patterns/`

3. Read `.claude/skills/matplotlib/style-reference.md` for palette/layout conventions

4. Read `scripts/chart-test-container.sh` and extract the prompt pool array for this pattern (e.g., `P2_POOL`).

5. Select prompts:
   - If `--prompt "..."` was provided: use that single prompt for ALL runs (same-dataset mode, like `/variation-analysis-single`)
   - Otherwise: select prompts from the pool for each parallel run:
     - Round 1 uses pool indices 0, 1, 2 (tags A, B, C get different prompts)
     - Round 2 uses pool indices 3, 4, 5 (tags D, E, F)
     - Round R uses indices `(R-1)*3`, `(R-1)*3+1`, `(R-1)*3+2`
     - If pool size is exceeded, wrap around (mod pool size). Reuse across rounds is allowed but not within a round.
   - Log which prompt each tag will receive.

6. Define **quality evaluation dimensions**:
   - **Identity preservation:** Does each chart use the correct palette family, despine convention, legend frame styling, annotation color?
   - **Visual quality:** Layout balance, text readability, no overlaps or clipping, appropriate spacing
   - **Data-appropriateness:** Figsize scales for data, annotations reflect actual data values, legend avoids occlusion
   - **Informativeness:** Axis labels present, annotations provide insight beyond axis labels, units where needed
   - **Pattern-specific checks:** e.g., masking for heatmaps, bar coloring for time series, panel outlines for multi-panel

   **Not evaluated:** column selection, filtering, sorting, data loading, variable names, exact fontsize/alpha values — these naturally vary across datasets.

### Step 2: Run Rounds

For each round R = 1 to N (where N = `--rounds` value, default 3, max 5):

**Tag scheme:** Round 1 = A, B, C; Round 2 = D, E, F; Round 3 = G, H, I; Round 4 = J, K, L; Round 5 = M, N, O

1. Select 3 prompts from pool at offset `(R-1)*3` (mod pool size, no duplicates within a round)

2. Run 3 parallel clean rooms, each with its own prompt:
   ```bash
   scripts/chart-test-container.sh --tag <tag1> "<prompt 1>" &
   scripts/chart-test-container.sh --tag <tag2> "<prompt 2>" &
   scripts/chart-test-container.sh --tag <tag3> "<prompt 3>" &
   wait
   ```

3. Wait for all 3 to complete

4. Read all 3 generated `.py` files from the results directories

5. Read all 3 PNGs for visual comparison

6. Evaluate each PNG against the quality dimensions above. Note:
   - Which charts meet the quality bar individually?
   - Do all 3 maintain Tim's visual identity (palette, despine, legend frame, annotation color)?
   - Are there quality issues that suggest the pattern needs clarification?

7. **Early exit check (Round 1 only):** If all 3 charts meet the quality bar and maintain identity,
   report "Pattern PN passes quality check — no issues found" and skip to gallery.

8. **Quality check (Rounds 2+):** If all charts meet quality bar, proceed to gallery.
   No need to run remaining rounds.

9. **Fix quality issues:** If issues are found:
    - Propose specific fixes for each issue
    - Edit the pattern file in `.claude/skills/matplotlib/patterns/` to improve guidance
    - Edit `.claude/skills/matplotlib/style-reference.md` if palette or layout conventions change
    - Fixes should clarify guidance or improve defaults — avoid adding prohibitions
    - Continue to next round

10. **Final round issues:** If the last round still shows quality issues,
    **halt and report**. List the issues that remain and suggest next steps.

### Step 3: Gallery Entry

1. Determine next gallery number from `gallery-archive/`

2. Create `gallery-archive/NN-pX-variation-analysis/`

3. Copy representative PNGs from each round (up to 3 per round, up to 15 total for 5 rounds):
   - `round1-A.png`, `round1-B.png`, `round1-C.png`
   - `round2-D.png`, `round2-E.png`, `round2-F.png`
   - etc.

4. Write `README.md` including:
   - **What Changed** — bullet list of skill file edits
   - **Why** — what quality issue this addresses
   - **Prompts Used** — table mapping each tag to its specific prompt:
     ```
     | Tag | Round | Prompt |
     |-----|-------|--------|
     | A   | 1     | "horizontal bar chart of..." |
     | B   | 1     | "horizontal bar chart of mpg..." |
     | C   | 1     | "horizontal bar chart of GDP..." |
     | D   | 2     | "horizontal bar chart of diamond..." |
     | ...
     ```
   - **Method** — quality dimensions evaluated
   - **Round N** sections — quality assessment per chart with issues highlighted
   - **Files Modified** — what was changed in skill files
   - **Lessons Learned** — insights for the blog (most valuable section)

5. Update `CLAUDE.md` gallery table with the new entry

### Step 4: Commit

Stage all changes and create an atomic commit:
```
📊 feat(skill): tighten PN via parallel clean-room variation analysis
```

Include in the commit: skill file changes, gallery entry, CLAUDE.md update.

## Error Handling

- **Docker not running:** If `scripts/chart-test-container.sh` fails with a Docker connection error, report the error and halt. Do not retry.
- **Chart generation fails:** If any clean-room run produces zero PNGs, inspect `logs/clean-room/` for the root cause. A single failure in a round of 3 is acceptable (note it in the quality assessment); if 2+ runs fail in the same round, halt and investigate.
- **No issues found:** If Round 1 shows all 3 charts meeting the quality bar, this is a positive result. Create a gallery entry documenting the quality evidence and skip remaining rounds.
- **Persistent issues:** If the final round still shows quality issues, halt and report. Do not run additional rounds beyond the configured max — the issue may need a different approach (e.g., rewriting the pattern from scratch via `/iterate-skill`).
- **Pool too small:** If the pattern's prompt pool has fewer than 3 entries, reuse is allowed within a round (log a warning). Consider adding more prompts to the pool.
- **`--rounds` out of range:** Clamp to [2, 5]. Warn if adjusted.

## Example Usage

```bash
# Analyze P2 violin plot with dataset variety (default 3 rounds)
/variation-analysis P2

# Analyze P5 with a custom prompt (disables dataset variety — same prompt for all runs)
/variation-analysis P5 --prompt "lollipop chart of happiness score range by region from data/raw/public/world_happiness.csv"

# Quick 2-round analysis of P1
/variation-analysis P1 --rounds 2

# Extended 5-round analysis of P7
/variation-analysis P7 --rounds 5

# Analyze by pattern name
/variation-analysis heatmap
```
