# Scoring v2 Technical Specification

Date: 2026-03-21

## Composite Formula

```
composite = compliance x (0.50 x visual + 0.25 x refinement + 0.25 x adaptiveness) x signature_penalty
```

Weights unchanged from v1. What changes is the range of each dimension.

### Expected Score Ranges

| Dimension | v1 Range (observed) | v2 Range (expected) |
|-----------|-------------------|-------------------|
| Compliance | 1.0 (constant) | 1.0 (constant) |
| Visual | 0.82–1.00 | 0.45–0.85 |
| Refinement | 0.80–1.00 | 0.50–0.90 |
| Adaptiveness | 0.60–1.00 | 0.40–0.85 |
| **Composite** | **0.77–1.00** | **0.45–0.75** |

---

## Layer 1: Compliance (binary gate)

Checked by `evaluate_skill.py` — static code analysis, no visual inspection.

### Existing checks (unchanged)
1. `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")` present
2. `sns.despine(left=True, bottom=True)` present
3. `dpi=150` (or 300 if publication)
4. `bbox_inches="tight"` on savefig
5. PDF+PNG dual save
6. Data loaded from CSV/NPZ with `dropna`

### New checks (moved from visual rubric)
7. Palette matches pattern spec (e.g., `palette="Blues_d"` for P1)
8. Title uses `loc="left"` and `pad=` specified
9. Annotation text uses `color="dimgrey"`
10. Legend includes `frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey"`
11. `tick_params` includes `length=0, labelcolor="dimgrey"`

**Score:** 1.0 if all pass, 0.0 if any fail. Compliance is a gate — failure zeroes the entire composite.

---

## Layer 2: Visual Quality (10-check graded rubric)

Scored by the evaluator looking at rendered PNGs. 10 checks, each scored 0/1/2. Applied to each of 3 PNGs independently.

### Tier 2A — Craft checks (6 checks)

| # | Check | 0 | 1 | 2 |
|---|-------|---|---|---|
| 1 | **Layout balance** | Overlapping elements or wasted space (>30% unused) | Minor spacing issues (tight labels, slightly wide margins) | Balanced whitespace, nothing crowded, proportional gaps |
| 2 | **Annotation placement & quality** | Missing annotations when data warrants them, OR overlapping text | Annotations present, correctly placed, generic format | Annotations highlight specific data insights, well-placed, no overlaps |
| 3 | **Colorblind safety** | Red-green encoding without diverging scheme | Partially safe (sequential used for categorical) | Confirmed safe per pattern spec |
| 4 | **Data-ink ratio** | Chartjunk (unnecessary borders, shadows, fills, decorations) | Mostly clean, one unnecessary element | Minimal non-data ink, every mark carries information |
| 5 | **Color effectiveness** | Palette doesn't serve the data (wrong type for comparison) | Correct palette family, generic application | Palette choices reinforce data meaning (emphasis where intended, semantic mapping) |
| 6 | **Axis/scale appropriateness** | Wrong scale type, misleading range, truncated baseline for bars | Correct scale, minor range issue | Appropriate scale, sensible range, zero-baseline for bars, units present |

### Tier 2B — Design excellence checks (4 checks, deliberately hard)

**Scoring guidance:** "A score of 2 on checks 7-10 should be rare. Default to 1 when the chart is competent but unremarkable. Reserve 2 for choices that a skilled human designer would make. Justify every score of 2 with a specific observation."

