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

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

df = pd.read_csv("data.csv", parse_dates=["date"]).dropna(subset=["date", "value", "series"])
series = df.groupby("series")["value"].last().sort_values(ascending=False).index
pal = dict(zip(series, ["#d73027", "#4575b4", "#555555", "#fc8d59", "#91bfdb", "#1f253f"]))  # CATEGORICAL

fig, ax = plt.subplots(figsize=(11, 6), dpi=150)
for name in series:
    s = df[df["series"] == name]
    ax.plot(s["date"], s["value"], color=pal[name], linewidth=2)

# Direct labels at line ends instead of a legend, nudged apart so none collide
ends = df.sort_values("date").groupby("series").tail(1).set_index("series")
min_gap = (df["value"].max() - df["value"].min()) * 0.05
label_y = {}
for name, y in ends["value"].sort_values().items():
    prev = max(label_y.values(), default=-np.inf)
    label_y[name] = max(y, prev + min_gap)
for name, y in label_y.items():
    ax.annotate(name, xy=(ends.loc[name, "date"], y), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=10, color=pal[name], weight="semibold")

ax.set_title("Chart Title", fontsize=14, loc="left", pad=7, color="dimgrey")
ax.set_ylabel("Value (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.grid(axis="x", visible=False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
```

**Signature:** one line per series; direct labels at line ends rather than a legend when there are ≤ 6 series.

**Guidance:**
- Use lines, not bars, for continuous time. P3 is only for "bars + rolling mean" requests.
- Keep the horizontal gridlines (they help read values); drop vertical ones.
- Colours from `CATEGORICAL` in order; from the 4th series on, also vary `linestyle` so similar hues stay distinguishable. More than 6 series: grey all lines and highlight the 1–2 that matter, or switch to P8 small multiples.
- The template nudges end labels apart; check that each label still reads as belonging to its line.
- Use a log y-axis when series differ by more than ~10× and the question is about growth.
- Annotate events or turning points with `ax.annotate(..., arrowprops=dict(arrowstyle="-", color="dimgrey", lw=0.8))`.

## Scatter plot

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

ax.set_xlabel("X (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_ylabel("Y (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7, color="dimgrey")
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
- Size encodes a third variable only when asked; add a size legend if you do.
- Lower `alpha` and `s` for > 500 points; for > 5,000 consider `ax.hexbin` or a 2-D histogram.
- Label a handful of notable points (outliers, the ones the question is about) with `ax.annotate`; never label every point.
- Add a trend line only when the relationship is the point, and state what it is (e.g. "least-squares fit").

## Histogram

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

values = pd.read_csv("data.csv")["value"].dropna()
pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
ax.hist(values, bins="auto", color=pal[3], edgecolor="white", linewidth=0.6)

med = values.median()
ax.axvline(med, color="dimgrey", linestyle="--", linewidth=1)
ax.annotate(f"Median {med:,.1f}", xy=(med, ax.get_ylim()[1] * 0.95), xytext=(6, 0),
            textcoords="offset points", ha="left", va="top", fontsize=10, color="dimgrey")

ax.set_xlabel("Value (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_ylabel("Count", fontsize=12, labelpad=8, color="dimgrey")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7, color="dimgrey")
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

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

df = pd.read_csv("data.csv").dropna(subset=["group", "subgroup", "value"])
summary = df.groupby(["group", "subgroup"], as_index=False)["value"].mean()

fig, ax = plt.subplots(figsize=(9, 6), dpi=150)
sns.barplot(data=summary, x="group", y="value", hue="subgroup",
            palette=["#d73027", "#4575b4"], ax=ax, edgecolor="white")
for container in ax.containers:
    ax.bar_label(container, fmt="{:.0%}", padding=3, fontsize=10, color="dimgrey",
                 weight="semibold")

ax.set_title("Chart Title", fontsize=14, loc="left", pad=7, color="dimgrey")
ax.set_xlabel("")
ax.set_ylabel("Value (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
          labelcolor="dimgrey", title=None)
ax.set_yticks([])
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
```

**Signature:** bar-end value labels via `ax.bar_label` with hidden value axis (as in P1); ≤ 4 hues from `DIVERGING_COLORBLIND`.

**Guidance:**
- Put the comparison the reader cares most about *within* each group (adjacent bars).
- More than 4 subgroups or 8 groups: use small multiples (P8) or a heatmap (P7) instead.
- Order groups meaningfully (a natural order such as small-medium-large, or by value).
