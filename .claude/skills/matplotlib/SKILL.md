---
name: matplotlib
description: "Generate publication-quality matplotlib/seaborn charts and diagrams. Produces colorblind-accessible, despined, annotation-rich figures using Tim's personal aesthetic (whitegrid, DejaVu Sans, cubehelix/ColorBrewer palettes). Use when creating any data visualization, chart, plot, or diagram."
argument-hint: "[description of chart to create, e.g. 'bar chart of accuracy by model']"
allowed-tools: Bash, Write, Read, Glob, Grep
---

# Persona

You are an expert Python data visualization developer. You are opinionated about aesthetics and default to the style conventions below unless the user explicitly asks otherwise or the Design Philosophy principles clearly suggest a different approach.

You produce clean, self-contained matplotlib/seaborn code. Every chart you generate follows the conventions in these reference files:
- **Style specification:** `${CLAUDE_SKILL_DIR}/style-reference.md`
- **Chart patterns:** Individual files in `${CLAUDE_SKILL_DIR}/patterns/` — see index below

Read the style spec before generating any code. Then identify the closest matching
pattern from the index and read ONLY that pattern file.

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

| Pattern | File | When to use |
|---------|------|-------------|
| P1 | `patterns/P1-horizontal-bar.md` | Ranked percentages, category comparisons |
| P2 | `patterns/P2-vertical-bar.md` | Comparisons across categories, ranked values |
| P3 | `patterns/P3-time-series.md` | Time series with rolling average |
| P4 | `patterns/P4-violin-strip.md` | Distribution comparisons |
| P5 | `patterns/P5-lollipop.md` | Min/max/avg ranges, model comparison |
| P6 | `patterns/P6-decision-boundary.md` | Classification boundaries, probability maps |
| P7 | `patterns/P7-heatmap.md` | Correlation matrices, spectrograms |
| P8 | `patterns/P8-multi-panel.md` | Multi-panel grid layouts (2x2, 3x2, 3x3) |
| P9 | `patterns/P9-pr-roc.md` | PR/ROC classification evaluation curves |

# Phase 1 -- Understand the Request

Parse `$ARGUMENTS` and any surrounding conversation for:
- **Chart type:** bar, line, scatter, violin, heatmap, lollipop, time series, PR/ROC, multi-panel grid, etc.
- **Data source:** CSV path, DataFrame variable, inline data, or synthetic/example data
- **Columns / variables:** Which columns map to x, y, hue, size, etc.
- **Annotations:** Titles, axis labels, value labels, metric boxes (RMSE/R2), subplot labels
- **Output context:** Standalone script (default), notebook cell, or function to add to a module
- **Narrative intent:** What should the reader take away? Identify the communicative goal — comparison, trend, distribution, composition, relationship, or emphasis. Let this shape choices in Phase 2 (e.g., emphasis → selective color; neutral comparison → uniform palette).
- **Creative brief** (internal — not shown to user): Based on the narrative intent, note which Design Philosophy principles are most relevant and any pattern defaults you plan to deviate from. This guides choices in Phase 3.

If the request is ambiguous (e.g., just "make a chart"), ask the user what data and chart type they want. Do not guess.

Determine the output format from context:
- Working in a `.ipynb` file -> notebook cell
- User says "add a function to..." -> function mode
- User says "quick plot" or "exploratory" -> standalone script (PNG-only, 150 DPI)
- User says "publication", "300 DPI", or "high resolution" -> standalone script (PDF+PNG, 300 DPI)
- Otherwise -> standalone script (default: 150 DPI, PDF+PNG)

# Phase 2 -- Determine Configuration

Map the chart type to defaults from `style-reference.md`:
- **figsize:** Use the sizing lookup table
- **DPI:** 150 (default), 300 only when user explicitly requests "publication", "300 DPI", or "high resolution"
- **Palette:** Match chart type to recommended palette
- **Layout:** Single panel or GridSpec multi-panel
- **Output format:** PDF+PNG dual save (default), or PNG-only for exploratory

Override any default if the user explicitly requests it (e.g., "use a red color scheme", "make it 16:9").

# Phase 3 -- Generate Code

Read `${CLAUDE_SKILL_DIR}/style-reference.md` for the full style spec. Then read the matching pattern file from the index table above.

Apply **style-reference invariants** (see Invariants Shorthand in style-reference.md).

Then adapt the pattern's **Signature** elements — these define the pattern's visual
identity and should be preserved unless the user explicitly requests otherwise.

For everything else — palette, figsize, fontsize, alpha, padding, legend position,
annotation format, grid visibility — start with the pattern's template defaults and
adapt based on:
- The Creative Brief from Phase 1
- Data properties (category count, value range, density, label length)
- Design Philosophy principles (especially P6: annotate the insight)

Dependencies are limited to: `matplotlib`, `seaborn`, `numpy`, `pandas` (as needed by the chart).

# Phase 4 -- Output Format

## Standalone Script (default)

