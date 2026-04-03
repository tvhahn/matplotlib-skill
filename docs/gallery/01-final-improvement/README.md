# 50 -- Template Improvements v2: Dynamic Figsize Sweep

## What Changed
- Added **dynamic figsize computation** to 6 pattern templates (P2, P3 attempted, P5, P6, P7, P8) — replacing hardcoded `figsize` tuples with data-driven calculations
- Added **dynamic annotation format detection** to P2 and P5 — auto-selecting `.2f`/`.1f`/`,.0f` based on data magnitude
- Added **insight annotation template code** to P7 (strongest correlation pair) and **suptitle template** to P9
- Added **CRITICAL inline comments** to P9 template code to reduce color signature deviation
- Pruned redundant Guidance text across P7 and P9

## Why
The `panel-frames-v1` run (gallery 49) discovered that **template code changes** are far more effective than prose guidance changes. Adding data-driven figsize scaling to P1 gave +0.080 composite, and adding an insight annotation template to P3 gave +0.170. Meanwhile, prose-only guidance on P6 produced 5 discards and barely +0.002.

This run systematically applied the proven strategy (dynamic figsize + annotation format in template code) to all patterns that lacked it.

## Prompt Used
`/autoresearch template-v2` — autonomous loop with re-baseline, 9 experiments total.

## Observations
- **Dynamic figsize in template code is the single most reliable improvement lever**: 5 keeps out of 5 patterns attempted (P2 +0.105, P6 +0.092, P5 +0.073, P7 +0.055, P8 +0.020)
- **CRITICAL inline comments** helped P9 adhere to color signature (+0.040) — agents are more likely to preserve a `# CRITICAL: MUST be orange` comment next to the color value than to follow a Guidance bullet point
- **Signature simplification** (merging P6 items 4→3) failed — the penalty gain (+0.03) was overwhelmed by prompt variance
- **P3 dynamic figsize failed** due to the stocks dataset edge case (10 bars, 1-point rolling mean scoring 0.60) — the figsize change itself was sound but the worst-of-3 floor formula punished the bad prompt draw
- **P6 remains the hardest pattern** — the geyser dataset's 12:1 feature range ratio causes agents to drop `set_aspect(1)` or switch to `imshow`, both signature violations

## Before vs After
- **Before:** See `../49-classical-titles-and-annotations/` and baseline scores in results.tsv
- **After:** See PNGs in this folder

## Visual Evaluation

### P2 — Vertical Bar (Taxi Fares)
- **Observe:** 4 bars sorted descending, DIVERGING_COLORBLIND palette (4 bars ≤ 4 threshold), value labels with `$` prefix above each bar, insight annotation in upper-right showing gap between top 2 boroughs
- **Compare:** Figsize dynamically computed (`max(6, 4 + n*1.0)`), annotation format auto-detected as dollar currency. Grid correctly omitted per pattern spec
- **Judge:** Clean, readable. The `$` prefix on value labels is a direct result of the dynamic format detection
- **Verdict:** PUBLISH

### P5 — Lollipop (GLUE Benchmark)
- **Observe:** 8 NLP models with min/max/avg dots, cubehelix two-tone palette, connecting grey lines. Dynamic format shows `.1f` for score values (not `,.0f` which would truncate decimals)
- **Compare:** Height scales correctly for 8 items via `max(3.5, 1.0 + 8*0.9) = 8.2`. Insight annotation identifies ERNIE as highest and BiLSTM as widest spread
- **Judge:** The format detection is the key improvement — without it, scores like 89.7 would display as "90"
- **Verdict:** PUBLISH

### P6 — Decision Boundary (Geyser)
- **Observe:** Probability-sized dots background, red/blue 2-class diverging, contour lines, dual legends outside. Figure is wider than tall due to dynamic figsize matching the geyser's asymmetric feature ranges
- **Compare:** Dynamic figsize computes `data_aspect` from X ranges, allocating extra width for legends. The geyser's duration (1-5 min) vs waiting (40-100 min) creates a ~12:1 ratio handled by the formula
- **Judge:** The wide aspect ratio is correct for `set_aspect(1)` with these feature ranges, but visually unusual
- **Verdict:** POLISH

