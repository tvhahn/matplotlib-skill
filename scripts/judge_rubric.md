# Chart Judge Rubric

Used by vision-capable judge agents to score benchmark outputs from
`scripts/benchmark.py`. Each run directory holds `meta.json` (prompt, `checks`,
model) and one or more PNGs. Judge the PNG(s) against the prompt; open the
generated `.py` in `workspace/` only to confirm a suspected data error.

The target aesthetic is clean and despined: whitegrid base, DejaVu Sans, muted
dimgrey text, ColorBrewer/cubehelix palettes, annotation-rich but uncluttered.
Score what a demanding data-visualisation editor would score: would this go into
a paper or report as-is?

## Scores (integers)

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **correct** — numbers and facts match `checks`; nothing silently dropped | wrong values / wrong data | partly wrong or ambiguous | right, minor slip (e.g. unclear units) | fully right |
| **fit** — chart type and encoding suit the request and data | wrong chart type (e.g. bars for a requested line chart) | workable but awkward | good | ideal choice, incl. smart touches (log scale, sorted order, direct labels) |
| **legible** — nothing overlaps, clips, or crowds; text readable at 100% | serious overlap/clipping | noticeable crowding | minor nit | clean |
| **insight** — annotations/title help the reader see the point | none, or misleading | generic/trivial (e.g. "X leads at 23.9" restating a bar label) or detached in a corner footer | useful | sharp, placed at the data it describes |
| **polish** — coherent palette, whitespace, hierarchy, despined, consistent style | default-looking or garish | some rough edges | publishable | outstanding |

Also give **overall** (1–10) and a list of **defects**: concrete, visible
problems, each under 15 words (e.g. "legend covers 2008 data", "footer text
collides with x tick labels", "8-cylinder bar shows 80 hp, expected ~158").

## Output

Return a JSON list, one object per run:

```json
{"run": "<model>/<case>", "correct": 3, "fit": 2, "legible": 3, "insight": 1,
 "polish": 2, "overall": 7, "defects": ["..."], "note": "one sentence"}
```

If a run produced no PNG, score every dimension 0, overall 0, defect "no chart".

## Pairwise mode

When asked to compare two versions of the same run (A vs B, order randomised),
answer `{"run": ..., "winner": "A"|"B"|"tie", "margin": "slight"|"clear"|"large",
"why": "one sentence"}`. Judge the chart, not the effort.
