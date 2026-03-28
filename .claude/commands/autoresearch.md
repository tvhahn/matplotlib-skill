---
description: Run autonomous skill improvement loop. Scores patterns, proposes changes, keeps improvements, reverts regressions. Runs until interrupted.
argument-hint: <tag> [--threshold 0.60] [--pattern P1..P9]
disable-model-invocation: false
allowed-tools: Agent, Bash(uv run *), Bash(scripts/*), Bash(git *), Bash(mkdir *), Bash(cp *), Bash(ls *), Bash(docker *), Read, Glob, Grep
---

# Autoresearch

Autonomous skill improvement loop. Modifies individual pattern files in `patterns/`,
evaluates via a composite metric (compliance × weighted quality layers × signature_penalty),
keeps improvements, reverts regressions, and repeats until interrupted or all patterns
exceed the threshold.

**Scoring spec:** See `docs/specs/autoresearch-v2/scoring-v2-spec.md` for full technical details.

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

## Evaluation Subagent

Steps 1 and 5 delegate Layers 2–4 (visual, refinement, adaptiveness) to an Agent
subagent. The orchestrator never reads PNGs or `.py` files — it only sees the
subagent's returned JSON scores. This keeps the orchestrator's context small enough
for 100+ iterations.

**Subagent prompt template** (orchestrator fills in variables and spawns):

```
You are an evaluation subagent for autoresearch experiment ${EXP} on pattern ${PATTERN}.

## Task
1. Run 3 parallel clean rooms:
   scripts/chart-test-container.sh --tag ${TAG_PREFIX}-A "${PROMPT_A}" &
   scripts/chart-test-container.sh --tag ${TAG_PREFIX}-B "${PROMPT_B}" &
   scripts/chart-test-container.sh --tag ${TAG_PREFIX}-C "${PROMPT_C}" &
   wait

2. Read the 3 generated PNGs and 3 .py files from the results.

3. Score Layer 2 (Visual Quality) — apply the 10-check graded rubric
   from the "Layer 2" section below to each PNG. Use worst-of-3 floor formula.

4. Score Layer 3 (Refinement) — read 3 .py files, apply the 5-check
   graded rubric (0/1/2/3) from the "Layer 3" section below.

5. Score Layer 4 (Adaptiveness) — read 3 PNGs + .py files, apply the
   5-check graded rubric (0/1/2/3) from the "Layer 4" section below.

## Scoring calibration
- A score of 2 on visual checks 7–10 should be RARE. Default to 1 when
  the chart is competent but unremarkable. Reserve 2 for choices that a
  skilled human designer would make. Justify every score of 2.
- A score of 3 on refinement/adaptiveness checks should be RARE. It
  indicates exceptional quality beyond professional competence.

## Return format (ONLY return this JSON, nothing else)
{"visual": 0.XX, "refinement": 0.XX, "adaptiveness": 0.XX, "issues": ["top issue 1", "top issue 2", "top issue 3"]}
```

The rubric tables referenced above are in the Layer sections of this document.
The orchestrator copies the relevant rubric tables into the subagent prompt.

---

## Step 0: Setup

1. Parse `$ARGUMENTS` for tag, threshold (default 0.60), optional `--pattern` filter.

2. Check for existing branch:
   - If `autoresearch/<tag>` exists AND `results.tsv` exists → **resume mode**:
     ```bash
     git checkout autoresearch/<tag>
     ```
     Read `results.tsv` to find the last experiment number. Build in-memory
     best-per-pattern dict from the latest `keep` or `baseline` row per pattern.
     Continue from there.
   - If branch does not exist → **fresh start**:
     ```bash
     git checkout -b autoresearch/<tag>
     ```

3. Read these files (context for the full run):
   - `program.md` — research priorities and strategies
   - `.claude/skills/matplotlib/style-reference.md` — palette/layout conventions

4. Read prompt pools from `scripts/chart-test-container.sh` to know available prompts per pattern.

5. **Prompt holdout split:** For each pattern's prompt pool, designate the first 70% as
   **train prompts** (used during iterations) and the last 30% as **holdout prompts**
   (reserved for checkpoint evaluation every 10 experiments).

---

## Step 1: Baseline (skip if resuming)

If `results.tsv` already exists with data rows, skip this step entirely.

For each pattern P1–P9 (or just the `--pattern` target):

### Layer 1 — Compliance
```bash
uv run scripts/evaluate_skill.py --json --pattern N
```
Parse JSON output. Score = 1.0 if all checks pass, 0.0 if any fail.

### Layers 2–4 — Spawn Evaluation Subagent

Select 3 different **train prompts** from the pattern's pool (indices 0, 1, 2).

Spawn an Agent subagent using the template from the "Evaluation Subagent" section above,
with `TAG_PREFIX=P${N}-base` and `EXP=0`.

The subagent runs 3 clean rooms, reads PNGs and .py files, applies all rubrics, and
returns JSON: `{"visual": X, "refinement": X, "adaptiveness": X, "issues": [...]}`.

### Signature Penalty
Count the number of bullet points in the target pattern's "Signature" section.

```
signature_penalty = min(1.0, 1.0 - 0.03 × max(0, signature_count - 3)²)
```

A pattern with 3 or fewer signature items: penalty = 1.0 (no reduction).
Penalty is **quadratic** — each additional item costs progressively more:
- 4 items → 0.97
- 5 items → 0.88
- 6 items → 0.73
- 7 items → 0.52

### Composite Score
```
composite = compliance × (0.50 × visual + 0.25 × refinement + 0.25 × adaptiveness) × signature_penalty
```

### Log Baseline
Create `results.tsv` with header and one row per pattern:
```
experiment	timestamp	pattern	composite	compliance	visual	refinement	adaptiveness	status	consecutive_discards	description	commit
0	2026-03-14T10:00:00	P1	0.48	1.0	0.55	0.60	0.47	baseline	0	Initial baseline	abc1234
```

Also initialize the in-memory best-per-pattern dict with baseline scores.

---

## Step 2: Pick Target Pattern

1. Use the in-memory best-per-pattern dict (or read `results.tsv` on first access).
   For each pattern, find the latest row with status `keep` or `baseline`.
2. Pick the pattern with the **lowest composite score**.
   - If `--pattern` was specified, always target that pattern.
3. Circuit breakers:
   - **10 consecutive discards** on the same pattern → skip to the next-lowest pattern.
   - **Pattern above 0.90 composite** → skip to the next-lowest pattern (diminishing returns brake).
   - **All patterns above threshold** → enter patrol mode (re-baseline all, check for regressions).
   - **All patterns above 0.90** → patrol mode: re-baseline all patterns, report results, halt.
   - **Experiment count > 100** → warn about context window limits. Suggest restarting with `/autoresearch <tag>` to resume on a fresh context.

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

1. Edit the target pattern file in `.claude/skills/matplotlib/patterns/` with the proposed change.
2. Commit immediately:
   ```bash
   git add .claude/skills/matplotlib/patterns/
   git commit -m "📊 feat(skill): [1-sentence description of change]"
   ```

---

## Step 5: Evaluate (target pattern only)

### Layer 1 — Compliance
```bash
uv run scripts/evaluate_skill.py --json --pattern N
```

### Layers 2–4 — Spawn Evaluation Subagent

Select 3 **train prompts** from the pool (rotate through pool indices to avoid reusing
baseline prompts — use offset `EXP * 3 mod pool_size`).

Spawn an Agent subagent using the template from the "Evaluation Subagent" section,
with `TAG_PREFIX=exp${EXP}` and the 3 selected prompts.

The subagent returns JSON: `{"visual": X, "refinement": X, "adaptiveness": X, "issues": [...]}`.

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

2. Compare composite to the pattern's **previous best** (from in-memory dict):
   - **Improved (composite > previous best):**
     - Set status = `keep`
     - Set commit = 7-char hash of the commit from Step 4
     - Reset consecutive_discards to 0
     - Update in-memory best-per-pattern dict
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
P1      | 0.65       | 12          | 4     | 8
P2      | 0.72       | 3           | 2     | 1
...
```

Every 10 experiments, also run a **holdout evaluation**: use holdout prompts (last 30% of
pool) instead of train prompts for one evaluation cycle. Compare holdout scores to train
scores. If train scores improved by > 0.10 while holdout scores are flat or declining,
flag **"potential rubric overfitting"** and suggest human review.

---

## Layer 2: Visual Quality — 10-Check Graded Rubric

Applied to each of 3 PNGs. Each check scored 0/1/2.

### Tier A — Craft checks (6 checks)

| Check | 0 | 1 | 2 |
|-------|---|---|---|
| 1. **Layout balance** | Overlapping elements or >30% wasted space | Minor spacing issues (tight labels, slightly wide margins) | Balanced whitespace, nothing crowded, proportional gaps |
| 2. **Annotation placement & quality** | Missing annotations when data warrants them, OR overlapping text | Annotations present, correctly placed, generic format | Annotations highlight specific data insights, well-placed, no overlaps |
| 3. **Colorblind safety** | Red-green encoding without diverging scheme | Partially safe (sequential used for categorical) | Confirmed safe per pattern spec |
| 4. **Data-ink ratio** | Chartjunk (unnecessary borders, shadows, fills, decorations) | Mostly clean, one unnecessary element | Minimal non-data ink, every mark carries information |
| 5. **Color effectiveness** | Palette doesn't serve the data (wrong type for comparison) | Correct palette family, generic application | Palette choices reinforce data meaning (emphasis where intended, semantic mapping) |
| 6. **Axis/scale appropriateness** | Wrong scale type, misleading range, truncated baseline for bars | Correct scale, minor range issue | Appropriate scale, sensible range, zero-baseline for bars, units present |

### Tier B — Design excellence checks (4 checks, deliberately hard)

**Scoring guidance:** A score of 2 on checks 7–10 should be **rare**. Default to 1 when
the chart is competent but unremarkable. Reserve 2 for choices that a skilled human
designer would make. Justify every score of 2 with a specific observation.

| Check | 0 | 1 | 2 |
|-------|---|---|---|
| 7. **Title quality** | Missing title or placeholder text ("Chart Title") | Classical title describes the metric (e.g., "Collisions per Billion Miles by State") | Classical title + insight annotation below chart that states a data-specific finding |
| 8. **Typography hierarchy** | All text same weight/size, no visual priority | Some hierarchy (title larger), but labels compete for attention | Clear progression: title > subtitle > labels > annotations. Professional editorial quality |
| 9. **Reader self-sufficiency** | Reader needs external context (no units, unlabeled axes, ambiguous categories) | Most context present, one gap (missing units or vague axis label) | Unfamiliar reader can fully interpret. Units clear, values labeled, axes descriptive |
| 10. **Adaptive composition** | Template defaults applied without regard for data | 1–2 layout choices adapted to data | Layout demonstrates understanding of the specific dataset. Non-obvious choices that improve communication |

### Red flag caps

If ANY of these are present in a PNG, reduce the **specific affected check** to 0:
- Overlapping text → check 2 (annotation quality) = 0
- Clipped content → check 1 (layout balance) = 0

Note: Default legend styling and visible spines are now compliance failures (Layer 1),
not visual penalties.

### Visual scoring formula

Per-PNG score: `sum of 10 checks / 20`

Aggregate across 3 PNGs with **worst-of-3 floor**:
```
worst_png = min(png_1_score, png_2_score, png_3_score)
mean_all = mean(png_1_score, png_2_score, png_3_score)
visual = max(0.4 × worst_png + 0.6 × mean_all, mean_all × 0.85)
```

One catastrophic PNG drags the score down; three consistent PNGs aren't penalized
beyond the average.

---

## Layer 3: Refinement — 5-Check Graded Rubric

Read all 3 generated `.py` files. Each check scored 0/1/2/3.

| Check | 0 | 1 | 2 | 3 |
|-------|---|---|---|---|
| 1. **No hardcoded data** | Displayed values hardcoded as literals | Most values from DataFrame, some literals | All displayed values from DataFrame | All from data + handles edge cases (empty DataFrame, single-row) |
| 2. **Defensive data handling** | No defensive coding | Basic `dropna()` after load | `dropna()` + type checks or column existence validation | `dropna()` + type checks + fallback values + informative error messages |
| 3. **Code organization** | Monolithic block, no comments, poor variable names | Section comments present, flat structure, generic names | Logical sections, descriptive names, comments at key steps | Publication-quality: helpers where warranted, consistent naming, docstring explains intent |
| 4. **Consistent approach** | 3 fundamentally different structural approaches | 2 similar, 1 divergent | Same structure, minor variation in details | Identical structural approach with data-appropriate adaptations |
| 5. **Save convention** | Missing PDF or PNG, wrong dpi, missing bbox_inches | Correct formats, missing `bbox_inches="tight"` | PDF+PNG, dpi=150, `bbox_inches="tight"` | + `figures/` dir created with `mkdir(exist_ok=True)`, descriptive filename |

Score = `total / 15`.

---

## Layer 4: Adaptiveness — 5-Check Graded Rubric

Read all 3 PNGs and generated `.py` files. Each check scored 0/1/2/3.

| Check | 0 | 1 | 2 | 3 |
|-------|---|---|---|---|
| 1. **Figsize scales for data** | Fixed template figsize regardless | Width OR height adapted | Both dimensions adapted for data properties | Adaptive + aspect ratio matches content type |
| 2. **Annotations reflect data** | Only generic labels copied from template | Data values present, generic format | Data-specific values with appropriate precision | Annotations highlight specific insights or outliers |
| 3. **Legend avoids occlusion** | Legend covers data points | Legend outside data range (template default) | Legend positioned to minimize occlusion for this dataset | Placement considers data density, visual hierarchy, and available whitespace |
| 4. **Palette matches semantics** | Random/default palette, no semantic relation | Correct palette family from pattern spec | Family + direction matches data semantics (diverging for ±, sequential for rank) | + emphasis color used meaningfully to highlight specific data |
| 5. **Data-driven choices** | Pure template copy-paste, only column names changed | 1 data-driven adaptation | 2–3 adaptations (figsize, format, sort, tick formatting) | 4+ adaptations demonstrating genuine understanding of the dataset's story |

Score = `total / 15`.

---

## Circuit Breakers

- **10 consecutive discards** on same pattern → move to next-lowest pattern
- **Docker failure** (2+ of 3 runs fail in same evaluation) → halt immediately
- **Pattern above 0.90 composite** → skip to next-lowest pattern (diminishing returns)
- **All patterns above threshold** → patrol mode: re-baseline all patterns, report results, halt
- **All patterns above 0.90** → patrol mode (separate from threshold-based patrol)
- **Experiment count > 100** → warn about context window, suggest restart

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

**Backward compatibility:** Old rows with a `convergence` column are valid. Ignore the convergence column when computing composite — use the 4-layer formula. Old rows may have inflated scores from the v1 rubric (binary refinement/adaptiveness, 12-check visual with template-compliance gimmes). When resuming on a branch with v1 data, consider re-baselining all patterns with the v2 rubric.

---

## Error Handling

- **Docker not running:** Report error and halt. Do not retry.
- **Clean-room produces 0 PNGs:** A single failure in 3 is tolerable (score the other 2). If 2+ fail, halt.
- **evaluate_skill.py errors:** Log as `error` status, skip to next pattern.
- **Git conflicts:** Should never happen (single-file edits on a dedicated branch). If detected, halt.
- **Subagent failure:** If the evaluation subagent fails or returns malformed JSON, log as `error` status, skip to next pattern.

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
