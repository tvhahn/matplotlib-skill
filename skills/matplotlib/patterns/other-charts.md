# Other Charts: Line, Scatter, Histogram, Grouped Bar

Use this file when no P1–P9 pattern fits. These charts get the same
style-reference invariants. Each section names its **Signature** (keep) and
**Guidance** (adapt to the data).

## Contents
- Line chart (multi-series over time)
- Scatter plot (two continuous variables)
- Histogram / distribution of one variable
- Grouped bar (two categorical variables)

## Line chart

**Exemplar:** `exemplars/other-line.png` — five stocks, cased lines, direct end labels (light hues darkened for text).

```python
import matplotlib

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

df = pd.read_csv("data.csv", parse_dates=["date"]).dropna(subset=["date", "value", "series"])
series = df.groupby("series")["value"].last().sort_values(ascending=False).index
pal = dict(zip(series, ["#d73027", "#4575b4", "#555555", "#fc8d59", "#91bfdb", "#1f253f"]))  # CATEGORICAL

fig, ax = plt.subplots(figsize=(11, 6), dpi=150)
for i, name in enumerate(series):  # white casing first, so crossings read as over/under
    s = df[df["series"] == name]
    ax.plot(s["date"], s["value"], color="white", linewidth=4.5, zorder=10 - i)
    ax.plot(s["date"], s["value"], color=pal[name], linewidth=2, zorder=10 - i)

# Direct labels at line ends instead of a legend, nudged apart so none collide
ends = df.sort_values("date").groupby("series").tail(1).set_index("series")
min_gap = (df["value"].max() - df["value"].min()) * 0.05
label_y = {}
for name, y in ends["value"].sort_values().items():
    prev = max(label_y.values(), default=-np.inf)
    label_y[name] = max(y, prev + min_gap)
def text_color(c):  # light hues (orange, light blue) are too faint as text: darken them
    r, g, b = matplotlib.colors.to_rgb(c)
    return (r * 0.7, g * 0.7, b * 0.7) if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.5 else c

for name, y in label_y.items():
    ax.annotate(name, xy=(ends.loc[name, "date"], y), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=10, color=text_color(pal[name]), weight="semibold")

ax.set_title("Chart Title", fontsize=14, loc="left", pad=26, color="dimgrey", weight="semibold")
# Takeaway subtitle: growth of the leader over the period, computed
first = df.sort_values("date").groupby("series")["value"].first()
growth = (ends["value"] / first).sort_values(ascending=False)
ax.annotate(f"{growth.index[0]} ended at {growth.iloc[0]:.1f}x its starting value; "
            f"{growth.index[-1]} at {growth.iloc[-1]:.1f}x",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")
ax.set_ylabel("Value (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.grid(axis="x", visible=False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
```

**Signature:** one line per series with a white casing underneath; direct labels at line ends rather than a legend when there are ≤ 6 series.

**Guidance:**
- Use lines, not bars, for continuous time. P3 is only for "bars + rolling mean" requests.
- Keep the horizontal gridlines (they help read values); drop vertical ones.
- Colours from `CATEGORICAL` in order; from the 4th series on, also vary `linestyle` so similar hues stay distinguishable. More than 6 series: grey all lines and highlight the 1–2 that matter (style-reference Craft), or switch to P8 small multiples.
- The subtitle states the comparison the reader came for (growth, a crossover, the gap at the end), computed from the data.
- The template nudges end labels apart; check that each label still reads as belonging to its line.
- Use a log y-axis when series differ by more than ~10× and the question is about growth.
- Annotate events or turning points with `ax.annotate(..., arrowprops=dict(arrowstyle="-", color="dimgrey", lw=0.8))`.

## Scatter plot

**Exemplar:** `exemplars/other-scatter.png` — three species, colour + marker shape, panel frame.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

df = pd.read_csv("data.csv").dropna(subset=["x", "y", "group"])
groups = df.groupby("group")["y"].median().sort_values(ascending=False).index
colors = ["#d73027", "#4575b4", "#555555", "#fc8d59", "#91bfdb", "#1f253f"]  # CATEGORICAL
markers = ["o", "s", "^", "D", "v", "P"]

fig, ax = plt.subplots(figsize=(10, 6.5), dpi=150)
for g, c, m in zip(groups, colors, markers):
    d = df[df["group"] == g]
    ax.scatter(d["x"], d["y"], s=40, color=c, marker=m, alpha=0.8,
               edgecolors="white", linewidths=0.5, label=g)

