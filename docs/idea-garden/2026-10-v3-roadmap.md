# v3 Roadmap — Taking the Skill to the Next Level

*October 2026. A proposal, not a plan of record. Built from three parallel research
passes: an audit of Rougier's* Scientific Visualization *book repo, a web survey
(other chart skills, LLM chart-generation papers, chart-choice canon, chart linting),
and an internal audit of the skill, checker and v2 benchmark judgements.*

## TL;DR

The v2 skill is good at *styling* a chart once it knows what chart to make. The next
level is three things it can't do yet:

1. **See Tim's taste, not just read about it.** Today the taste lives only in prose.
   Ship exemplar images, and have an independent critic compare against them.
2. **Choose the chart.** Route by *intent × data shape* and cover the charts the
   dataviz canon recommends most (slope, dumbbell, stacked/100%, ECDF, ridgeline,
   training curves, confusion matrix).
3. **Catch dishonest and inaccessible charts in code.** The checker finds collisions;
   it doesn't find a bar axis that doesn't start at zero, a red/grey pair that
   collapses for protanopes, or a `$6 to $230` mathtext bug.

Rougier's book fits best as a **craft layer**, not a chart catalogue: about a dozen
matplotlib idioms that make labels, lines and panels read better (halo text, blended
transforms, line casing, highlight-in-small-multiples). Most of his showcase figures
(Escher, 3D, domain colouring) conflict with the despined, minimal identity, and the
book has no slope, dumbbell or waffle charts.

**Recommendation:** do Phase 0 (debt + eval hardening), then **Direction A
(exemplars + independent critic)** as the v3 headline, carrying the Rougier craft
layer with it. Direction B (router + new charts) is v3.1.


## Status (implemented on `claude/kind-gates-bgjbvg`)

