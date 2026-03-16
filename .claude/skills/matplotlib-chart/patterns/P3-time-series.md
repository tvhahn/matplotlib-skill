# Time Series with Rolling Average

**When to use:** Time series visualization with annual/periodic aggregation and smoothing trend line. Also suitable for predicted vs actual (see Customize).
**Palette:** `#4575b4` (blue) for negative/below-average values, `#d73027` (red) for positive/above-average values. Rolling line: cubehelix `pal[5]`.
**API:** Always use `ax.bar()` for the main data — bars are this pattern's signature.

```python
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data ---
df = pd.read_csv("data.csv")
rolling_df = df.dropna(subset=["rolling"])

# --- Palette (red/blue bars + cubehelix rolling line) ---
pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

fig, ax = plt.subplots(figsize=(12, 6), dpi=150)

# Reference: use 0 for anomaly/deviation data, mean for all-positive data
reference = 0 if (df["value"] < 0).any() else df["value"].mean()

# Colored bars: #d73027 red for ≥ reference, #4575b4 blue for < reference
bar_colors = ["#d73027" if v >= reference else "#4575b4" for v in df["value"]]
ax.bar(df["year"], df["value"],
       color=bar_colors, alpha=0.55, width=0.9, zorder=2)

# Rolling mean trend line — always pal[5], no markers
ax.plot(rolling_df["year"], rolling_df["rolling"],
        color=pal[5], linewidth=2.5, zorder=4)

# Reference baseline (at 0 for deviation data, at mean for all-positive)
ax.axhline(y=reference, color="lightgrey", linewidth=0.8, zorder=1)

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

**Rules (identity):**
- Use `ax.bar()` as the primary data layer — not `ax.scatter()`, `fill_between`, or line-only variants.
- Bar colors are `"#d73027"` (red) for values ≥ reference and `"#4575b4"` (blue) for values < reference. Do not substitute or invert. Even if all values are positive, compute the series mean and color above/below it.
- Rolling mean line uses `pal[5]` from `sns.cubehelix_palette(6, rot=-0.25, light=0.7)` — do not hardcode `"navy"`, `"black"`, or other colors. Use a plain `ax.plot()` — no markers or glow effects.
- Exactly 3 legend items using custom Patch + Line2D handles. Adapt labels to data domain (e.g., "Above baseline" for anomaly data).
- Reference value: use `0` when data has negative values; otherwise use `df["value"].mean()`. The template code shows the conditional: `reference = 0 if (df["value"] < 0).any() else df["value"].mean()`.
- When the data provides a pre-computed `rolling` column, use it directly — do not recompute.
- Filter NaN from rolling column before plotting: `rolling_df = df.dropna(subset=["rolling"])`.
- Always use `dpi=150`. Save PDF+PNG with `bbox_inches="tight"`.

**Adapt when:**
- Adjust bar `alpha` for data density: lower (0.4) for many bars, higher (0.65) for few.
- Scale `figsize` wider for long time ranges (e.g., `(14, 6)` for 50+ years).
- Move legend to another corner if `"upper left"` occludes data.
- Add data point annotations if the user requests them.

**Customize:** Adjust rolling window size (default 10). For predicted-vs-actual, replace bars with `ax.plot()` for true values (`#4575b4`, linewidth=1) and `ax.scatter()` for predictions (grey, alpha=0.4, s=2), compute rolling on predictions via `pd.rolling()`, and add RMSE/R² annotation box. Use `ax.annotate()` with `arrowprops=dict(arrowstyle="-", color="dimgrey", lw=0.8)` for notable data points.
