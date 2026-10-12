# Distributions: ECDF / Ridgeline

**Use for:** comparing whole distributions. ECDF for 2–4 groups when the reader asks
"what share is below x?" or the tails matter; ridgeline for many *ordered* groups
(months, years, ranks). A few groups with raw points → P4; one variable → histogram
(other-charts.md).
**Exemplars:** `exemplars/P12-ecdf.png` (2 groups, medians marked) and `exemplars/P12-ridgeline.png` (12 months in calendar order, the peak row highlighted). Fixed: ECDF colour + line style + direct labels; ridgeline white outlines, lower rows in front. Varies: guide lines, highlighted row, x clipping.

## Contents
- ECDF (2–4 groups)
- Ridgeline (many ordered groups)

## ECDF

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker

# --- Data: one row per observation; adapt the column names ---
df = pd.read_csv("data.csv").dropna(subset=["group", "value"])
med = df.groupby("group")["value"].median().sort_values(ascending=False)
groups = med.index  # highest median first = rightmost curve
COLORS = ["#d73027", "#4575b4", "#555555", "#fc8d59"]  # CATEGORICAL
STYLES, MARKERS = ["-", "--", ":", "-."], ["o", "s", "^", "D"]  # second encoding

fmt = ".2f" if med.max() < 10 else ".1f" if med.max() < 100 else ",.0f"
HALO = [pe.withStroke(linewidth=3, foreground="white")]
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
xlo, xmax = df["value"].min(), df["value"].quantile(0.99)  # cut the long tail; say so in the label
for i, (g, c, ls, mk) in enumerate(zip(groups, COLORS, STYLES, MARKERS)):
    v = df.loc[df["group"] == g, "value"]
    ax.ecdf(v, color=c, linestyle=ls, linewidth=2, zorder=3)
    ax.scatter([med[g]], [0.5], s=45, color=c, marker=mk, edgecolors="white", zorder=4)
    # Direct label with the median: rightmost curve below-right, the others above-left
    q, dx, ha = (0.3, 10, "left") if i == 0 else (0.85 - 0.2 * (len(groups) - 1 - i), -4, "right")
    x = v.quantile(q) if i == 0 else max(v.quantile(q), xlo + 0.3 * (xmax - xlo))  # room on the left
    t = ax.annotate(f"{g}  (median {med[g]:{fmt}})", xy=(x, (v <= x).mean()), xytext=(dx, 0 if i == 0 else 4),
                    textcoords="offset points", ha=ha, va="center" if i == 0 else "bottom",
                    fontsize=11, color=c,
                    weight="semibold")
    t.set_path_effects(HALO)  # middle curves have no empty side

# Median guide, named once at the right end where the curves have reached ~100%
ax.axhline(0.5, color="dimgrey", linestyle=(0, (2, 3)), linewidth=0.8, zorder=2)
ax.text(0.99, 0.5, "median", transform=ax.get_yaxis_transform(), ha="right", va="bottom",
        fontsize=10, color="dimgrey")