| Item | Status |
|---|---|
| Phase 0 template debt (rows 1, 3, 6, 7, 8) | Done |
| Phase 0 rows 2, 4, 5 (Tim's call) | **Pending Tim.** Hexes and P2's Signature unchanged; the non-destructive default was taken: the checker flags colour-only encodings (CVD-simulated) and faint text, and light hues are darkened only when used as text |
| Eval hardening: 3 runs/cell, both-order pairwise, judge agreement, P6 + mode prompts, checker negative tests | Done (`scripts/judge.py`, `tests/test_checker.py`) |
| Human anchor set | Tooling done; ratings **pending Tim** |
| A. Exemplars + independent critic | Done. Pairwise 73–77% of decided pairs vs v2; misses on absolute targets, Haiku variety and cost — see `docs/benchmarks/2026-10-skill-v3/` |
| B. Router + new chart types | Done (P10–P13); all acceptance tests pass |
| C. Checker v3 | Done, except the data-fidelity dump (deferred) |
| D. Rougier craft layer | Done (style-reference "Craft") |
| E. Output modes (physical sizes, slides, notebook checks, restyle path) | Not started; alt text added to the report step |

---

## Phase 0 — Fix before building (small, do regardless)

Real defects the audit found in v2. Each one is small. Rows marked **Tim's call**
change colours Tim chose, so they are decisions, not fixes (the README already keeps
the P9 orange baseline on those grounds). Options for row 4: swap `#555555` for a
lighter grey or move it later in the order; or keep the hexes and rely on a second
encoding (marker/linestyle/direct label) that the checker enforces.

| # | Defect | Where |
|---|---|---|
| 1 | P9 and P6 templates still build a detached below-axes footer the style reference forbids | `P9-pr-roc.md:81`, `P6-decision-boundary.md:71` |
| 2 | **Tim's call.** P2 Signature locks `DIVERGING_COLORBLIND` for ≤4 single-series bars; style-reference says one series → one colour | `P2-vertical-bar.md:48` |
| 3 | Grouped-bar Signature says DIVERGING; style-reference says CATEGORICAL for nominal | `other-charts.md` |
| 4 | **Tim's call.** `CATEGORICAL` red `#d73027` vs grey `#555555`: ΔE 7.7 under protanopia (validator WARN). Red vs blue `#4575b4` have near-identical luminance (0.167 vs 0.173), so they merge in greyscale print | `style-reference.md` |
| 5 | **Tim's call.** Orange `#fc8d59` (2.25:1) and light blue `#91bfdb` (1.92:1) are below 3:1 contrast on white — too faint for thin lines | `style-reference.md` |
| 6 | P8 template references undefined `all_values/x_data/y_last` (the test injects them); `hspace_map` lacks 3×3 | `P8-multi-panel.md` |
| 7 | Takeaway subtitle missing from P3, P6, P9 and all four other-charts templates; other-charts titles lack `weight="semibold"` | patterns |
| 8 | P1 hardcodes `%` in value labels | `P1-horizontal-bar.md:24` |

**Eval hardening (prerequisite for measuring v3):**
- ≥3 runs per cell (Haiku P9 already flipped between runs at n=1).
- Pairwise judging in both A/B orders; report inter-judge agreement.
- Add P6 and the output modes (notebook, function, publication, quick) to the prompts.
- A **human anchor set**: Tim rates ~30 charts once. VisJudge-Bench reportedly found
  GPT-5 judges correlate with expert ratings at only r ≈ 0.43 (unverified), so the pairwise result stays the
  headline and the anchor set calibrates the judges.
- **Negative tests for the checker**: today `test_patterns.py` only proves clean
  templates pass; nothing proves broken charts fail.

---

## The menu (ranked)

### A. Taste you can see — exemplars + independent critic ★ recommended

**What.**
- `skills/matplotlib/exemplars/` — one or two gold PNGs per pattern: Tim's originals
  from `docs/gallery/00-original-inspiration/` and the best v2 outputs, re-rendered
  with the craft layer below. Each exemplar ships with a 3-line caption: the
  **Signature** to keep, and what **varied** with the data.
- Step 6 changes from "look at your PNG" to: a **fresh vision subagent** that sees
  only the request, the PNG and the pattern's exemplar (not the code). It describes
  the chart literally, then diffs it against the step-1 takeaway and the exemplar's
  Signature (the describe→diff method from ChartIR).

**Why.**
- ChartMimic's "Customized Mimic" task — write code for new data while keeping a
  reference chart's style — is exactly the job an exemplar sets up, and GPT-4o already
  scores 83.2 on it (81.2 on straight copying). Models use a reference image well;
  today the skill gives them none. (This shows the channel works, not that exemplars
  will beat v2's prose — the acceptance test below decides that.)
- Visual feedback is the best-measured lever in the literature. MatPlotAgent (GPT-4,
  MatPlotBench): direct decoding 48.9 → full agent 61.2; removing only the visual
  feedback drops it to 53.4. METAL, which splits critique by modality, reports +5.2%
  over the prior best, rising with token budget. A model judging its own PNG tends to
  approve it — which matches Opus's colliding callouts in v2.

**Risk — the blog's own lesson.** Exemplars can re-create the uniformity trap
("measure uniformity, you get uniform"). Mitigations: two exemplars per pattern
on different data; captions that name what *should* vary; the critic grades the
Signature, not resemblance.

**Feasibility.** `SKILL.md` `allowed-tools` is `Bash, Write, Edit, Read, Glob, Grep` —
no `Agent`, so the critic needs `Agent` added (or a forked-context critic skill).
`scripts/benchmark.py` passes no tool allow/deny flags, so clean rooms won't block it,
but confirm the critic actually fires in the transcript tool counts.

**Cost.** ~1–1.5k tokens per exemplar image, only the matching pattern's is loaded.
The critic adds a subagent call (~+30–50% cost per chart, estimate).

**Acceptance test (vs v2, eval-hardened harness).**
- Blind pairwise v3 vs v2: ≥ 65% wins across 3 models × 12 prompts × 3 runs, both orders.
- Mean judge score ≥ 8.3 (v2: Sonnet 7.8, Opus 7.8, Haiku 7.1); Haiku ≥ 7.8.
- No loss of variety: across 3 runs of one prompt, annotation text and placement
  differ in ≥ 2 of 3 (judge-checked).
- Cost per chart ≤ 1.5× v2.

### B. Pick the right chart — intent × data-shape router + new chart types

**What.**
- Replace the 10-row routing table with a matrix. **Rows:** the FT Visual Vocabulary
  intents (deviation, correlation, ranking, distribution, change over time, magnitude,
  part-to-whole, flow). **Columns:** category count (≤6 / 7–15 / >15), series count,
  time points (two / few / many), nominal vs ordinal, signed vs unsigned. **Cells:**
  default, alternative, avoid.
- Datawrapper's rules of thumb go straight into the cells: two time points → slope;
  few → columns; many → line; tangled lines → small multiples; cluttered scatter →
  2D histogram.
- New chart sections, in order: **slope**, **dot plot / dumbbell**, **stacked and 100%
  bar**, **ECDF**, **area with deviation shading**, **connected scatter** (the
  alternative to dual axes), **ridgeline**. Two more suit Tim's ML work: **training/loss
  curves** and **confusion matrix**.
- From Rougier: ridgeline (`anatomy/zorder-plots.py`), scatter with marginal
  histograms (`layout/standard-layout-2.py`), butterfly bars (`rules/rule-1.py`) as
  starting points, rewritten in the house style.
- Gate: only add a chart Tim has an opinion about. Each new one gets a Signature.

**Acceptance test.** 8 new prompts (one per new chart). Routed to the right file in
≥ 90% of 3 models × 3 runs. Mean judge on new prompts ≥ 7.8. No regression on the
original 12.

### C. Checker v3 — honesty and accessibility, in code

**What.** Deterministic checks on the live Figure:

- **Misleading charts.** Bar or area baseline not at zero (Wilke's proportional-ink
  rule: length/area must start at 0; position-only marks needn't); `twinx` dual axes;
  inverted axes; uneven tick spacing; decimal ticks on integer data (year 2010.5).
- **Colour.** Pairwise ΔE of the colours actually drawn, under deuteranopia/protanopia
  and in greyscale. WARN when two series differ by colour alone (same marker and
  linestyle). Text or thin lines below 3:1 contrast. `jet`/`rainbow`/`hsv` colormaps.
  A diverging colormap not centred on 0.
- **House style.** Text that isn't dimgrey. Detached footers (text at axes y < 0).
  Two or more unescaped `$` in one string (the shipped "6to230" bug). PDF and PNG not
  both saved. More than three annotations per panel.
- **Data fidelity.** Dump bar heights, line y-values and heatmap arrays to JSON so
  the model and the tests can compare them with the pandas aggregation.
- `--strict`: label-on-data WARNs fail the run. v2's final charts still carried 9 WARNs.

**Acceptance test.** A corpus of ≥ 20 deliberately broken scripts: ≥ 95% caught, and
0 false positives on every template and every v2 benchmark final script. Final-chart
WARNs in the benchmark: 9 → 0.

### D. Rougier craft layer

**What.** A new "Craft" section in `style-reference.md`, with idioms written in our own
code (the book's code is BSD-2 and can be adapted with credit; its prose is
CC BY-NC-SA and is not copied):

| Idiom | Upgrades | Fixes |
|---|---|---|
| White halo on annotation text **and** arrow (`patheffects.withStroke`) | P3, P4, P6, P7, scatter | Labels on dense strips (P4 weakness) without a box hiding the data |
| Highlight one series, grey the rest, per panel | P8, line > 6 series | P8 spaghetti end-labels |
| Blended transforms for reference-line labels (`get_xaxis_transform`) | histogram median, P3/P5 reference lines | Labels drifting when limits change |
| White casing under crossing lines, explicit zorder | line charts | Unreadable crossings |
| Emphasised tick label (colour + weight) | P1/P2 highlight | Encodes emphasis twice (principle 7) |
| Size legend with area ∝ value (`legend_elements`) | bubble scatter | "Add a size legend" has no idiom today |
| Zoom inset (`inset_axes` + `indicate_inset_zoom`) | P9 low-FPR corner, dense lines | — |
| Opaque tint instead of alpha for overlapping bands | P8 bands, CI bands | Muddy blended third colour |

Rejected from the book: offset/dropped spines and axis arrows (conflict with despine),
alternative font stacks (DejaVu Sans is identity), polar histograms and other
ornament-heavy showcases (principles 2 and 10), Material/rainbow palettes.

**Acceptance test.** Label-on-data WARNs in P4/P8 → 0. Pairwise win on the P4, P8 and
scatter prompts.

### E. Output modes — publication, slides, notebooks, restyle

**What.**
- **Publication presets in physical units.** Single column 89 mm / 3.5 in, double
  column 183 mm / 7 in; 7–9 pt text at final size. Today "publication" only means
  300 DPI, so a (14, 9) figure shrunk into a column prints 10 pt text at ~2.5 pt.
  The checker scales its minimum font size by target width ÷ figure width.
- **Slides mode**: fewer ticks, thicker lines, larger text, one message per figure.
- **Notebook and function modes can be checked**: add a harness snippet so step 5
  runs outside scripts.
- **Restyle path**: the description promises "restyle an existing figure" but
  SKILL.md has no workflow for it.
- Report step adds a one-sentence alt text.

**Acceptance test.** Prompt "single-column IEEE figure": width 3.5 in and min font
≥ 7 pt at final size, in 9/9 runs. Notebook and function prompts run the checker in
≥ 8/9 runs.

---

## Suggested sequencing

| Release | Contents | Why this order |
|---|---|---|
| v2.2 | Phase 0 debt + eval hardening + checker negative tests | Can't measure v3 without it |
| **v3** | **A (exemplars + critic) + D (craft layer)** + the cheap half of C (misleading-chart, colour, house-style checks) | Exemplars should already show the craft; the checker keeps the critic honest |
| v3.1 | B (router + new charts), each new chart with its own exemplar | Builds on A's exemplar format |
| v3.2 | E (output modes) + C's data-fidelity dump | Lower impact on benchmark, high for real use |

For the blog: v3 is a natural sequel. "I taught Claude my taste in words; then I
showed it." The exemplar uniformity risk and its mitigation is the same lesson as
the autoresearch episode, from the other side.

## Sources

Verified against the papers: ChartMimic (abstract + main results), MatPlotAgent
(Table 4), METAL (abstract). Reported by the research pass but **not yet verified**:
PlotGen's ablation figures, VisJudge-Bench's r ≈ 0.43, VisPath's +17%, Misviz's
99.7% precision. Check those before quoting them in the blog.

- Rougier, *Scientific Visualization: Python + Matplotlib* — https://github.com/rougier/scientific-visualization-book (code BSD-2; text CC BY-NC-SA 4.0). Ten Simple Rules chapter originally PLOS Comp Bio 2014.
- ChartMimic — https://arxiv.org/abs/2406.09961
- METAL — https://arxiv.org/abs/2502.17651
- PlotGen — https://arxiv.org/abs/2502.00988
- MatPlotAgent — https://arxiv.org/abs/2402.11453
- ChartIR — https://arxiv.org/abs/2506.14837
- VisEval — https://arxiv.org/abs/2407.00981
- VisJudge-Bench — https://arxiv.org/abs/2510.22373
- VisPath — https://arxiv.org/abs/2502.11140
- Misviz — https://arxiv.org/abs/2508.21675
- FT Visual Vocabulary — https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary
- Datawrapper chart types guide — https://www.datawrapper.de/blog/chart-types-guide
- Wilke, *Fundamentals of Data Visualization* — https://clauswilke.com/dataviz/ (proportional ink, directory of visualizations)
- Schwabish, five charts — https://policyviz.com/2021/02/08/five-charts-youve-never-used-but-should
- SciencePlots — https://github.com/garrettj403/SciencePlots
- Anthropic data-visualization skill — https://github.com/anthropics/knowledge-work-plugins/tree/main/data/skills/data-visualization
- colorspacious (CVD simulation) — https://colorspacious.readthedocs.io/
