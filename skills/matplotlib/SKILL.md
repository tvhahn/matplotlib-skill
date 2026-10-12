---
name: matplotlib
description: "Creates publication-quality matplotlib/seaborn charts in Python with an opinionated, despined, annotation-rich style (whitegrid, DejaVu Sans, ColorBrewer and cubehelix palettes, dimgrey text) and saves a reproducible script plus PDF/PNG. Use when the user asks for a chart, plot, graph, or figure from data in Python — bar, line, scatter, histogram, violin, lollipop, heatmap, small multiples, slope or dumbbell, stacked or 100% bar, area, ECDF, ridgeline, decision boundary, PR/ROC, training curves, or confusion matrix — or wants an existing matplotlib figure restyled. Also use for terse requests that only name a chart and a data file (e.g. 'PR and ROC curves from results.npz'): make the chart."
argument-hint: "[chart request, e.g. 'bar chart of accuracy by model from results.csv']"
allowed-tools: Bash, Write, Edit, Read, Glob, Grep, Agent
---

# Persona

You are an expert Python data-visualisation developer with strong, specific taste.
Default to the conventions in this skill unless the user asks otherwise or the
Design Philosophy clearly calls for something different.

# Design Philosophy

These principles take precedence over pattern defaults. When a pattern's default
conflicts with the communicative goal, adapt the pattern to serve the principle.

 1. Above all else, show the data. (Tufte — the prime directive)
 2. Every element earns its ink. (Data-ink ratio, reframed as a test)
 3. Prefer position over color, color over size. (Cleveland & McGill hierarchy, compressed)
 4. Grey is a color. White space is a feature. (Muth + Schwabish — the minimalist foundation)
 5. Despine, degrid, then add back only what the reader needs. (Tim's workflow, made explicit)
 6. Annotate the insight, not just the axis. (Cairo + Knaflic — charts should say something)
 7. Encode meaning twice — never rely on color alone. (Wilke/WCAG — accessibility as principle)
 8. Consistency across panels; variety across charts. (Multi-panel coherence vs. chart-type adaptation)
 9. The reader should never do arithmetic. (Cleveland — if they need to compare, plot the comparison)
10. When in doubt, remove. (Darkhorse "remove to improve" + Tufte "erase non-data-ink")

# Reference files

- `${CLAUDE_SKILL_DIR}/style-reference.md` — invariants, palettes, typography, titles, craft idioms, saving. Read it every time.
- One pattern file from the table below. Read only the one that matches.
- The exemplar PNGs the pattern file names (`${CLAUDE_SKILL_DIR}/exemplars/`). Look at them before writing code: they show the finished look on real data.
- `${CLAUDE_SKILL_DIR}/critic.md` — how to get the independent review in step 6.
- `${CLAUDE_SKILL_DIR}/scripts/check_figure.py` — run it (don't read it) to find overlaps, misleading scales, colour-only encodings and style drift.

| Pattern | File | Use for |
|---------|------|---------|
| P1 | `patterns/P1-horizontal-bar.md` | One value per category, ranked; long category names |
| P2 | `patterns/P2-vertical-bar.md` | One value per category, few short categories or a natural order |
| P3 | `patterns/P3-time-series.md` | Periodic values as **bars** with a rolling-mean line, above/below a reference |
| P4 | `patterns/P4-violin-strip.md` | Distributions compared across categories |
| P5 | `patterns/P5-lollipop.md` | Min/avg/max ranges per item, model comparisons |
| P6 | `patterns/P6-decision-boundary.md` | Classifier decision regions over two features |
| P7 | `patterns/P7-heatmap.md` | Correlation matrices, pivot tables, spectrograms |
| P8 | `patterns/P8-multi-panel.md` | Small multiples: one panel per group (2x2, 3x2, 3x3) |
| P9 | `patterns/P9-pr-roc.md` | Precision-recall and ROC curves |
| P10 | `patterns/P10-slope-dumbbell.md` | Two values per item: before/after, two years, rank change |
| P11 | `patterns/P11-part-to-whole.md` | Shares: 100% stacked bars, stacked area over time |
| P12 | `patterns/P12-distribution-ecdf-ridgeline.md` | ECDF for 2–4 groups; ridgeline for many ordered groups |
| P13 | `patterns/P13-training-diagnostics.md` | Training/validation curves, confusion matrix |
| — | `patterns/other-charts.md` | Line charts, scatter plots, histograms, grouped bars, anything else |

A plain "line chart over time" is `other-charts.md`, not P3. A scatter plot of two
variables is `other-charts.md`, not P6.

# Choosing the chart

When the request names a chart type, make that chart. When it names data and a
question but no chart, choose by what the reader must do and the shape of the data:

| The reader must… | Data shape | Use | Avoid |
|---|---|---|---|
| Rank or compare one value per category | nominal, long names or > 6 categories | P1 | pie; rotated tick labels |
| | ≤ 6 short or naturally ordered categories | P2 | |
| Compare two values per item | two time points, before/after | P10 slope (≤ 10 items, crossings matter) or dumbbell (more items, gap matters) | 2N grouped bars |
| Compare ranges per item | min/avg/max, fold scores | P5 | |
| Compare across two categorical variables | ≤ 4 subgroups | grouped bar (other-charts) | > 4 subgroups → P7 heatmap or P8 |
| See part-to-whole | shares at one time, few groups | P11 100% bars | pie, donut, 3-D |
| | composition over time | P11 stacked area | > 5 components (fold into "Other") |
| Follow change over time | many time points | line (other-charts) | bars for continuous time |
| | periodic values vs a reference | P3 | |
| | > 6 series | highlight 1–2 and grey the rest, or P8 small multiples | spaghetti; dual y-axes |
| See a distribution | one group | histogram (other-charts) | |
| | 2–6 groups, shape matters | P4 violin + strip | bar of means |
| | 2–4 groups, quantiles or thresholds matter | P12 ECDF | |
| | many ordered groups (months, years) | P12 ridgeline | |
| See a relationship | two continuous variables | scatter (other-charts); hexbin beyond ~5,000 points | dual y-axes |
| | many variable pairs | P7 correlation heatmap | |
| Evaluate a model | classifier scores | P9 PR/ROC | |
| | predicted vs true classes | P13 confusion matrix | |
| | training history | P13 training curves | |
| | decision regions over two features | P6 | |

Two measures on different scales never share an axis: use two panels, or index
both to 100 at the start.

# Workflow

Copy this checklist into your response and tick it off:

```
- [ ] 1. Understand the request and the one thing the reader should take away
- [ ] 2. Choose the chart; read style-reference.md, the pattern file, and look at its exemplars
- [ ] 3. Inspect the data (columns, dtypes, missing values, category order, group sizes)
- [ ] 4. Write the script into the working directory and run it
- [ ] 5. Run check_figure.py and fix every ERROR and WARN
- [ ] 6. Get an independent review of the PNG (critic.md) and fix what it finds (≤ 2 rounds)
- [ ] 7. Report files, the takeaway, and one improvement you would make next
```

## 1. Understand

Identify chart type, data source, columns (x, y, hue, facet), annotations wanted,
and output mode. Decide the **narrative intent** — comparison, trend, distribution,
composition, relationship, or emphasis — and the single takeaway. That takeaway
drives palette, ordering, and annotation choices.

If the request names no data and no chart type ("make a chart"), ask. If it names
data but no chart type, choose the chart that best answers the implied question and
proceed. A request that names a data file is a request to plot it; do not stop to
ask what to do with it.

Output mode:
- `.ipynb` context → notebook cell
- "add a function to …" → function mode
- "quick plot" / "exploratory" → standalone script, PNG only, 150 DPI
- "publication", "300 DPI", "high resolution" → standalone script, PDF+PNG, 300 DPI
- otherwise → standalone script, PDF+PNG, 150 DPI

## 2–3. Configure from the data

Pick the pattern with the tables above. Read its file, then Read the exemplar PNGs it
lists: they show the Signature on real data and how the rest adapted to that data.
Match the finish, not the content — your annotations, ordering and layout come from
your data and takeaway.

Start from the pattern template, keep its **Signature**, and adapt everything else
(figsize, font sizes, alpha, label format, legend position) to the data:
category count, label length, value range, point density.

Before writing the plot code, look at the data (`head`, dtypes, `isna().sum()` on
the columns you will use). In particular:
- **Missing values:** drop them only in the columns you plot —
  `df.dropna(subset=[...])`. A blanket `df.dropna()` silently discards rows that
  are missing an unrelated column — one mostly-empty notes column can remove most
  of the data and change every group average.
- **Category order:** keep natural orders (sizes, months, ratings, education
  levels, numeric codes). Sort by value only for nominal categories.
- **Aggregation:** compute it in pandas from the loaded file; never hardcode values.
- **Group sizes and caveats:** note `n` per group, groups that shrink over time
  (dropouts), and how a rolling window is aligned. Say so on the chart when it
  changes how the reader should read it (a tiny group, a centred window).

## 4. Write and run

Write the script into the current working directory (not a temp or scratch
directory) so the user keeps it. Run it with `uv run <script>.py`; if `uv` is not
installed, use `python <script>.py`.

### Standalone script (default)

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "matplotlib",
#     "seaborn",
#     "numpy",
#     "pandas",
# ]
# ///
```

- One `main()` with a numpy-style docstring (Parameters, Saves); no type hints
- Inline config values; no constants module
- Section comments: `# --- Style Setup ---`, `# --- Data ---`, `# --- Plot ---`, `# --- Save ---`
- Helpers only when logic genuinely repeats
- `Path("./figures").mkdir(exist_ok=True)`; save PDF+PNG to `./figures/`
- `if __name__ == "__main__": main()`

### Notebook cell
Flat script, comments instead of docstrings, `plt.show()` instead of `savefig`.

### Function
`def plot_thing(df, figsize=(10, 8), dpi=150):` — takes data, returns `fig, ax`,
numpy-style docstring, no type hints, no saving.

Dependencies: `matplotlib`, `seaborn`, `numpy`, `pandas` only (plus `scikit-learn`
when the user explicitly asks to fit a model).

## 5. Check

Run the checker on the script — it executes the script and inspects every figure:

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/check_figure.py <script>.py
```

It reports text collisions (titles, tick labels, annotations, legends), legends or
labels covering data, annotations spilling into other panels, empty panels, tiny
or faint text, misleading scales (bars not starting at zero, dual axes, inverted
axes), series that differ by colour alone, detached footers, mathtext `$` bugs, and
style drift (spines, tick marks, text colour, legend frame, DPI). Fix every
**ERROR** and re-run. Resolve each **WARN** too — move the label or legend off the
data, add a halo or a second encoding — unless it is deliberate (e.g. a label
inside its own bar). Fix **STYLE** items unless the user asked for that look.
`--strict` makes WARNs fail the run.

Also confirm in the code: `sns.set_theme(font_scale=1.0, style="whitegrid",
font="DejaVu Sans")`, `sns.despine(left=True, bottom=True)`, dimgrey annotation and
tick-label colour, legend frame kwargs, `bbox_inches="tight"`.

## 6. Review

Follow `${CLAUDE_SKILL_DIR}/critic.md`: hand the PNG, the request, your intended
takeaway and the pattern's exemplars to a fresh reviewer subagent that never sees
the code. It describes the chart literally, diffs it against the takeaway, and
returns ranked issues. Fix every BLOCKER and MAJOR, re-run the script and the
checker, then Read the PNG yourself and confirm:

1. **Fidelity:** right data, right columns, title matches content, values plausible.
2. **Integrity:** sensible axis ranges; bars start at zero; reference lines present
   where expected (diagonal, baseline, zero).
3. **Principles** (Design Philosophy numbers): data visible (1); main comparison
   encoded by position (3); at least one annotation states a finding, placed at the
   data it describes (6); series distinguishable without colour (7); consistent
   panels (8); no mental arithmetic needed (9).
4. **Layout:** balanced whitespace, nothing cramped, annotations near their data.
5. **Pattern rules:** the pattern's Signature is present.

At most two review rounds. If problems remain, report them and ask how to proceed.

## 7. Report

If the user asked for publication quality, re-render at 300 DPI. Then tell the
user: the files written, the takeaway the chart shows, one sentence of alt text,
anything the reviewer raised that you chose not to change (and why), and one
improvement you would make next. Offer refinements.
