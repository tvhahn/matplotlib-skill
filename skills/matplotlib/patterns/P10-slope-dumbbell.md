# Slope Chart / Dumbbell

**Use for:** change between two points per item — two years, before/after, rank change.
Many time points → line chart (`other-charts.md`); min/avg/max ranges → P5.

## Contents
- Slope chart (few items, the direction of change is the story)
- Dumbbell (more items, or long names; sorted rows)

## Slope chart

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
import matplotlib.patheffects as pe

# --- Data: one value per item and period; adapt the column names ---
df = pd.read_csv("data.csv").dropna(subset=["item", "period", "value"])
p0, p1 = df["period"].min(), df["period"].max()  # or the two periods the question names
wide = df[df["period"].isin([p0, p1])].groupby(["item", "period"])["value"].mean().unstack()
missing = wide.index[wide.isna().any(axis=1)].tolist()  # no line without both ends
wide = wide.dropna()
change = (wide[p1] - wide[p0]).sort_values()
focus, least = change.index[-1], change.index[0]  # the item the takeaway is about

ACCENT_RED, HALO = "#bd0c0c", [pe.withStroke(linewidth=3, foreground="white")]
fig, ax = plt.subplots(figsize=(7, 6.5), dpi=150)
for item, r in wide.iterrows():
    hl = item == focus
    ax.plot([0, 1], [r[p0], r[p1]], color=ACCENT_RED if hl else "#bdbdbd", lw=2.5 if hl else 1.6,
            marker="o", ms=6, mec="white", zorder=3 if hl else 2)

# End labels, de-collided per side: push touching labels apart, centre each cluster
# on its points, push once more; a leader marks any label moved off its point
lo, hi = wide[[p0, p1]].min().min(), wide[[p0, p1]].max().max()
gap = (hi - lo) * 0.05
spread = lambda v, k: np.maximum.accumulate(v - k * gap) + k * gap
ys_all = []
for x, col, ha, dx in ((0, p0, "right", -10), (1, p1, "left", 10)):
    s = wide[col].sort_values()
    v, k = s.to_numpy(), np.arange(len(s))
    ys = spread(v, k)
    cl = np.cumsum(np.r_[True, np.diff(ys) > gap * 1.001])
    for c in np.unique(cl):
        ys[cl == c] -= (ys[cl == c] - v[cl == c]).mean()
    ys = spread(ys, k)
    ys_all += list(ys)
    for item, vi, y in zip(s.index, v, ys):
        hl = item == focus
        ax.annotate(f"{item}  {vi:.1f}" if x == 0 else f"{vi:.1f}", xy=(x, vi),
                    xytext=(x + dx / 300, y), textcoords="data", ha=ha, va="center",
                    fontsize=10.5, color=ACCENT_RED if hl else "dimgrey",
                    weight="semibold" if hl else "normal",
                    arrowprops=dict(arrowstyle="-", color="lightgrey", lw=0.6) if abs(y - vi) > gap / 4 else None)

# Change on the focus line, at the data
ax.annotate(f"{change[focus]:+.1f}", xy=(0.5, wide.loc[focus].mean()), xytext=(8, -6),
            textcoords="offset points", ha="left", va="top", fontsize=10.5, color=ACCENT_RED,
            weight="semibold", path_effects=HALO)

ax.set_xticks([0, 1], [str(p0), str(p1)], fontsize=12)
ax.set_xlim(-0.08, 1.08)
ax.set_ylim(min(lo, min(ys_all)) - gap, max(hi, max(ys_all)) + gap)
ax.set_yticks([])
ax.grid(axis="y", visible=False)

# --- Title + takeaway subtitle (computed); a second line names items left out ---
lines = [f"{focus}: {change[focus]:+.1f} from {p0} to {p1}, the largest gain; {least}: {change[least]:+.1f}"]
if missing:
    lines.append(f"Not shown: {', '.join(missing)} (no value for {p0} or {p1})")
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold",
             pad=26 + 15 * (len(lines) - 1))
ax.annotate("\n".join(lines), xy=(0, 1), xycoords="axes fraction", xytext=(0, 8),
            textcoords="offset points", ha="left", va="bottom", fontsize=10.5, color="dimgrey")
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Two x positions only, one line per item, values printed at both ends (name + value on the left, value on the right); no y-axis.
- Grey lines; the item(s) the takeaway is about in `ACCENT_RED`, with matching semibold labels.

