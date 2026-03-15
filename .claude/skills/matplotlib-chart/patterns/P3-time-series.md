# Time Series with Rolling Average

**When to use:** Time series visualization with annual/periodic aggregation and smoothing trend line. Also suitable for predicted vs actual (see Customize).
**Palette:** `#4575b4` (blue) for negative/below-average values, `#d73027` (red) for positive/above-average values. Rolling line: cubehelix `pal[5]`.
**Figsize:** `(12, 6)` for single-panel time series.
**API:** Always use `ax.bar()` for the main data — never use `ax.scatter()`, `fill_between`, colorbars, or line-only variants for the primary layer.
**Annotations:** Do not add data point annotations unless the user explicitly requests them.
**Legend:** Exactly 3 items: above-average Patch, below-average Patch, rolling mean Line2D. Do not add extra entries for the zero baseline.

```python
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

fig, ax = plt.subplots(figsize=(12, 6), dpi=150)

# Colored bars: positive vs negative
bar_colors = ["#d73027" if v >= 0 else "#4575b4" for v in df_annual["value"]]
ax.bar(df_annual["year"], df_annual["value"],
       color=bar_colors, alpha=0.55, width=0.9, zorder=2)

# Rolling mean trend line
ax.plot(df_annual["year"], df_annual["rolling"],
        color=pal[5], linewidth=2.5, label="Rolling mean", zorder=4)

# Zero baseline
ax.axhline(y=0, color="lightgrey", linewidth=0.8, zorder=1)

ax.set_xlabel("Year", fontsize=12, labelpad=8, color="dimgrey")
ax.set_ylabel("Y-Axis Label (Unit)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7)

# Legend with Patch handles for bar colors + Line2D for rolling
legend_handles = [
    Patch(facecolor="#d73027", alpha=0.55, label="Above average"),
    Patch(facecolor="#4575b4", alpha=0.55, label="Below average"),
    Line2D([0], [0], color=pal[5], linewidth=2.5, label="Rolling mean"),
]
ax.legend(handles=legend_handles, loc="upper left", fontsize=10,
         frameon=True, facecolor="white", framealpha=0.8,
         edgecolor="lightgrey", labelcolor="dimgrey")

ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.grid(False)
sns.despine(left=True, bottom=True)
```

**Rules:**
1. Always use `ax.bar()` as the primary data layer — never use `ax.plot()`, `ax.scatter()`, or `fill_between` for the main data. Bars are the pattern's signature.
2. Color bars relative to a reference value (mean of the series): `"#d73027"` for values ≥ reference, `"#4575b4"` for values < reference. Even if all values are positive (e.g., passenger counts), compute the series mean and color above/below it.
3. Rolling mean line must use `pal[5]` from `sns.cubehelix_palette(6, rot=-0.25, light=0.7)` — never hardcode a color like `"navy"` or `"black"`.
4. `figsize=(12, 6)` — do not change to (10, 6) or other sizes.
5. Exactly 3 legend items using custom handles: `Patch(facecolor="#d73027", alpha=0.55)`, `Patch(facecolor="#4575b4", alpha=0.55)`, `Line2D([0], [0], color=pal[5], linewidth=2.5)`. Do not use `ax.plot(..., label=...)` — build handles explicitly. Labels: `"Above average"`, `"Below average"`, `"Rolling mean"`.
6. Legend: `loc="upper left"`, `fontsize=10`, standard frame styling. Do not move to other positions.
7. Reference value: always compute `reference = df["value"].mean()`. Use for bar coloring (Rule 2) and baseline: `ax.axhline(y=reference, color="lightgrey", linewidth=0.8, zorder=1)`. No special cases — always use the mean.
8. Bar styling: `alpha=0.55`, `width=0.9`, `zorder=2` — do not vary these.
9. Do not add `ax.annotate()` arrows or data point labels unless the user explicitly requests them.
10. When the data provides a pre-computed `rolling` column, use it directly — do not recompute rolling with `pd.Series.rolling()`.
11. Title: `fontsize=14`, `loc="left"`, `pad=7` — do not change these values.

**Customize:** Adjust rolling window size (default 10). For predicted-vs-actual, replace bars with `ax.plot()` for true values (`#4575b4`, linewidth=1) and `ax.scatter()` for predictions (grey, alpha=0.4, s=2), compute rolling on predictions via `pd.rolling()`, and add RMSE/R² annotation box. Use `ax.annotate()` with `arrowprops=dict(arrowstyle="-", color="dimgrey", lw=0.8)` for notable data points.
