---
description: Run parallel clean-room variation analysis on a single chart pattern using ONE prompt for all runs (original single-dataset behavior).
argument-hint: P1..P9 [--prompt "..."] [--rounds N]
disable-model-invocation: true
allowed-tools: Bash(uv run *), Bash(scripts/*), Bash(git *), Bash(mkdir *), Bash(cp *), Bash(ls *), Bash(docker *)
---

# Variation Analysis

Run 3-round parallel clean-room variation analysis on a single chart pattern.
Each round runs 3 parallel clean rooms with the same prompt, then compares
generated code across ~10 dimensions to find divergence. Fixes are applied
between rounds until the pattern converges.

## Guardrails

- **Max 3 rounds** — if Round 3 still shows structural divergence, halt and report
- **No destructive changes** — add/modify only, never delete patterns
- **Style invariants** — `sns.set_theme()` and `sns.despine()` calls are immutable
- **Rollback** — each round's fixes are committed; `git revert` any single one
- **Single pattern** — this command targets exactly one pattern per invocation

## Current State

**Current pattern code:**
!`ls .claude/skills/matplotlib-chart/patterns/`

**Current gallery entries:**
!`ls -1d docs/gallery/[0-9]* 2>/dev/null | tail -5 || echo "None"`

**Git branch:**
!`git branch --show-current`

**Recent commits:**
!`git log --oneline -3`

## Arguments

Parse `$ARGUMENTS` for:
- **Pattern identifier** (required): `P1`..`P9` or a pattern name (e.g., "violin", "heatmap")
- `--prompt "..."` (optional): Override the default test prompt for that pattern
- `--rounds N` (optional, default 3): Number of rounds to run (minimum 2 for baseline + validation)

${ARGUMENTS ? `**User input:** ${ARGUMENTS}` : ""}

## Workflow

### Step 1: Identify Pattern and Prompt

1. Parse the pattern from `$ARGUMENTS`. Map names to numbers if needed:
   - P1: horizontal bar, P2: violin, P3: time series, P4: PR/ROC
   - P5: lollipop/dumbbell, P6: vertical bar, P7: heatmap, P8: multi-panel, P9: decision boundary

2. Read the current pattern code from the matching file in `.claude/skills/matplotlib-chart/patterns/`

3. Read `.claude/skills/matplotlib-chart/style-reference.md` for palette/layout conventions

4. Select the test prompt:
   - If `--prompt "..."` was provided, use that
   - Otherwise, use the **first prompt** (index 0) from the pattern's pool in `scripts/chart-test-container.sh`
   - Log the chosen prompt — all 9 runs will use this exact same prompt

5. Define comparison dimensions for this pattern. Always include these core dimensions:
   - API calls (which seaborn/matplotlib functions used)
   - Palette/cmap choice
   - Figsize and aspect ratio
   - Annotation styling (format, color, size, weight)
   - Legend/colorbar configuration
   - Title format (fontsize, loc, pad)
   - Tick styling (tick_params arguments)
   - Data handling (column selection, filtering, sorting)
   - Add pattern-specific dimensions (e.g., masking for heatmaps, line styles for time series)

### Step 2: Round 1 — Establish Variation Baseline (tags A, B, C)

1. Run 3 parallel clean rooms with the same prompt:
   ```bash
   scripts/chart-test-container.sh --tag A "prompt here" &
   scripts/chart-test-container.sh --tag B "prompt here" &
   scripts/chart-test-container.sh --tag C "prompt here" &
   wait
   ```

2. Wait for all 3 to complete

3. Read all 3 generated `.py` files from the results directories

4. Read all 3 PNGs for visual comparison

5. Build convergence matrix: for each dimension, record what each run (A, B, C) produced

6. Identify divergent dimensions — these are where the pattern is under-specified

7. **Early exit check:** If all 3 runs are structurally identical across all dimensions,
   report "Pattern PN is already well-specified — no divergence found" and skip to Step 6
   (gallery entry documents the convergence evidence)

8. Propose specific fixes for each divergent dimension — each fix should add an explicit
   rule or code snippet to the pattern

### Step 3: Apply Round 1 Fixes

1. Edit the pattern file in `.claude/skills/matplotlib-chart/patterns/` to tighten the pattern on divergent dimensions

2. Edit `.claude/skills/matplotlib-chart/style-reference.md` if palette or layout conventions change

3. Each fix must be concrete: add explicit code, parameter values, or "do/do not" rules.
   Vague guidance (e.g., "use appropriate colors") does not reduce divergence.

### Step 4: Round 2 — Validate Fixes (tags D, E, F)

1. Run 3 parallel clean rooms with the same prompt (same as Round 1):
   ```bash
   scripts/chart-test-container.sh --tag D "prompt here" &
   scripts/chart-test-container.sh --tag E "prompt here" &
   scripts/chart-test-container.sh --tag F "prompt here" &
   wait
   ```

2. Read all 3 generated `.py` files and PNGs

3. Build convergence matrix across the same dimensions

4. Check: did Round 1 fixes converge? Any new divergence introduced?

5. If converged on all structural dimensions (cosmetic variation is acceptable), proceed to
   Round 3 for final verification. If structural divergence remains, apply additional fixes
   to the pattern file before Round 3.

### Step 5: Round 3 — Final Verification (tags G, H, I)

1. Run 3 parallel clean rooms:
   ```bash
   scripts/chart-test-container.sh --tag G "prompt here" &
   scripts/chart-test-container.sh --tag H "prompt here" &
   scripts/chart-test-container.sh --tag I "prompt here" &
   wait
   ```

2. Read all 3 generated `.py` files and PNGs

3. Confirm convergence across all structural dimensions

4. Select best output as representative

5. If structural divergence persists after Round 3: **halt and report**. List the
   dimensions that remain divergent and explain why additional rounds may not help
   (e.g., the dimension may be inherently ambiguous).

### Step 6: Gallery Entry

1. Determine next gallery number from `docs/gallery/`

2. Create `docs/gallery/NN-pX-variation-analysis/`

3. Copy representative PNGs from each round (up to 9 total):
   - `round1-A.png`, `round1-B.png`, `round1-C.png`
   - `round2-D.png`, `round2-E.png`, `round2-F.png`
   - `round3-G.png`, `round3-H.png`, `round3-I.png`

4. Write `README.md` following the pattern from galleries 27-29:
   - **What Changed** — bullet list of skill file edits
   - **Why** — what divergence problem this solves
   - **Prompt Used** — the exact prompt used for all 9 runs
   - **Method** — dimension table showing what was compared
   - **Round 1** — convergence table (A, B, C) with divergent dimensions highlighted
   - **Round 2** — convergence table (D, E, F) showing fix validation
   - **Round 3** — convergence table (G, H, I) confirming convergence
   - **Files Modified** — what was changed in skill files
   - **Lessons Learned** — insights for the blog (most valuable section)

5. Update `CLAUDE.md` gallery table with the new entry

### Step 7: Commit

Stage all changes and create an atomic commit:
```
📊 feat(skill): tighten PN via parallel clean-room variation analysis
```

Include in the commit: skill file changes, gallery entry, CLAUDE.md update.

## Error Handling

- **Docker not running:** If `scripts/chart-test-container.sh` fails with a Docker connection error, report the error and halt. Do not retry.
- **Chart generation fails:** If any clean-room run produces zero PNGs, inspect `logs/clean-room/` for the root cause. A single failure in a round of 3 is acceptable (note it in the convergence table); if 2+ runs fail in the same round, halt and investigate.
- **No divergence found:** If Round 1 shows all 3 runs structurally identical, this is a positive result. Create a gallery entry documenting the convergence evidence and skip Rounds 2-3.
- **Persistent divergence:** If Round 3 still shows structural divergence, halt and report. Do not run additional rounds — the dimension may be inherently ambiguous and needs a different approach (e.g., rewriting the pattern from scratch via `/iterate-skill`).
- **Fewer than 3 rounds requested:** With `--rounds 2`, skip Round 3 (Steps 5). Minimum 2 rounds is required (baseline + validation).

## Example Usage

```bash
# Analyze P2 violin plot divergence
/variation-analysis P2

# Analyze P5 with a custom prompt
/variation-analysis P5 --prompt "lollipop chart of happiness score range by region from data/raw/public/world_happiness.csv"

# Quick 2-round analysis of P1
/variation-analysis P1 --rounds 2

# Analyze by pattern name
/variation-analysis heatmap
```