| # | Check | 0 | 1 | 2 |
|---|-------|---|---|---|
| 7 | **Narrative coherence** | Title is generic/descriptive only ("Sales by Region") | Title suggests a finding, visual partially supports it | Title states a clear finding, visual evidence directly supports it — chart argues a point |
| 8 | **Typography hierarchy** | All text same weight/size, no visual priority | Some hierarchy (title larger), but labels compete for attention | Clear progression: title > subtitle > labels > annotations. Professional editorial quality |
| 9 | **Reader self-sufficiency** | Reader needs external context to interpret (no units, unlabeled axes, ambiguous categories) | Most context present, one gap (missing units or vague axis label) | Reader unfamiliar with dataset can fully interpret. Units clear, values labeled, axes descriptive |
| 10 | **Adaptive composition** | Template defaults applied without regard for data (fixed figsize, default positions) | 1-2 layout choices adapted to data | Layout demonstrates understanding of the specific dataset. Choices are non-obvious and improve communication |

### Red flag caps (per-check, not per-PNG)

If ANY of these are present in a PNG, reduce the **specific affected check** to 0:
- Overlapping text -> check 2 (annotation quality) = 0
- Clipped content -> check 1 (layout balance) = 0
- Default matplotlib legend (no frame styling visible) -> compliance failure (Layer 1), not visual penalty
- Visible axis spines -> compliance failure (Layer 1), not visual penalty

Note: legend and spine issues are now compliance checks, not visual penalties.

### Scoring formula

Per-PNG score: `sum of 10 checks / 20`

Aggregate across 3 PNGs with worst-of-3 floor:
```
worst_png = min(png_1_score, png_2_score, png_3_score)
mean_all = mean(png_1_score, png_2_score, png_3_score)
visual = max(0.4 x worst_png + 0.6 x mean_all, mean_all x 0.85)
```

This ensures one catastrophic chart drags the score down meaningfully, while three consistent charts aren't penalized beyond the average.

---

## Layer 3: Refinement (5-check graded rubric)

Scored by reading 3 generated `.py` files. Each check scored 0/1/2/3.

| # | Check | 0 | 1 | 2 | 3 |
|---|-------|---|---|---|---|
| 1 | **No hardcoded data** | Displayed values hardcoded as literals | Most values from DataFrame, some literals remain | All displayed values from DataFrame | All from data + handles edge cases (empty DataFrame, single-row) |
| 2 | **Defensive data handling** | No defensive coding | Basic `dropna()` after load | `dropna()` + type checks or column existence validation | `dropna()` + type checks + fallback values + informative error messages |
| 3 | **Code organization** | Monolithic block, no comments, poor variable names | Section comments present but flat structure; generic variable names | Logical sections (`# --- Style ---`, `# --- Data ---`), descriptive names, comments at key steps | Publication-quality: helper functions where logic repeats, consistent naming, docstring explains intent and parameters |
| 4 | **Consistent approach** | 3 runs take fundamentally different structural approaches | 2 similar approaches, 1 divergent | Same structural approach across 3 runs, minor variation in details | Identical structural approach with data-appropriate adaptations (same skeleton, different data-driven tweaks) |
| 5 | **Save convention** | Missing PDF or PNG, wrong dpi, missing bbox_inches | Correct formats and dpi, missing `bbox_inches="tight"` | PDF+PNG, dpi=150, `bbox_inches="tight"` | + `figures/` dir created with `mkdir(exist_ok=True)`, descriptive filename |

**Score:** `total / 15`

---

## Layer 4: Adaptiveness (5-check graded rubric)

Scored by reading 3 PNGs and 3 `.py` files together. Each check scored 0/1/2/3.

| # | Check | 0 | 1 | 2 | 3 |
|---|-------|---|---|---|---|
| 1 | **Figsize scales for data** | Fixed template figsize regardless of data volume | Width OR height adapted (e.g., taller for more categories) | Both dimensions adapted for data properties | Adaptive + aspect ratio matches content type (e.g., square for correlation, wide for time series) |
| 2 | **Annotations reflect data** | Only generic labels copied from template | Data values present but generic format (e.g., all `.2f` regardless of magnitude) | Data-specific values with appropriate precision and formatting | Annotations highlight specific insights or outliers, not just values |
| 3 | **Legend avoids occlusion** | Legend covers data points or key features | Legend placed outside data range but position is template default | Legend positioned to actively minimize occlusion for this specific dataset | Legend placement considers data density, visual hierarchy, and available whitespace |
| 4 | **Palette matches semantics** | Random/default palette with no semantic relationship | Correct palette family from pattern spec | Family + direction matches data semantics (diverging for +/-, sequential for ranking) | + emphasis color used meaningfully to highlight specific data points or categories |
| 5 | **Data-driven choices** | Pure template copy-paste with only column names changed | 1 data-driven adaptation beyond template | 2-3 data-driven adaptations (figsize, annotation format, sort order, tick formatting) | 4+ adaptations that demonstrate genuine understanding of the dataset's story |

