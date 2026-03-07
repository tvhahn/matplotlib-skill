# 00 -- Original Baseline

## What Changed
- Nothing -- this is the baseline from the original commit (`871261a`)

## Why
Captures the starting point before any improvements, for before/after comparison in the blog article.

## Prompt Used
See `../../scratch/test_original_patterns.py` (generated retroactively from `git show 871261a:claude/skills/matplotlib-chart/chart-patterns.md`)

## Observations
- Annotation text uses default black instead of dimgrey
- Title `loc="right"` on horizontal bar chart looks odd
- Rolling average line barely visible at `linewidth=0.5`
- Lollipop chart has y-tick labels hidden (`set_yticks([])`) so you can't see classifier names
- Heatmap uses overlay `ax.text(transform=ax.transAxes)` instead of `set_title` for panel labels
- ROC panel missing its legend entirely
- Pattern 3 legend has no frame (bare `ax.legend()`)
- Pattern 5 legend has `frameon=False` -- no visual containment
- Manual spine removal (`ax.spines[...].set_visible(False)`) is verbose and error-prone
- `plt.rcParams["axes.titlepad"]` is a global side-effect, not per-axes

## Before vs After
- **Before:** N/A (this is the baseline)
- **After:** See `../01-current/`

## Files Modified
None -- original state

## Lessons Learned
- Starting from real research code means inheriting accumulated quirks
- A baseline capture is essential for showing progress -- you can't measure improvement without it
- Even "working" code has consistency issues that only become visible when you lay all patterns side by side
