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
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7, color="dimgrey")

# Legend with Patch handles for bar colors + Line2D for rolling
legend_handles = [
    Patch(facecolor="#d73027", alpha=0.55, label="Above average"),
    Patch(facecolor="#4575b4", alpha=0.55, label="Below average"),
    Line2D([0], [0], color=pal[5], linewidth=2.5, label="Rolling mean"),
]
ax.legend(handles=legend_handles, loc="upper left", fontsize=10,
         frameon=True, facecolor="white", framealpha=0.8,
         edgecolor="lightgrey", labelcolor="dimgrey")

# --- Insight annotation (change over time from data) ---
first_year, last_year = int(df["year"].min()), int(df["year"].max())
change = df["value"].iloc[-1] - df["value"].iloc[0]
ax.text(0.98, 0.98, f"Change: {change:+.1f} from {first_year} to {last_year}",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=9, color="dimgrey", style="italic")

ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.grid(False)
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Use `ax.bar()` as the primary data layer.
- Bar colors: `"#d73027"` (red) for values ≥ reference, `"#4575b4"` (blue) for values < reference.
- Rolling mean line uses cubehelix `pal[5]`.
- Legend with custom Patch + Line2D handles. Adapt labels to data domain.

**Guidance:**
- Always read data from the CSV file using `pd.read_csv()` — never hardcode data values inline. The pre-computed CSV has columns `year`, `value`, `rolling`.
- Use classical titles that describe the metric (e.g., "Global Temperature Anomalies, 1880–2023"). Insight annotations carry findings, not the title.
- Default rolling line style: plain `ax.plot()`. Add markers if data is sparse (<10 points) to clarify individual values.
- Default rolling line color is `pal[5]` (darkest cubehelix). Any dark cubehelix shade works if the darkest conflicts with the data.
- Reference value: use `0` when data has negative values; otherwise use `df["value"].mean()`. The template code shows the conditional.
- Bar colors must be exactly `"#d73027"` (red) and `"#4575b4"` (blue) — do not substitute other shades (e.g., steel blue, coral). These hex codes are the pattern's visual identity.
- When the data provides a pre-computed `rolling` column, use it directly — do not recompute.
- Adjust bar `alpha` for data density: lower (0.4) for many bars, higher (0.65) for few.
- Scale `figsize` wider for long time ranges (e.g., `(14, 6)` for 50+ years).
- Move legend to another corner if `"upper left"` occludes data.
- Add data point annotations if the user requests them or an insight warrants emphasis.
- **Panel frame:** Optional. Consider adding a panel frame (`ax.patch.set_edgecolor("lightgrey")`, `ax.patch.set_linewidth(0.8)`) when the rolling mean line floats far above the bar tops, creating a visual gap between data and chart boundary. Omit when bars fill most of the vertical space.

**Customize:** Adjust rolling window size (default 10). For predicted-vs-actual, replace bars with `ax.plot()` for true values (`#4575b4`, linewidth=1) and `ax.scatter()` for predictions (grey, alpha=0.4, s=2), compute rolling on predictions via `pd.rolling()`, and add RMSE/R² annotation box. Use `ax.annotate()` with `arrowprops=dict(arrowstyle="-", color="dimgrey", lw=0.8)` for notable data points.