**Score:** `total / 15`

---

## Signature Penalty

Counts bullet points in the target pattern's "Signature" section.

### v1 (linear, starts at 5)
```
penalty = min(1.0, 1.0 - 0.05 x max(0, count - 4))
```

### v2 (quadratic, starts at 4)
```
penalty = min(1.0, 1.0 - 0.03 x max(0, count - 3)^2)
```

| Signature items | v1 penalty | v2 penalty |
|----------------|-----------|-----------|
| 3 | 1.00 | 1.00 |
| 4 | 1.00 | 0.97 |
| 5 | 0.95 | 0.88 |
| 6 | 0.90 | 0.73 |
| 7 | 0.85 | 0.52 |
| 8 | 0.80 | 0.25 |

The quadratic curve makes over-specification dramatically more costly and structurally favors simplification (removing items improves scores).

---

## Circuit Breakers

### Unchanged from v1
- **10 consecutive discards** on same pattern -> skip to next-lowest
- **Docker failure** (2+ of 3 runs fail) -> halt immediately
- **All patterns above threshold** -> patrol mode

### New in v2
- **Pattern above 0.90 composite** -> skip to next-lowest pattern (don't optimize further)
- **All patterns above 0.90** -> patrol mode (re-baseline, report, halt)
- **Experiment count > 100** -> warn about context (raised from 50 due to subagent architecture)

---

## Prompt Holdout Set

Added to Step 0 setup:

1. For each pattern, split the prompt pool:
   - **Train prompts** (first 70%): Used during autoresearch iterations
   - **Holdout prompts** (last 30%): Reserved for checkpoint evaluation

2. Every 10 experiments, run holdout evaluation:
   - Use holdout prompts instead of train prompts
   - Score with the same rubric
   - Compare holdout scores to train scores

3. **Overfitting signal:** If train scores improve by > 0.10 while holdout scores are flat or declining, flag "potential rubric overfitting" and suggest:
   - Human review of recent changes
   - Reverting to last holdout-validated version
   - Switching to a different improvement strategy

---

## Subagent Evaluation Architecture

### Orchestrator responsibilities
- Step 0: Setup, read program.md, parse arguments
- Step 1: Run compliance check via `evaluate_skill.py`
- Step 2: Pick target pattern (from in-memory best-per-pattern dict)
- Step 3: Propose change (read pattern file, identify weakest layer)
- Step 4: Apply change and commit
- Step 5: Run compliance check, then **spawn evaluation subagent**
- Step 6: Receive JSON scores, compute composite, log to results.tsv, decide keep/discard
- Step 7: Loop

### Evaluation subagent responsibilities
- Run 3 parallel clean rooms with provided prompts
- Read 3 PNGs and 3 .py files
- Apply Layer 2 (visual), Layer 3 (refinement), Layer 4 (adaptiveness) rubrics
- Return compact JSON:
  ```json
  {"visual": 0.XX, "refinement": 0.XX, "adaptiveness": 0.XX, "issues": ["issue 1", "issue 2", "issue 3"]}
  ```

### Context budget
- Orchestrator per-iteration: ~1,100 tokens (down from ~13,600)
- Subagent per-invocation: ~15,000 tokens (fresh context each time)
- Feasible iterations before context limit: 100+ (up from ~50)
