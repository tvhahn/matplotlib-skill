# Time Series: Bars with Rolling Mean

**Use for:** periodic values (annual, monthly) shown as bars above/below a reference, with a smoothing trend line. For plain line charts over time use `other-charts.md`.
**Exemplars:** `exemplars/P3-a.png` (anomalies around zero) and `exemplars/P3-b.png` (all-positive series vs its mean). Fixed: red/blue bars around the named reference, cubehelix rolling line, Patch+Line2D legend. Varies: reference, annotated moment, subtitle.

```python
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data ---
df = pd.read_csv("data.csv").dropna(subset=["year", "value"])
rolling_df = df.dropna(subset=["rolling"])
pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

# Reference: 0 for anomaly/deviation data, the mean for all-positive data
reference = 0 if (df["value"] < 0).any() else df["value"].mean()
ref_label = "zero" if reference == 0 else f"the mean ({reference:,.1f})"

fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
bar_colors = ["#d73027" if v >= reference else "#4575b4" for v in df["value"]]
ax.bar(df["year"], df["value"], color=bar_colors, alpha=0.55, width=0.9, zorder=2)
ax.plot(rolling_df["year"], rolling_df["rolling"], color=pal[5], linewidth=2.5, zorder=4)
ax.axhline(y=reference, color="lightgrey", linewidth=0.8, zorder=1)

# --- Annotate the record at the data ---
rec = df.loc[df["value"].idxmax()]
ax.annotate(f'Record: {rec["value"]:+.2f} ({int(rec["year"])})',
            xy=(rec["year"], rec["value"]), xytext=(-12, 8), textcoords="offset points",
            ha="right", va="bottom", fontsize=10, color="dimgrey",
            arrowprops=dict(arrowstyle="-", color="dimgrey", lw=0.8))

ax.set_xlabel("Year", fontsize=12, labelpad=8, color="dimgrey")
ax.set_ylabel("Y-Axis Label (unit)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=26, color="dimgrey", weight="semibold")

# --- Takeaway subtitle: how the trend moved, computed from the rolling column ---
first, last = rolling_df.iloc[0], rolling_df.iloc[-1]
direction = "rose" if last["rolling"] > first["rolling"] else "fell"
recent = df.tail(10)
above = (recent["value"] >= reference).sum()
ax.annotate(f'The rolling mean {direction} from {first["rolling"]:,.2f} ({int(first["year"])}) '
            f'to {last["rolling"]:,.2f} ({int(last["year"])}); {above} of the last {len(recent)} '
            f'periods are above {ref_label}',
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")

legend_handles = [
    Patch(facecolor="#d73027", alpha=0.55, label=f"Above {ref_label}"),
    Patch(facecolor="#4575b4", alpha=0.55, label=f"Below {ref_label}"),
    Line2D([0], [0], color=pal[5], linewidth=2.5, label="10-year rolling mean"),
]
ax.legend(handles=legend_handles, loc="upper left", fontsize=10, frameon=True,
          facecolor="white", framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey")

ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.grid(False)
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- `ax.bar()` as the primary data layer, coloured `"#d73027"` at or above the reference and `"#4575b4"` below.
- Rolling-mean line in cubehelix `pal[5]`.
- Legend built from `Patch` + `Line2D` handles that name the reference and the rolling window.

**Guidance:**
- Use the pre-computed `rolling` column when the data has one; state its window in the legend (check the data or ask if unknown — don't guess).
- Name the baseline: "relative to 1951–1980 average", "zero", or "series mean". Readers can't interpret above/below without it.
- The subtitle states how the trend moved (from → to, computed). Annotate 1–2 moments at the data: the record, a turning point, a well-known event. Compute values from the data; don't repeat the subtitle's numbers.
- A centred rolling mean has no values at either end; say "centred" or "trailing" in the legend when you know which.
- Bar `alpha` 0.4 for many bars, 0.65 for few. Widen to `(14, 6)` for 50+ periods. Add markers to the rolling line when there are fewer than 10 points.
- Move the legend if it covers bars; with the record annotation top-right, top-left usually stays clear.
- Panel frame optional — add it when the rolling line floats well above the bars.
- **Predicted vs. actual variant:** true values as a `#4575b4` line (lw=1), predictions as grey points (`alpha=0.4, s=2`), rolling mean of predictions in `#d73027`, and a metric box (RMSE, R²) top-left — see style-reference Annotations.