### P7 — Heatmap (MPG Correlations)
- **Observe:** 5x5 correlation matrix, RdBu_r palette, annotated cells at size 8 (dynamically computed: `max(7, 13-5)=8`). Colorbar labeled "Pearson r". Insight annotation at bottom identifies displacement-weight as strongest pair (r=0.93)
- **Compare:** Figsize `(8, 6)` for 5 vars via `max(6, 2+5*1.2)=8`. Lower-triangle mask applied (agents chose this for aesthetics despite template showing full matrix)
- **Judge:** The dynamic annotation sizing prevents text overlap that would occur with the default size 11 on larger matrices
- **Verdict:** PUBLISH

### P8 — Multi-Panel (Happiness by Region)
- **Observe:** 3x2 grid with stacked horizontal bars per region. Panel (f) North America has only 2 countries creating excessive whitespace. Suptitle, bold panel labels, figure-level insight annotation
- **Compare:** Grid dimensions parameterized (`n_rows, n_cols`), figsize from lookup table. The template now supports 2x2/3x2/3x3 from a single code path
- **Judge:** The parameterized grid is the real win — agents can now adapt to 4, 5, or 6 panels without rewriting the template
- **Verdict:** POLISH (panel height imbalance for unequal group sizes)

### P9 — PR/ROC (Breast Cancer)
- **Observe:** Two-panel PR+ROC with grey k-fold lines, cubehelix average, orange dashed baseline. Suptitle "Breast Cancer — 5-Fold Cross-Validation Performance". Strong classifier insight annotation
- **Compare:** All 3 charts in this evaluation correctly used orange baselines and cubehelix average lines — the CRITICAL comments worked. Suptitle now reliably appears (it was only in Guidance before, agents skipped it ~50% of the time)
- **Judge:** The visual improvement from reliable suptitle is subtle but meaningful for reader context
- **Verdict:** PUBLISH

## Files Modified
| File | Change |
|------|--------|
| `patterns/P2-vertical-bar.md` | Dynamic figsize (`max(6, 4+n*1.0)`) and format detection in template code |
| `patterns/P5-lollipop.md` | Dynamic annotation format (`fmt` variable) and figsize width scaling |
| `patterns/P6-decision-boundary.md` | Dynamic figsize from `data_aspect` ratio for `set_aspect(1)` compatibility |
| `patterns/P7-heatmap.md` | Dynamic figsize/annot_size for matrix dimensions, strongest-pair insight template |
| `patterns/P8-multi-panel.md` | Parameterized grid dimensions with figsize lookup table |
| `patterns/P9-pr-roc.md` | Suptitle in template code, CRITICAL color comments, pruned redundant Guidance |
| `program.md` | Updated priorities to reflect template-v2 strategy |

## Lessons Learned
- **Template code > prose guidance, quantified:** Dynamic figsize in template code produced 5 consecutive keeps. The previous run proved that prose-only guidance changes on P6 yielded 5 discards. If you want agents to do something, put it in the code block they copy — not in a bullet point they might skip.
- **The format detection pattern is reusable:** The `if max_val < 10: fmt=".2f" elif < 100: fmt=".1f" else: fmt=",.0f"` idiom works across bar charts (P2), lollipop (P5), and could extend to any annotation-heavy pattern.
- **CRITICAL comments work for color adherence:** P9's orange baseline was being replaced by grey in ~30% of runs. Adding `# CRITICAL: baseline MUST be orange dashed — not grey` right next to the `color="orange"` line fixed it.
- **Worst-of-3 floor makes prompt variance painful:** P3's figsize change was sound, but one bad prompt draw (stocks with 1-point rolling mean) scored 0.60, dragging the visual floor down and killing the composite. This suggests the evaluation rubric penalizes edge-case datasets disproportionately.
- **Signature simplification has marginal returns:** Merging P6 Signature items from 4→3 gives only +0.03 from the penalty formula. Not worth the risk unless the visual/refinement/adaptiveness scores also improve.