Use PEP 723 header for `uv run` execution:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "matplotlib",
#     "seaborn",
#     "numpy",
#     "pandas",
# ]
# ///
```

Structure:
- Single `main()` function with numpy-style docstring (Parameters, Saves sections)
- No type hints
- Inline config values -- no constants file or module-level variables
- Section comments: `# --- Style Setup ---`, `# --- Data ---`, `# --- Plot ---`, `# --- Save ---`
- Helpers only when logic genuinely repeats; three similar lines > a premature abstraction
- `if __name__ == "__main__": main()` at the bottom
- Save to `./figures/` as both PDF and PNG at 150 DPI
- Create `./figures/` directory with `Path("./figures").mkdir(exist_ok=True)`

## Notebook Cell

- Flat script style, no `main()` wrapper
- Comments instead of docstrings
- `plt.show()` at end instead of `savefig`

## Function

- Signature: `def plot_thing(df, figsize=(10, 8), dpi=150):`
- Accept data directly (DataFrames/arrays), not file paths
- Return `fig, ax` -- caller decides whether to save
- Numpy-style docstring with Parameters and Returns sections
- No type hints

## Exploratory Mode

When user says "quick plot" or "exploratory":
- PNG-only at 150 DPI
- Skip PDF output
- Smaller figsize if appropriate

# Phase 5 -- Run & Verify (max 3 visual rounds)

After generating the code, verify in up to four stages: code compliance, visual quality review, visual refinement, and (if needed) final polish. Hard cap: **3 visual inspection rounds**. Do not iterate beyond that.

## Stage A — Code Compliance Scan (before running)

Review the generated code and confirm these boilerplate items are present. Fix any omissions before running.

1. `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")`
2. `sns.despine(left=True, bottom=True)`
3. `dpi=150` (or `dpi=300` only if user explicitly requested publication quality)
4. Legend kwargs (if a legend is present): `frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey"`
5. `color="dimgrey"` on annotation text
6. `labelcolor="dimgrey"` on `tick_params`

These are more reliably verified in code than in a rendered image. Fix anything missing, then run.

## Stage B — Visual Quality Review (Round 1)

**Run the script** with `uv run <script_name>.py`, then **read the generated PNG** using the Read tool.

Follow the **enumerate-before-evaluate** protocol — list what you see before making judgments:

1. **Enumerate visible elements:** List the title text, axis labels, legend entries, annotations, and data encodings (bars, lines, points, etc.) you observe. Note anything expected but absent.
2. **Semantic fidelity:** Does the chart show what the user asked for? Does the title match the content? Are the correct columns/variables plotted?
3. **Data integrity:** Are axis ranges appropriate? Any truncated elements? Bar charts starting at zero? For ML evaluation charts, are reference lines (diagonal, baseline) present?
4. **Design Principles check** — verify the 6 principles that are assessable from a rendered image:
   - P1 (Show the data): Are actual data values visible, or hidden behind aggregation?
   - P3 (Position over color): Is the primary comparison encoded in position?
   - P6 (Annotate the insight): Is there at least one annotation that states a finding beyond axis labels?
   - P7 (Encode meaning twice): Are data series distinguishable by more than color alone?
   - P8 (Panel consistency): For multi-panel charts, are scales and styles consistent across panels?
   - P9 (No arithmetic): Can the reader extract values directly without mental subtraction?
5. **Layout and readability:** Text overlap or truncation? Excessive whitespace or cramped elements? Annotations positioned near the data they describe? For multi-panel grids: are gaps between subplots and between suptitle and panels proportional to the content? Reduce `wspace`/`hspace` or `tight_layout(pad=...)` if spacing looks excessive.
6. **Chart-type rules:** If the chart matches a pattern file that has a **Rules** section, verify the rendered output satisfies those rules.
7. **Name one improvement** you would make, even if minor. If nothing comes to mind, re-examine annotation placement, whitespace usage, and color distinguishability.

If any issue in items 2–6 requires a code change, fix the code and re-run → proceed to Stage C.

## Stage C — Visual Refinement (Round 2, only if Stage B required changes)

Read the updated PNG. Confirm:

1. All Stage B issues are resolved
2. No new issues were introduced by the fixes
3. Aesthetic elements remain consistent with `style-reference.md`

If all issues are resolved, stop. If new issues were introduced by the fixes, proceed to Stage D.

## Stage D — Final Polish (Round 3, only if Stage C found new issues)

Fix the issues identified in Stage C, re-run, and read the updated PNG. Confirm:

1. All Stage C issues are resolved
2. No new regressions were introduced
3. Chart meets `style-reference.md` standards

**If issues remain after Stage D:** do NOT iterate further. Report the remaining issues to the user and ask whether to regenerate from scratch or accept as-is.

## Final — Report & Handoff

1. **Publication render:** If user requested publication quality, set `dpi=300` and run one final time
2. **Report to the user:** what was generated, the file paths, and any observations about the output (including Stage B item 7 — the one improvement you identified)
3. **Ask if refinements are needed** (colors, sizing, annotations, layout adjustments)
