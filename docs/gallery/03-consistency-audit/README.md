# 03 -- Consistency Audit

## What Changed
- Pattern 3 (Time Series): Added missing `font="DejaVu Sans"` to `sns.set_theme()`
- Pattern 5 (Lollipop): Added missing `dpi=300` to `plt.subplots()`
- Pattern 6 (Decision Boundary): Changed `dpi=150` to `dpi=300`
- Pattern 8 (Multi-Panel Grid): Added missing `font="DejaVu Sans"` to `sns.set_theme()`
- Pattern 9 (PR/ROC): Added `font_scale=1.0, font="DejaVu Sans"`, removed non-standard `context="notebook"`, changed `dpi=150` to `dpi=300`

## Why
An expert panel review found that 5 of the 9 patterns had inconsistencies in their `sns.set_theme()` calls or `dpi=` values. These subtle differences meant charts generated from different patterns could look slightly different in font rendering and resolution.

## Prompt Used
See `../../scratch/test_chart_patterns.py` (updated to match pattern fixes)

## Observations
- Pattern 9 was the worst offender: missing font, non-standard context, and wrong DPI
- The font difference is subtle but visible when comparing time series (pattern 3) output before/after
- Pattern 5 lollipop chart now renders at proper resolution instead of matplotlib's default 100 DPI
- All `grep 'sns.set' chart-patterns.md` calls are now identical

## Before vs After
- **Before:** See `../02-dpi-optimization/`
- **After:** See PNGs in this folder

## Files Modified
- `chart-patterns.md`: 5 patterns fixed for consistent `sns.set_theme()` and `dpi=300`
- `test_chart_patterns.py`: Updated to match pattern fixes

## Lessons Learned
- Consistency bugs are invisible when you look at patterns one at a time -- you only find them by grepping across all patterns
- A simple `grep 'sns.set'` check is a powerful verification: if the lines aren't identical, something's wrong
- `context="notebook"` in seaborn quietly changes font sizes, which breaks consistency with other patterns
