---
description: Run autonomous skill improvement loop. Scores patterns, proposes changes, keeps improvements, reverts regressions. Runs until interrupted.
argument-hint: <tag> [--threshold 0.85] [--pattern P1..P9]
disable-model-invocation: false
allowed-tools: Bash(uv run *), Bash(scripts/*), Bash(git *), Bash(mkdir *), Bash(cp *), Bash(ls *), Bash(docker *), Read, Glob, Grep
---

# Autoresearch

Autonomous skill improvement loop. Modifies `chart-patterns.md`, evaluates via
a composite metric (compliance × convergence × visual), keeps improvements,
reverts regressions, and repeats until interrupted or all patterns exceed the
threshold.

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
- `--threshold N` (optional, default 0.85): Minimum composite score
- `--pattern PN` (optional): Focus on a single pattern (P1–P9)

${ARGUMENTS ? `**User input:** ${ARGUMENTS}` : ""}

## Guardrails

- **Immutable files:** `style-reference.md`, `SKILL.md`
- **Immutable calls:** `sns.set_theme()` and `sns.despine()` — never modify
- **No pattern deletions** — add/modify only
- **Single file modified per experiment:** `chart-patterns.md`
- **Max 5 rounds per pattern before moving on** (circuit breaker below)

---

## Step 0: Setup

1. Parse `$ARGUMENTS` for tag, threshold (default 0.85), optional `--pattern` filter.

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

Read the 3 generated `.py` files. Compare across 10 structural dimensions (excluding data-handling):
1. API calls (seaborn/matplotlib functions)
2. Palette/cmap choice
3. Figsize and aspect ratio
4. Annotation styling (format, color, size, weight)
5. Legend/colorbar configuration
6. Title format (fontsize, loc, pad)
7. Tick styling (tick_params arguments)
8. Grid configuration
9. DPI and save conventions
10. Pattern-specific (masking, line styles, etc.)

Score = `dimensions_matching / dimensions_total`

### Layer 3 — Visual Quality
Read the 3 PNGs. For each PNG, apply this 5-check binary rubric:

1. **Layout & spacing:** No overlapping elements, balanced whitespace (0/1)
2. **Color:** Palette matches pattern spec, colorblind-safe (0/1)
3. **Typography:** Titles, labels, annotations properly sized and dimgrey (0/1)
4. **Annotations:** Data values annotated where pattern specifies (0/1)
5. **Publishability:** Acceptable in a blog post without changes? (0/1)

Score = `checks_passed / 15` (5 checks × 3 PNGs). All 3 PNGs must pass all 5 checks for a perfect 1.0.

### Composite Score
```
composite = compliance × convergence × visual
```

### Log Baseline
Create `results.tsv` with header and one row per pattern:
```
experiment	timestamp	pattern	composite	compliance	convergence	visual	status	consecutive_discards	description	commit
0	2026-03-14T10:00:00	P1	0.72	1.0	0.8	0.9	baseline	0	Initial baseline	abc1234
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
2. Read ONLY the target pattern block from `chart-patterns.md`:
   - Search for `## N.` to find the section start, read until the next `## ` heading.
   - Do NOT read the full 28KB file — context conservation.
3. Read this pattern's experiment history from `results.tsv` (filter to matching pattern rows).
4. Identify the weakest layer and focus there:
   - `compliance < 1.0` → fix compliance first (highest leverage)
   - `convergence` is lowest → tighten rules, pin parameters
   - `visual` is lowest → adjust layout, sizing, annotations
5. Propose a **specific, small change** — one dimension at a time.
   - Concrete: exact parameter values, explicit code, "do/don't" rules.
   - Avoid vague guidance — it doesn't reduce divergence.

---

## Step 4: Apply and Commit

1. Edit `.claude/skills/matplotlib-chart/chart-patterns.md` with the proposed change.
2. Commit immediately:
   ```bash
   git add .claude/skills/matplotlib-chart/chart-patterns.md
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

Read 3 `.py` files → compare 10 structural dimensions → `dims_matching / dims_total`

### Layer 3 — Visual Quality
Read 3 PNGs → apply 5-check rubric to each → `checks_passed / 15`

### Composite
```
composite = compliance × convergence × visual
```

---

## Step 6: Log and Decide

1. Append a row to `results.tsv`:
   ```
   EXP	TIMESTAMP	PN	COMPOSITE	COMPLIANCE	CONVERGENCE	VISUAL	STATUS	CONSEC	DESCRIPTION	COMMIT
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
experiment	timestamp	pattern	composite	compliance	convergence	visual	status	consecutive_discards	description	commit
```

Column types:
- `experiment`: Sequential integer (0 = baseline)
- `timestamp`: ISO 8601 (e.g., `2026-03-14T10:30:00`)
- `pattern`: `P1`..`P9`
- `composite`, `compliance`, `convergence`, `visual`: Float 0.0–1.0
- `status`: `baseline`, `keep`, `discard`, `error`
- `consecutive_discards`: Integer, resets on `keep`
- `description`: Free text, no tabs
- `commit`: 7-char git hash or `(reverted)`

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
/autoresearch p4-focus --pattern P4 --threshold 0.90

# Lower threshold for broad exploration
/autoresearch broad-sweep --threshold 0.75
```
