# Autoresearch v2: Subagent Architecture + Harder Scoring

Date: 2026-03-21

## Why This Exists

After 16 experiments across 9 patterns, the autoresearch scoring system has two structural problems that prevent productive long-running optimization:

1. **Context window exhaustion** — Each iteration reads 3 PNG images (~10,500 tokens), filling the context window after ~8 iterations per pattern.
2. **Score over-saturation** — 7 of 9 patterns score >= 0.95 composite at baseline. Refinement and adaptiveness are 1.0 in 85% of rows. The effective scoring range is 5 points wide (0.95–1.00).

### Evidence from `results.tsv`

| Metric | Min | Median | Max | Rows at 1.0 |
|--------|-----|--------|-----|-------------|
| Compliance | 1.0 | 1.0 | 1.0 | 26/26 (100%) |
| Visual | 0.819 | 0.958 | 1.0 | 2/26 (8%) |
| Refinement | 0.8 | 1.0 | 1.0 | 22/26 (85%) |
| Adaptiveness | 0.6 | 1.0 | 1.0 | 22/26 (85%) |
| **Composite** | **0.767** | **0.979** | **1.0** | **1/26 (4%)** |

P9 scored a perfect 1.000 at baseline, before any optimization. This means the scoring system cannot distinguish between "good" and "excellent."

## What Changes

### Part A: Subagent Delegation
Evaluation (reading PNGs, applying rubrics) is delegated to Agent subagents. The orchestrator only sees compact JSON scores. This reduces per-iteration context cost from ~13,600 to ~1,100 tokens (12x reduction), enabling 100+ iterations.

### Part B: Scoring Overhaul
- **Visual rubric restructured**: 5 template-compliance checks moved to automated `evaluate_skill.py`; 4 deliberately hard "design excellence" checks added
- **Refinement & adaptiveness graduated**: Binary (0/1) → graded (0/1/2/3) scales with anchored criteria
- **Worst-of-3 floor**: Prevents one bad chart from being averaged away by two good ones
- **Annotation-positive scoring**: Missing annotations score 0 (not neutral), making annotation attempts positive expected value
- **Steeper signature penalty**: Quadratic (not linear), kicks in at 4 items (not 5)
- **Diminishing returns brake**: Patterns above 0.90 are frozen
- **Prompt holdout set**: 70/30 train/holdout split detects rubric overfitting

Expected baseline composite shifts from 0.90–1.00 to 0.50–0.75, providing 25–50 points of optimization headroom.

## Files in This Spec

- [`expert-panel-analysis.md`](expert-panel-analysis.md) — 5-panelist deep critique of the current scoring methodology
- [`scoring-v2-spec.md`](scoring-v2-spec.md) — Technical specification for the new scoring system

## Implementation Target

- `.claude/commands/autoresearch.md` — all changes applied to this single file
