---
description: Run autonomous skill improvement loop. Scores patterns, proposes changes, keeps improvements, reverts regressions. Runs until interrupted.
argument-hint: <tag> [--threshold 0.60] [--pattern P1..P9]
disable-model-invocation: false
allowed-tools: Bash(uv run *), Bash(scripts/*), Bash(git *), Bash(mkdir *), Bash(cp *), Bash(ls *), Bash(docker *), Read, Glob, Grep
---

# Autoresearch

Autonomous skill improvement loop. Modifies individual pattern files in `patterns/`,
evaluates via a composite metric (compliance × convergence × visual × refinement),
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

- **Immutable files:** `style-reference.md`, `SKILL.md`
- **Immutable calls:** `sns.set_theme()` and `sns.despine()` — never modify
- **No pattern deletions** — add/modify only
- **Single file modified per experiment:** the target `patterns/PN-*.md` file
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

### Layer 2 — Convergence
Select 3 different prompts from the pattern's pool (indices 0, 1, 2). Run 3 parallel clean rooms:
```bash
scripts/chart-test-container.sh --tag P${N}-base-A "<prompt_A>" &
scripts/chart-test-container.sh --tag P${N}-base-B "<prompt_B>" &
scripts/chart-test-container.sh --tag P${N}-base-C "<prompt_C>" &
wait
```

Read the 3 generated `.py` files. Compare across two tiers of dimensions (excluding data-handling):

**Structural dimensions (must match — define the pattern's identity):**
1. API calls (seaborn/matplotlib functions used)
2. Palette/cmap family (e.g., "rocket", "RdBu_r", cubehelix)
3. DPI and save conventions (PDF+PNG, dpi=150, bbox_inches)
4. Grid on/off and despine configuration
5. Core pattern structure (e.g., bars+rolling line for P3, k-fold+average for P9)

**Adaptive dimensions (may vary based on data — healthy flexibility):**
6. Figsize scaling (may increase for more data points/categories)
7. Legend position (may move to avoid occlusion)
8. Annotation format (decimal places may adapt to value range)
9. Exact parameter values (fontsize, labelpad, alpha within ±2 of spec)
10. Pattern-specific adaptations (rotation, axis limits, label text)

Score = `structural_matching / structural_total` (only structural dimensions count for convergence). Log adaptive dimension variation as informational — divergence here is expected and healthy.

**Appropriateness bonus:** If 2 of 3 runs match on a structural dimension and the third makes a defensible, data-driven choice (e.g., different figsize for a dataset with many more categories, moved legend to avoid occlusion), score that dimension as matching (1.0, not 0.67). Only penalize when the third run uses a fundamentally wrong approach (wrong palette family, wrong API).

### Layer 3 — Visual Quality
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

**Red flag cap:** If ANY of these are present in a PNG, that PNG's raw score is **halved**:
- Overlapping text (any text element obscured by another)
- Clipped content (bars, labels, or annotations cut off at figure edges)
- Default matplotlib legend (no custom frame styling visible)
- Visible axis spines (despine not applied or overridden)

Score = `total_points / 72` (12 checks × 2 max × 3 PNGs). A "pretty good" chart typically scores 16–20/24 per PNG (visual ≈ 0.70–0.80), leaving meaningful headroom for improvement.

### Layer 4 — Refinement (code quality)
Read all 3 generated `.py` files and score 5 binary checks:

| Check | Pass (1) | Fail (0) |
|-------|----------|----------|
| 1. **No hardcoded data** | All displayed values come from the DataFrame | Values from the CSV are hardcoded as literals in the script |
| 2. **Defensive data handling** | Has dropna, type checks, or fallback values for common issues | No defensive coding (would crash on missing columns or NaN) |
| 3. **Code organization** | Logical sections, descriptive variable names, comments at key steps | Monolithic block, poor variable names, no comments |
| 4. **Consistent approach** | All 3 runs use the same structural approach to the data task | The 3 runs take fundamentally different approaches |
| 5. **Save convention** | PDF+PNG dual save, dpi=150, bbox_inches="tight" | Missing PDF or PNG, wrong dpi, missing bbox_inches |

Score = `checks_passed / 5`.

### Rule-Count Penalty
Count the number of bullet points in the target pattern's "Rules (identity)" section. For every rule beyond 8, subtract 0.02 from the refinement score (floor at 0). This creates evolutionary pressure to keep patterns concise — the simplest specification that achieves quality is preferred.

### Composite Score
```
composite = compliance × (0.25 × convergence + 0.45 × visual + 0.25 × refinement)
```

### Log Baseline
Create `results.tsv` with header and one row per pattern:
```
experiment	timestamp	pattern	composite	compliance	convergence	visual	refinement	status	consecutive_discards	description	commit
0	2026-03-14T10:00:00	P1	0.48	1.0	0.8	0.75	0.8	baseline	0	Initial baseline	abc1234
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
   - `convergence` is lowest → tighten rules on **structural** dimensions only
   - `visual` is lowest → adjust layout, sizing, annotations
   - `refinement` is lowest → add defensive coding guidance, save convention rules
5. Propose a **specific, small change** — one dimension at a time.
   - Concrete: exact parameter values, explicit code, "do/don't" rules.
   - Avoid vague guidance — it doesn't reduce divergence.
   - **Before adding a new rule**, check whether the divergence is **harmful** (wrong visual output, broken API) or **adaptive** (reasonable data-driven variation like legend repositioning). Only add rules to prevent harmful divergence. If 2 of 3 runs make the same choice and the result looks correct, the pattern is already well-specified — do not add a rule to force the third run to match.
   - **Pruning mode (every 10 experiments):** Instead of adding, attempt to **remove** the least-impactful rule from the highest-scoring pattern. If scores hold or improve after removal → keep the simplification. This counteracts the rule-accumulation ratchet. Prefer removing rules that re-state values already present in the code template.

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

### Layer 2 — Convergence
Select 3 prompts from the pool (rotate through pool indices to avoid reusing baseline prompts):
```bash
scripts/chart-test-container.sh --tag exp${EXP}-A "<prompt_1>" &
scripts/chart-test-container.sh --tag exp${EXP}-B "<prompt_2>" &
scripts/chart-test-container.sh --tag exp${EXP}-C "<prompt_3>" &
wait
```

Read 3 `.py` files → compare 5 structural dimensions → `structural_matching / 5` (log adaptive dimension variation as informational)

### Layer 3 — Visual Quality
Read 3 PNGs → apply 12-check graded rubric (0/1/2 per check) to each → `total_points / 72`
Apply red flag caps if any PNG has overlapping text, clipped content, visible spines, or default legend.

### Layer 4 — Refinement
Read 3 `.py` files → score 5 binary code-quality checks → `passed / 5`

### Composite
```
composite = compliance × (0.25 × convergence + 0.45 × visual + 0.25 × refinement)
```

---

## Step 6: Log and Decide

1. Append a row to `results.tsv`:
   ```
   EXP	TIMESTAMP	PN	COMPOSITE	COMPLIANCE	CONVERGENCE	VISUAL	REFINEMENT	STATUS	CONSEC	DESCRIPTION	COMMIT
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
experiment	timestamp	pattern	composite	compliance	convergence	visual	refinement	status	consecutive_discards	description	commit
```

Column types:
- `experiment`: Sequential integer (0 = baseline)
- `timestamp`: ISO 8601 (e.g., `2026-03-14T10:30:00`)
- `pattern`: `P1`..`P9`
- `composite`, `compliance`, `convergence`, `visual`, `refinement`: Float 0.0–1.0
- `status`: `baseline`, `keep`, `discard`, `error`
- `consecutive_discards`: Integer, resets on `keep`
- `description`: Free text, no tabs
- `commit`: 7-char git hash or `(reverted)`

**Backward compatibility:** Old rows without a `refinement` column are valid. Treat missing refinement as 1.0 when computing composite for comparison purposes.

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
