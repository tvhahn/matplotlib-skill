# Autoresearch Program

Human-authored research priorities. Read by the agent each iteration.
Last updated: 2026-03-21.

## Current Priorities

1. **Validate restructured patterns** — baseline all 9 patterns with new Signature/Guidance structure
2. **Adaptiveness gaps** — patterns scoring low on the new adaptiveness dimension
3. **Visual quality** — patterns below 0.80 visual score
4. **Guidance clarity** — templates with ambiguous defaults that cause harmful divergence

## Constraints

- **Immutable:** `style-reference.md` Invariants section, `SKILL.md` Design Philosophy
- **Immutable style calls:** `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")` and `sns.despine(left=True, bottom=True)` — never modify
- **No pattern deletions** — add/modify only
- **Single file scope:** only the target `patterns/PN-*.md` file is modified per experiment
- **Signature items:** max 4 per pattern (enforced by signature_penalty)

## Success Criteria

- **Minimum composite threshold:** 0.60 (compliance × weighted layers × signature_penalty)
- **Target:** all 9 patterns above 0.60; stretch goal 0.80
- **Diminishing returns:** patterns above 0.90 are frozen — skip to next-lowest
- **Compliance must be 1.0** — fix compliance failures before optimizing other layers
- **Note (v2 scoring):** Scoring overhauled 2026-03-21. Visual rubric restructured (10 checks, 4 deliberately hard), refinement/adaptiveness graduated to 0/1/2/3 scales, worst-of-3 floor, quadratic signature penalty. Expected baseline: 0.50–0.75 (v1 baselines were 0.90–1.00 due to ceiling effects). See `docs/specs/autoresearch-v2/` for rationale. Old results.tsv rows are v1 scores — re-baseline before comparing.

## Exploration Strategies

When improving a pattern, try these approaches in order:
1. **Simplification** — remove Signature items that restate invariants or template code. Fewer items → better signature_penalty → higher composite. The simplest specification that achieves quality is preferred.
2. **Guidance tuning** — clarify Guidance defaults with "default X; consider Y when Z" language. Good guidance enables adaptiveness without over-constraining.
3. **Template alignment** — ensure template code matches Signature claims. Inconsistencies between template and Signature are the highest-leverage fixes.
4. **Parameter defaults** — replace vague descriptions with sensible defaults. Use "default" language to allow data-driven adaptation. Avoid mandating exact values in rules.
5. **Palette refinement** — ensure palette name + slice indices are explicit
6. **Annotation guidance** — encourage data-specific annotations (Design Philosophy P6). Never remove annotations solely to improve scores.

## When Stuck

- Re-read the discard history for this pattern in `results.tsv` — avoid repeating failed approaches
- Try a fundamentally different strategy (e.g., if guidance tuning isn't working, try simplification)
- Skip to the next-lowest pattern and return later with fresh context
- If 10+ consecutive discards: the pattern may need a full rewrite via `/variation-analysis`, not incremental fixes
