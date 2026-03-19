---
description: Run autonomous skill improvement loop. Scores patterns, proposes changes, keeps improvements, reverts regressions. Runs until interrupted.
argument-hint: <tag> [--threshold 0.60] [--pattern P1..P9]
disable-model-invocation: false
allowed-tools: Bash(uv run *), Bash(scripts/*), Bash(git *), Bash(mkdir *), Bash(cp *), Bash(ls *), Bash(docker *), Read, Glob, Grep
---

# Autoresearch

Autonomous skill improvement loop. Modifies individual pattern files in `patterns/`,
evaluates via a composite metric (compliance × weighted quality layers × signature_penalty),
keeps improvements, reverts regressions, and repeats until interrupted or all patterns
exceed the threshold.

## Current State

**Git branch:**
!`git branch --show-current`

**Results log:**
!`test -f results.tsv && wc -l results.tsv || echo "Not found"`

**Last experiment:**
!`tail -1 results.tsv 2>/dev/null || echo "No experiments yet"`

**Evaluation:**
!`uv run scripts/evaluate_skill.py 2>&1 || true`

## Arguments

Parse `$ARGUMENTS` for:
- **tag** (required): Branch suffix → `autoresearch/<tag>`
- `--threshold N` (optional, default 0.60): Minimum composite score
- `--pattern PN` (optional): Focus on a single pattern (P1–P9)

${ARGUMENTS ? `**User input:** ${ARGUMENTS}` : ""}

## Guardrails

- **Immutable:** `style-reference.md` Invariants section, `SKILL.md` Design Philosophy
- **Immutable calls:** `sns.set_theme()` and `sns.despine()` — never modify
- **No pattern deletions** — add/modify only
- **Single file modified per experiment:** the target `patterns/PN-*.md` file
- **Signature items:** max 4 per pattern (enforced by signature_penalty)
- **Max 5 rounds per pattern before moving on** (circuit breaker below)

---

## Step 0: Setup

1. Parse `$ARGUMENTS` for tag, threshold (default 0.60), optional `--pattern` filter.

2. Check for existing branch:
   - If `autoresearch/<tag>` exists AND `results.tsv` exists → **resume mode**:
     ```bash
     git checkout autoresearch/<tag>
     ```
     Read `results.tsv` to find the last experiment number. Continue from there.
   - If branch does not exist → **fresh start**:
     ```bash
     git checkout -b autoresearch/<tag>
     ```

3. Read these files (context for the full run):
   - `program.md` — research priorities and strategies
   - `.claude/skills/matplotlib-chart/style-reference.md` — palette/layout conventions

4. Read prompt pools from `scripts/chart-test-container.sh` to know available prompts per pattern.

---

## Step 1: Baseline (skip if resuming)

If `results.tsv` already exists with data rows, skip this step entirely.

For each pattern P1–P9 (or just the `--pattern` target):

### Layer 1 — Compliance
```bash
uv run scripts/evaluate_skill.py --json --pattern N
```
Parse JSON output. Score = 1.0 if all checks pass, 0.0 if any fail.

### Layer 2 — Visual Quality
Select 3 different prompts from the pattern's pool (indices 0, 1, 2). Run 3 parallel clean rooms:
```bash
scripts/chart-test-container.sh --tag P${N}-base-A "<prompt_A>" &
scripts/chart-test-container.sh --tag P${N}-base-B "<prompt_B>" &
scripts/chart-test-container.sh --tag P${N}-base-C "<prompt_C>" &
wait
```
Read the 3 PNGs. For each PNG, apply this 12-check **graded** rubric (0 / 1 / 2 per check):

| Check | 0 | 1 | 2 |
|-------|---|---|---|
| 1. **Layout balance** | Overlapping elements or wasted space | Minor spacing issues (tight labels, wide margins) | Balanced whitespace, nothing crowded |
| 2. **Palette correctness** | Wrong palette or missing colors | Right palette, minor deviation (wrong slice index, alpha off) | Exact match to pattern spec |
| 3. **Colorblind safety** | Red-green without diverging scheme | Partially safe (sequential used for categorical) | Confirmed safe per spec |
| 4. **Title format** | Missing or wrong position | Present but wrong fontsize, pad, or loc | Exact: fontsize, loc="left", pad=7 |
| 5. **Axis label styling** | Missing required labels or wrong color | Present but inconsistent (mixed colors, wrong fontsize) | All labels dimgrey, correct fontsize |
| 6. **Annotation quality** | Missing required annotations or unreadable | Present but wrong format/position (overlapping, clipped) | Clean, well-placed, correct format string |
| 7. **Legend compliance** | Missing required legend or default styling | Partial frame styling (missing framealpha, wrong loc) | Full spec (frameon, facecolor, edgecolor, labelcolor, loc) |
| 8. **Grid/spine cleanliness** | Visible spines or wrong grid config | Despined but grid alpha/axis wrong | Clean: despined, grid per pattern spec, no extra noise |
| 9. **Data-ink ratio** | Chartjunk (unnecessary borders, shadows, fills) | Mostly clean, one unnecessary element | Minimal non-data ink, every mark carries information |
| 10. **Publication readiness** | Would need significant rework for a blog post | Minor issues (one font inconsistency, slightly off spacing) | Ready to publish without changes |
| 11. **Data-appropriate adaptation** | Makes inappropriate data-driven choices (wrong scale, misleading) | Follows defaults blindly even when data warrants adaptation | Makes sensible data-driven choices (moved legend to avoid occlusion, scaled figsize for data volume) |
| 12. **Informativeness** | Missing critical context (no axis label for numeric data, no units, key values unlabeled) | Partial context (axis label present but vague, or some values unlabeled) | Reader can fully interpret the chart without external context (units clear, key values labeled, axis labels descriptive) |

**Note:** Check 12 evaluates against chart communication standards, NOT against the pattern spec. A pattern cannot opt out of informativeness by removing labels from its spec.

**Red flag cap:** If ANY of these are present in a PNG, reduce the **specific affected check** to 0 (do not halve the entire PNG score):
- Overlapping text → check 6 (annotation quality) = 0
- Clipped content → check 1 (layout balance) = 0
- Default matplotlib legend → check 7 (legend compliance) = 0
- Visible axis spines → check 8 (grid/spine cleanliness) = 0

Score = `total_points / 72` (12 checks × 2 max × 3 PNGs).

### Layer 3 — Refinement (code quality)
Read all 3 generated `.py` files and score 5 binary checks:

| Check | Pass (1) | Fail (0) |
|-------|----------|----------|
| 1. **No hardcoded data** | All displayed values come from the DataFrame | Values from the CSV are hardcoded as literals in the script |
| 2. **Defensive data handling** | Has dropna, type checks, or fallback values for common issues | No defensive coding (would crash on missing columns or NaN) |
| 3. **Code organization** | Logical sections, descriptive variable names, comments at key steps | Monolithic block, poor variable names, no comments |
| 4. **Consistent approach** | All 3 runs use the same structural approach to the data task | The 3 runs take fundamentally different approaches |
| 5. **Save convention** | PDF+PNG dual save, dpi=150, bbox_inches="tight" | Missing PDF or PNG, wrong dpi, missing bbox_inches |

Score = `checks_passed / 5`.

### Layer 4 — Adaptiveness
Read all 3 PNGs and generated `.py` files. Score 5 binary checks:

| Check | Pass (1) | Fail (0) |
|-------|----------|----------|
| 1. **Figsize scales for data volume** | figsize adapts to category count, label length, or data density | Fixed figsize regardless of data properties |
| 2. **Annotations reflect data-specific insights** | Annotations include data-specific values, labels, or findings | Only generic labels copied from template |
| 3. **Legend positioned to avoid occlusion** | Legend placed where it doesn't cover data points | Legend covers data or placed without regard to data |
| 4. **Palette matches data semantics** | Diverging for ±, sequential for ranking, categorical for groups | Palette applied without semantic consideration |
| 5. **At least one data-driven choice** | Code makes at least one choice that goes beyond template copy-paste | Pure template copy-paste with only column names changed |

Score = `checks_passed / 5`.

### Signature Penalty
Count the number of bullet points in the target pattern's "Signature" section.

```
signature_penalty = min(1.0, 1.0 - 0.05 × max(0, signature_count - 4))
```

A pattern with 4 or fewer signature items: penalty = 1.0 (no reduction).
A pattern with 5 items loses 5%, 6 items loses 10%, etc.

### Composite Score
```
composite = compliance × (0.50 × visual + 0.25 × refinement + 0.25 × adaptiveness) × signature_penalty
```

### Log Baseline
Create `results.tsv` with header and one row per pattern:
```
experiment	timestamp	pattern	composite	compliance	visual	refinement	adaptiveness	status	consecutive_discards	description	commit
0	2026-03-14T10:00:00	P1	0.48	1.0	0.75	0.8	0.6	baseline	0	Initial baseline	abc1234
```

---

## Step 2: Pick Target Pattern

1. Read `results.tsv`. For each pattern, find the latest row with status `keep` or `baseline`.
2. Pick the pattern with the **lowest composite score**.
   - If `--pattern` was specified, always target that pattern.
3. Circuit breakers:
   - **10 consecutive discards** on the same pattern → skip to the next-lowest pattern.
   - **All patterns above threshold** → enter patrol mode (re-baseline all, check for regressions).
   - **Experiment count > 50** → warn about context window limits. Suggest restarting with `/autoresearch <tag>` to resume on a fresh context.

---

## Step 3: Propose Change

1. Re-read `program.md` for current priorities and strategies.
2. Read ONLY the target pattern file from `patterns/` (e.g., `patterns/P3-time-series.md`).
3. Read this pattern's experiment history from `results.tsv` (filter to matching pattern rows).
4. Identify the weakest layer and focus there:
   - `compliance < 1.0` → fix compliance first (highest leverage)
   - `visual` is lowest → adjust layout, sizing, annotations
   - `refinement` is lowest → add defensive coding guidance
   - `adaptiveness` is lowest → add Guidance for data-driven adaptation
5. Propose a **specific, small change** — one dimension at a time.
   - Concrete: exact parameter values, explicit code, clear guidance.
   - **Before adding a new Signature item**, check whether the divergence is **harmful** (wrong visual identity) or **adaptive** (reasonable data-driven variation). Only add Signature items to prevent harmful identity divergence. Move adaptive guidance to the Guidance section.
   - **Pruning mode (every 5 experiments):** Instead of adding, attempt to **remove** the least-impactful Signature item or Guidance point from the **highest-scoring** pattern. If scores hold or improve after removal → keep the simplification. Removing Signature items improves the signature_penalty multiplier, making simplification structurally advantaged.

---

## Step 4: Apply and Commit

1. Edit the target pattern file in `.claude/skills/matplotlib-chart/patterns/` with the proposed change.
2. Commit immediately:
   ```bash
   git add .claude/skills/matplotlib-chart/patterns/
   git commit -m "📊 feat(skill): [1-sentence description of change]"
   ```

---

## Step 5: Evaluate (target pattern only)

### Layer 1 — Compliance
```bash
uv run scripts/evaluate_skill.py --json --pattern N
```

### Layer 2 — Visual Quality
Select 3 prompts from the pool (rotate through pool indices to avoid reusing baseline prompts):
```bash
scripts/chart-test-container.sh --tag exp${EXP}-A "<prompt_1>" &
scripts/chart-test-container.sh --tag exp${EXP}-B "<prompt_2>" &
scripts/chart-test-container.sh --tag exp${EXP}-C "<prompt_3>" &
wait
```

Read 3 PNGs → apply 12-check graded rubric (0/1/2 per check) to each → `total_points / 72`
Apply red flag caps: reduce specific affected check to 0 (not entire PNG score).

### Layer 3 — Refinement
Read 3 `.py` files → score 5 binary code-quality checks → `passed / 5`

### Layer 4 — Adaptiveness
Read 3 PNGs + `.py` files → score 5 binary adaptiveness checks → `passed / 5`

### Composite
```
composite = compliance × (0.50 × visual + 0.25 × refinement + 0.25 × adaptiveness) × signature_penalty
```

---

## Step 6: Log and Decide

1. Append a row to `results.tsv`:
   ```
   EXP	TIMESTAMP	PN	COMPOSITE	COMPLIANCE	VISUAL	REFINEMENT	ADAPTIVENESS	STATUS	CONSEC	DESCRIPTION	COMMIT
   ```

2. Compare composite to the pattern's **previous best** (latest `keep` or `baseline` row):
   - **Improved (composite > previous best):**
     - Set status = `keep`
     - Set commit = 7-char hash of the commit from Step 4
     - Reset consecutive_discards to 0
     - The branch advances with this commit.
   - **Same or worse (composite <= previous best):**
     - Set status = `discard`
     - Set commit = `(reverted)`
     - Increment consecutive_discards
     - Revert the commit:
       ```bash
       git reset --hard HEAD~1
       ```

---

## Step 7: Loop

Return to **Step 2**.

Every 10 experiments, emit a progress summary table:
```
Pattern | Best Score | Experiments | Keeps | Discards
P1      | 0.85       | 12          | 4     | 8
P2      | 0.92       | 3           | 2     | 1
...
```

---

## Circuit Breakers

- **10 consecutive discards** on same pattern → move to next-lowest pattern
- **Docker failure** (2+ of 3 runs fail in same evaluation) → halt immediately
- **All patterns above threshold** → patrol mode: re-baseline all patterns, report results, halt
- **Experiment count > 50** → warn about context window, suggest restart

---

## Results TSV Format

Tab-separated, header row + data rows. Created on first run, append-only.

```
experiment	timestamp	pattern	composite	compliance	visual	refinement	adaptiveness	status	consecutive_discards	description	commit
```

Column types:
- `experiment`: Sequential integer (0 = baseline)
- `timestamp`: ISO 8601 (e.g., `2026-03-14T10:30:00`)
- `pattern`: `P1`..`P9`
- `composite`, `compliance`, `visual`, `refinement`, `adaptiveness`: Float 0.0–1.0
- `status`: `baseline`, `keep`, `discard`, `error`
- `consecutive_discards`: Integer, resets on `keep`
- `description`: Free text, no tabs
- `commit`: 7-char git hash or `(reverted)`

**Backward compatibility:** Old rows with a `convergence` column are valid. Ignore the convergence column when computing composite — use the 4-layer formula.

---

## Error Handling

- **Docker not running:** Report error and halt. Do not retry.
- **Clean-room produces 0 PNGs:** A single failure in 3 is tolerable (score the other 2). If 2+ fail, halt.
- **evaluate_skill.py errors:** Log as `error` status, skip to next pattern.
- **Git conflicts:** Should never happen (single-file edits on a dedicated branch). If detected, halt.

---

## Example Usage

```bash
# Start a fresh autoresearch run
/autoresearch overnight-v1

# Resume an interrupted run
/autoresearch overnight-v1

# Focus on a single pattern with higher threshold
/autoresearch p4-focus --pattern P4 --threshold 0.70

# Lower threshold for broad exploration
/autoresearch broad-sweep --threshold 0.50
```