r = df["x"].corr(df["y"])
top = df.groupby("group")["y"].median()
ax.annotate(f"Correlation r = {r:.2f}; {top.idxmax()} has the highest median "
            f"({top.max():,.0f})",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")
ax.set_xlabel("X (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_ylabel("Y (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=26, color="dimgrey", weight="semibold")
ax.legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
          labelcolor="dimgrey", loc="lower right", title=None)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.patch.set_edgecolor("lightgrey")
ax.patch.set_linewidth(0.8)
sns.despine(left=True, bottom=True)
```

**Signature:** white-edged markers; colour *and* marker shape per group (encode meaning twice); panel frame.

**Guidance:**
- Log-scale an axis that spans orders of magnitude (income, population, prices) and say so in the label.
- Size encodes a third variable only when asked; then scale area (not radius) with the value and build the size legend with `legend_elements` (style-reference Craft).
- Lower `alpha` and `s` for > 500 points; for > 5,000 consider `ax.hexbin` or a 2-D histogram.
- Label a handful of notable points (outliers, the ones the question is about) with `ax.annotate` and a white halo; never label every point. If labels can't sit next to their points, use side callouts (Craft).
- Add a trend line only when the relationship is the point, and state what it is (e.g. "least-squares fit").

## Histogram

**Exemplar:** `exemplars/other-histogram.png` — skewed fares, median pinned to its line.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

values = pd.read_csv("data.csv")["value"].dropna()
pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
ax.hist(values, bins="auto", color=pal[3], edgecolor="white", linewidth=0.6)

med = values.median()
ax.axvline(med, color="dimgrey", linestyle="--", linewidth=1)
# x in data units, y in axes fraction: the label stays on its line whatever the limits
ax.text(med, 0.97, f"  Median {med:,.1f}", transform=ax.get_xaxis_transform(),
        ha="left", va="top", fontsize=10, color="dimgrey")

p90 = values.quantile(0.9)
ax.annotate(f"Half of values fall below {med:,.1f}; the top 10% exceed {p90:,.1f}",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")

ax.set_xlabel("Value (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_ylabel("Count", fontsize=12, labelpad=8, color="dimgrey")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=26, color="dimgrey", weight="semibold")
ax.grid(axis="x", visible=False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
```

**Signature:** single cubehelix fill with white bar edges; median (or mean) reference line, labelled.

**Guidance:**
- Choose bins for the data: `"auto"` to start; round-number bin edges (e.g. every $2) read better when units are familiar.
- Heavy right skew: clip the view at a high percentile and note the clipped tail, or log the x-axis.
- Comparing 2–3 groups: overlay with `alpha=0.5` and distinct colours, or use P4 for more groups.
- Annotate features that matter (a second mode, a spike at a fixed price), not just the summary statistic.

## Grouped bar

**Exemplar:** `exemplars/other-grouped.png` — survival by class and sex, gap stated in the subtitle.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

df = pd.read_csv("data.csv").dropna(subset=["group", "subgroup", "value"])
summary = df.groupby(["group", "subgroup"], as_index=False)["value"].mean()

fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
n_sub = summary["subgroup"].nunique()
sns.barplot(data=summary, x="group", y="value", hue="subgroup",
            palette=["#d73027", "#4575b4", "#555555", "#fc8d59"][:n_sub],  # CATEGORICAL
            ax=ax, edgecolor="white")
for container in ax.containers:
    ax.bar_label(container, fmt="{:.0%}", padding=3, fontsize=10, color="dimgrey",
                 weight="semibold")

ax.set_title("Chart Title", fontsize=14, loc="left", pad=26, color="dimgrey", weight="semibold")
wide = summary.pivot(index="group", columns="subgroup", values="value")
gap = (wide.max(axis=1) - wide.min(axis=1)).sort_values(ascending=False)
ax.annotate(f"The widest gap between subgroups is in {gap.index[0]} ({gap.iloc[0]:.0%} points)",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")
ax.set_xlabel("")
ax.set_ylabel("Value (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
          labelcolor="dimgrey", title=None)
ax.set_yticks([])
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
```

**Signature:** bar-end value labels via `ax.bar_label` with hidden value axis (as in P1); ≤ 4 subgroup hues from `CATEGORICAL`, in order.

**Guidance:**
- Put the comparison the reader cares most about *within* each group (adjacent bars).
- More than 4 subgroups or 8 groups: use small multiples (P8) or a heatmap (P7) instead.
- Order groups meaningfully (a natural order such as small-medium-large, or by value).
- Match the label and subtitle formats to the data (`{:.0%}` for rates stored as 0–1, `{:,.0f}` for counts).