ax.set_xlim(xlo, xmax)
ax.set_ylim(0, 1.02)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
ax.set_xlabel("Value (units; axis cut at the 99th percentile)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_ylabel("Share at or below value", fontsize=12, labelpad=8, color="dimgrey")
ax.grid(axis="x", visible=False)

# --- Title + takeaway subtitle (computed) ---
hi, lo = groups[0], groups[-1]
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold", pad=26)
p90 = df.groupby("group")["value"].quantile(0.9)
ax.annotate(f"Half of {hi} values exceed {med[hi]:{fmt}}, against {med[lo]:{fmt}} for {lo}; "
            f"90th percentiles {p90[hi]:{fmt}} vs {p90[lo]:{fmt}}",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.patch.set_edgecolor("lightgrey")
ax.patch.set_linewidth(0.8)
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Step lines in `CATEGORICAL` colours *and* distinct linestyles, labelled directly (no legend).
- Dashed guide at 50% with each group's median marked on its curve and given in its label.

**Guidance:**
- 2–4 groups. More → ridgeline below, or P4.
- Heavy right tail: cut the x-axis at a high percentile and say so in the label, or use a log x-axis (`ax.set_xscale("log")`, drop zeros first and say how many).
- Read the subtitle off the curves: a median gap, a share above a threshold ("38% of card trips exceed 3 mi, 21% of cash trips"), or where the curves cross.
- Labels carry a white halo because middle curves (3–4 groups) have no empty side; check each still reads as its own curve.
- Add a vertical reference (a target, an SLA) with a label pinned by `ax.get_xaxis_transform()`.

## Ridgeline

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
# --- Data: one row per observation; adapt the column names ---
df = pd.read_csv("data.csv").dropna(subset=["group", "value"])
order = list(df["group"].drop_duplicates())  # natural order (months, years) — never alphabetical
n = len(order)
med = df.groupby("group")["value"].median()
focus, low = med.idxmax(), med.idxmin()

# Gaussian KDE with Scott's bandwidth, in numpy (no scipy needed)
v_all = df["value"].to_numpy(float)
grid = np.linspace(v_all.min() - v_all.std() * 0.3, v_all.max() + v_all.std() * 0.3, 400)
def kde(v):
    h = v.std(ddof=1) * len(v) ** (-1 / 5)
    z = (grid[:, None] - v[None, :]) / h
    return np.exp(-0.5 * z**2).sum(axis=1) / (len(v) * h * np.sqrt(2 * np.pi))
dens = {g: kde(df.loc[df["group"] == g, "value"].to_numpy(float)) for g in order}
scale = 1.5 / max(d.max() for d in dens.values())  # tallest ridge spans 1.5 rows

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)
fig, ax = plt.subplots(figsize=(9, 0.5 * n + 2), dpi=150)
for i, g in enumerate(order):
    base, z = n - 1 - i, 2 * i + 2  # first group on top; lower rows drawn in front
    top = base + dens[g] * scale
    ax.fill_between(grid, base, top, color=pal[5] if g == focus else pal[1], lw=0, zorder=z)
    ax.plot(grid, top, color="white", lw=1.2, zorder=z + 1)
    ax.vlines(med[g], base, base + np.interp(med[g], grid, dens[g]) * scale,
              color="white", lw=1.5, zorder=z + 1)  # median tick

# The focus row's median, in white inside its dark ridge beside the median tick
b = n - 1 - order.index(focus)
ax.annotate(f"{med[focus]:.1f}", xy=(med[focus], b + 0.45), xytext=(-5, 0),
            textcoords="offset points", ha="right", va="center", fontsize=10.5,
            color="white", weight="semibold", zorder=2 * n + 4)

ax.set_yticks(range(n), order[::-1], fontsize=11)
ax.set_ylim(-0.15, n - 1 + 1.6)
ax.set_xlim(grid.min(), grid.max())
ax.set_xlabel("Value (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.grid(axis="y", visible=False)

# --- Title + takeaway subtitle (computed) ---
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold", pad=26)
ax.annotate(f"Medians run from {med[low]:.1f} in {low} to {med[focus]:.1f} in {focus}",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Overlapping filled KDE rows with a white outline, lower rows in front (zorder rises down the stack), group names as y tick labels at each baseline.
- One shared x-axis; a white median tick inside every ridge.

**Guidance:**
- Groups need a natural order; keep it (calendar months, years ascending top to bottom). Unordered groups → ECDF or P4.
- Colour: one cubehelix tint for all rows, the darkest shade (`pal[5]`) for the row the takeaway is about. For ordered magnitude (years, ranks) a sequential cubehelix by order also works; not for cyclic groups like months, where December and January would get opposite colours.
- Overlap: tallest ridge ≈ 1.5 rows. More overlap hides the rows behind; less wastes height.
- Bandwidth: Scott's rule is the default; multiply `h` by 0.5–0.8 for multimodal data, and say so if the shape matters.
- Small groups (< 30 values) make unreliable curves — use P4 strip points instead.
- Height ≈ `0.5 × n + 2` in.
