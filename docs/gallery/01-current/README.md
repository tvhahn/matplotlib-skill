# 01 -- Current (API Modernization + Visual Polish)

## What Changed
- **API modernization** (`f99598d`): `sns.set()` -> `sns.set_theme()`, `scale=` -> `density_norm=`, `df["col"][i]` -> `df["col"].iloc[i]`, added `hue=` + `legend=False` to barplots
- **Visual polish** (`e0d1726`): Added `color="dimgrey"` to all annotations, `frameon=True` with white background on legends, `pad=` kwarg instead of `plt.rcParams["axes.titlepad"]`, `sns.despine()` everywhere, `linewidth=1.5` on rolling avg, `set_title` on heatmap panels, ROC legend added

## Why
- API modernization prevents FutureWarning deprecations in seaborn >= 0.13 and pandas >= 2.1
- Visual polish enforces consistent aesthetic rules across all 9 patterns

## Prompt Used
See `../../scratch/test_chart_patterns.py`

## Observations
- Annotations now consistently dimgrey -- much cleaner than default black
- Framed legends (white background, light grey border) are more readable than frameon=False
- Lollipop chart now shows classifier names (removed `set_yticks([])`)
- Rolling average line is visible at `linewidth=1.5`
- Heatmap panel labels use `set_title` with bold prefix, matching all other patterns
- ROC panel now has its own legend

## Before vs After
- **Before:** See `../00-original/`
- **After:** See PNGs in this folder

## Files Modified
- `chart-patterns.md`: All 9 patterns updated for modern APIs and consistent styling

## Lessons Learned
- API deprecations in seaborn/pandas accumulate silently -- periodic audit catches them before they break
- Small visual details (dimgrey vs black, framed vs unframed legends) compound into a noticeably more polished aesthetic
- Using `sns.despine()` instead of manual spine removal reduces code and eliminates missed-spine bugs
