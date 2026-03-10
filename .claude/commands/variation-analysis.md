---
description: Run parallel clean-room variation analysis on a single chart pattern with dataset variety — each parallel run uses a different prompt from the pool.
argument-hint: P1..P9 [--prompt "..."] [--rounds N]
disable-model-invocation: true
allowed-tools: Bash(uv run *), Bash(scripts/*), Bash(git *), Bash(mkdir *), Bash(cp *), Bash(ls *), Bash(docker *)
---

# Variation Analysis (Dataset Variety)

Run parallel clean-room variation analysis on a single chart pattern.
Each round runs 3 parallel clean rooms with **different prompts from the pool**,
then compares generated code across structural dimensions to find divergence.
Fixes are applied between rounds until the pattern converges.

Because each run uses a different dataset, convergence checks focus on
**structural dimensions only** — data-handling code (column names, filtering,
sorting) is expected to differ and is excluded from comparison.

## Guardrails

- **Max rounds configurable** — `--rounds N` (default 3, max 5). If the final round still shows structural divergence, halt and report.
- **No destructive changes** — add/modify only, never delete patterns
- **Style invariants** — `sns.set_theme()` and `sns.despine()` calls are immutable
- **Rollback** — each round's fixes are committed; `git revert` any single one
- **Single pattern** — this command targets exactly one pattern per invocation

## Current State

**Current pattern code:**
!`ls .claude/skills/matplotlib-chart/chart-patterns.md`

**Current gallery entries:**
!`ls -1d docs/gallery/[0-9]* 2>/dev/null | tail -5 || echo "None"`

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

2. Read the current pattern code from `.claude/skills/matplotlib-chart/chart-patterns.md`

3. Read `.claude/skills/matplotlib-chart/style-reference.md` for palette/layout conventions

4. Read `scripts/chart-test-container.sh` and extract the prompt pool array for this pattern (e.g., `P2_POOL`).

5. Select prompts:
   - If `--prompt "..."` was provided: use that single prompt for ALL runs (same-dataset mode, like `/variation-analysis-single`)
   - Otherwise: select prompts from the pool for each parallel run:
     - Round 1 uses pool indices 0, 1, 2 (tags A, B, C get different prompts)
     - Round 2 uses pool indices 3, 4, 5 (tags D, E, F)
     - Round R uses indices `(R-1)*3`, `(R-1)*3+1`, `(R-1)*3+2`
     - If pool size is exceeded, wrap around (mod pool size). Reuse across rounds is allowed but not within a round.
   - Log which prompt each tag will receive.

6. Define **structural** comparison dimensions (data-handling is EXCLUDED):
   - API calls (which seaborn/matplotlib functions used)
   - Palette/cmap choice
   - Figsize and aspect ratio
   - Annotation styling (format, color, size, weight)
   - Legend/colorbar configuration
   - Title format (fontsize, loc, pad)
   - Tick styling (tick_params arguments)
   - Grid configuration
   - DPI and save conventions
   - Add pattern-specific dimensions (e.g., masking for heatmaps, line styles for time series)

   **Excluded from convergence:** column selection, filtering, sorting, data loading,
   variable names — these will naturally differ because each run uses different data.

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

6. Build convergence matrix: for each **structural** dimension, record what each run produced.
   Ignore data-handling differences (expected due to different datasets).

7. Identify divergent **structural** dimensions — these are where the pattern is under-specified

8. **Early exit check (Round 1 only):** If all 3 runs are structurally identical across all
   dimensions, report "Pattern PN is already well-specified — no divergence found" and skip
   to gallery (document the convergence evidence).

9. **Convergence check (Rounds 2+):** If all structural dimensions converge, proceed to
   gallery. No need to run remaining rounds.

10. **Fix divergence:** If structural divergence exists:
    - Propose specific fixes for each divergent dimension
    - Edit `.claude/skills/matplotlib-chart/chart-patterns.md` to tighten the pattern
    - Edit `.claude/skills/matplotlib-chart/style-reference.md` if palette or layout conventions change
    - Each fix must be concrete: explicit code, parameter values, or "do/do not" rules.
      Vague guidance does not reduce divergence.
    - Continue to next round

11. **Final round divergence:** If the last round still shows structural divergence,
    **halt and report**. List the dimensions that remain divergent and explain why
    additional rounds may not help.

### Step 3: Gallery Entry

1. Determine next gallery number from `docs/gallery/`

2. Create `docs/gallery/NN-pX-variation-analysis/`

3. Copy representative PNGs from each round (up to 3 per round, up to 15 total for 5 rounds):
   - `round1-A.png`, `round1-B.png`, `round1-C.png`
   - `round2-D.png`, `round2-E.png`, `round2-F.png`
   - etc.

4. Write `README.md` including:
   - **What Changed** — bullet list of skill file edits
   - **Why** — what divergence problem this solves
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
   - **Method** — dimension table showing what was compared (note: data-handling excluded)
   - **Round N** sections — convergence tables with divergent dimensions highlighted
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
- **Chart generation fails:** If any clean-room run produces zero PNGs, inspect `logs/clean-room/` for the root cause. A single failure in a round of 3 is acceptable (note it in the convergence table); if 2+ runs fail in the same round, halt and investigate.
- **No divergence found:** If Round 1 shows all 3 runs structurally identical, this is a positive result. Create a gallery entry documenting the convergence evidence and skip remaining rounds.
- **Persistent divergence:** If the final round still shows structural divergence, halt and report. Do not run additional rounds beyond the configured max — the dimension may be inherently ambiguous and needs a different approach (e.g., rewriting the pattern from scratch via `/iterate-skill`).
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
