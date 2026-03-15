# Autoresearch Program

Human-authored research priorities. Read by the agent each iteration.
Last updated: 2026-03-14.

## Current Priorities

1. **P4 (PR/ROC)** — k-fold convergence, panel layout consistency
2. **P8 (Multi-panel)** — shared y-axis, color consistency, subplot spacing
3. **P9 (Decision boundary)** — diverging colormap, legend placement
4. **P1 (Horizontal bar)** — annotation format, Blues_d palette adherence
5. **P5 (Lollipop)** — legend positioning, stem/marker sizing
6. **P6 (Vertical bar)** — palette slice order, annotation format
7. **P3 (Time series)** — rolling window styling, annotation placement
8. **P2 (Violin)** — strip overlay consistency
9. **P7 (Heatmap)** — annotation font size, diverging palette usage

## Constraints

- **Immutable files:** `style-reference.md` (start conservative — loosen later if needed)
- **Immutable style calls:** `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")` and `sns.despine(left=True, bottom=True)` — never modify
- **No pattern deletions** — add/modify only
- **Single file scope:** only the target `patterns/PN-*.md` file is modified per experiment

## Success Criteria

- **Minimum composite threshold:** 0.60 (compliance × convergence × visual × refinement)
- **Target:** all 9 patterns above 0.60; stretch goal 0.80
- **Compliance must be 1.0** — fix compliance failures before optimizing other layers
- **Note:** Threshold lowered from 0.85 to 0.60 to account for the harder 4-layer scoring (graded visual rubric + refinement layer). A "good" pattern typically scores ~0.45–0.55 under the new system.

## Exploration Strategies

When improving a pattern, try these approaches in order:
1. **Rule tightening** — add explicit "do/don't" rules to reduce ambiguity on *structural* dimensions (API, palette family, despine). Avoid tightening *adaptive* dimensions (figsize, legend position, annotation format).
2. **Code simplification** — fewer lines = less room for divergence
3. **Parameter pinning** — replace vague descriptions with exact values (fontsize=14, alpha=0.5). Use "default" language — not "do not change" — to allow data-driven adaptation.
4. **Palette refinement** — ensure palette name + slice indices are explicit
5. **Layout constraints** — pin figsize, wspace, hspace as *defaults* with guidance on when to scale
6. **Annotation templates** — provide exact f-string format for data labels
7. **Rule softening** — change "do not change X" to "default X; adapt if data requires". Use when a rigid rule causes convergence on test data but would fail on novel data (e.g., fixed figsize that truncates labels on wider datasets).
8. **Informativeness preservation** — never remove annotations, axis labels, or contextual elements solely to improve convergence. If runs disagree on whether to include a label, the fix is to mandate inclusion (not ban it). A chart that's consistently uninformative is worse than one that's inconsistently informative.

## When Stuck

- Re-read the discard history for this pattern in `results.tsv` — avoid repeating failed approaches
- Try a fundamentally different strategy (e.g., if rule tightening isn't working, try code simplification)
- Skip to the next-lowest pattern and return later with fresh context
- If 10+ consecutive discards: the pattern may need a full rewrite via `/variation-analysis`, not incremental fixes