**Guidance:**
- Highlight what the takeaway is about: the biggest gainer, the one that fell, the user's own item. When direction *is* the story (some rose, some fell), colour rises `#4575b4` and falls `#d73027` and keep the sign in the label (`+3.1` / `-2.4`) so it reads without colour.
- Compare like with like: if the membership of a group differs between periods, restrict to items present in both and say so.
- Items missing an endpoint get no line; name them in the subtitle's second line instead of silently dropping them.
- Up to ~12 items. More, or long names → dumbbell below. Rank change: plot rank (1 = top) and invert the y-axis.
- Format to the data (`.1f` years, `,.0f` counts, `%` for shares); put units in the title or subtitle.

## Dumbbell

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data: one value per item and period; adapt the column names ---
df = pd.read_csv("data.csv").dropna(subset=["item", "period", "value"])
p0, p1 = df["period"].min(), df["period"].max()  # or the two periods the question names
wide = df[df["period"].isin([p0, p1])].groupby(["item", "period"])["value"].mean().unstack()
wide = wide.dropna(subset=[p1]).sort_values(p1).reset_index()  # largest end value on top
no_start = wide.loc[wide[p0].isna(), "item"].tolist()
wide["change"] = wide[p1] - wide[p0]

START, END = "#bdbdbd", "#4575b4"
n = len(wide)
fig, ax = plt.subplots(figsize=(9, 0.6 * n + 1.8), dpi=150)
ax.hlines(wide.index, wide[p0], wide[p1], color="lightgrey", lw=3, zorder=1)
ax.scatter(wide[p0], wide.index, s=110, color=START, edgecolors="white", zorder=3)
ax.scatter(wide[p1], wide.index, s=110, color=END, edgecolors="white", zorder=3)

# Value labels on the outer side of each dot
for i, r in wide.iterrows():
    for v, other in ((r[p0], r[p1]), (r[p1], r[p0])):
        if pd.isna(v):
            continue
        out = 1 if pd.isna(other) or v >= other else -1
        ax.annotate(f"{v:,.0f}", xy=(v, i), xytext=(9 * out, 0), textcoords="offset points",
                    ha="left" if out > 0 else "right", va="center", fontsize=10, color="dimgrey")

# Direct legend: period names above the top row that has both dots
key = wide.dropna(subset=[p0]).index[-1]
for v, c in ((wide.loc[key, p0], "dimgrey"), (wide.loc[key, p1], END)):
    ax.annotate(str(p0 if c == "dimgrey" else p1), xy=(v, key), xytext=(0, 10),
                textcoords="offset points", ha="center", va="bottom", fontsize=10,
                color=c, weight="semibold")

lo, hi = np.nanmin(wide[[p0, p1]].values), np.nanmax(wide[[p0, p1]].values)
ax.set_xlim(lo - 0.1 * (hi - lo), hi + 0.1 * (hi - lo))
ax.set_ylim(-0.6, n - 0.3)
ax.set_yticks(wide.index, wide["item"], fontsize=11)
ax.set_xticks([])
ax.grid(False)

# --- Title + takeaway subtitle (computed) ---
big, small = wide.loc[wide["change"].idxmax()], wide.loc[wide["change"].idxmin()]
lines = [f"{big['item']} rose most ({big[p0]:,.0f} to {big[p1]:,.0f}); "
         f"{small['item']} least ({small['change']:+,.0f})"]
if no_start:
    lines.append(f"No {p0} value for {', '.join(no_start)}: {p1} shown alone")
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold",
             pad=26 + 15 * (len(lines) - 1))
ax.annotate("\n".join(lines), xy=(0, 1), xycoords="axes fraction", xytext=(0, 8),
            textcoords="offset points", ha="left", va="bottom", fontsize=10.5, color="dimgrey")
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Start dot light grey (`#bdbdbd`), end dot `#4575b4` (or `pal[5]`), joined by a lightgrey line; every row the same two colours.
- Period names written over the top row's dots instead of a legend; value labels on the outer side of each dot, value axis hidden.

**Guidance:**
- Sort by the end value (largest on top) or by the change when change is the question; keep a natural order if the items have one.
- Missing start or end: show the dot that exists, and say which items are incomplete in the subtitle.
- When the end values dwarf the start values (36x growth), the start dots crowd at the left; consider a log x-axis or plotting the ratio as P1 bars instead.
- Format to the data: `\$` and thousands separators for money (`f"\${v:,.0f}"`), `%` for shares.
- Height ≈ `0.6 × n + 1.8` in. With > 20 rows drop the start labels and keep only the end values.
