# Part-to-Whole: 100% Stacked Bars / Stacked Area

**Use for:** composition — each component's share within a group (100% bars) or how
the mix changes over time (stacked area). Never a pie: shares compared by length or
height along a common baseline read far more precisely than angles.
**Exemplars:** `exemplars/P11-share-bars.png` (3 groups, 2 components) and `exemplars/P11-stacked-area.png` (2 named components + Other over 20 years). Fixed: white separators, story component on the common baseline, names inside the bands. Varies: which component is coloured, label placement.

## Contents
- 100% stacked horizontal bars (share within each of a few groups)
- Stacked area over time

## 100% stacked bars

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
from matplotlib.colors import to_rgb

# --- Data: one row per observation; adapt the column names ---
df = pd.read_csv("data.csv").dropna(subset=["group", "component"])
top4 = df["component"].value_counts().index[:4]
if df["component"].nunique() > 5:  # at most 5 segments: fold the rest into "Other"
    df["component"] = df["component"].where(df["component"].isin(top4), "Other")
share = pd.crosstab(df["group"], df["component"], normalize="index")
n_obs = df["group"].value_counts()
focus = share.mean().drop("Other", errors="ignore").idxmin()  # or name the story component
rest = [c for c in share.mean().sort_values(ascending=False).index if c not in (focus, "Other")]
comps = [focus] + rest + (["Other"] if "Other" in share else [])
share = share[comps].sort_values(focus)  # nominal groups: highest focus share on top
# natural order instead: share = share.reindex(["First", "Second", "Third"][::-1])

colors = dict(zip(comps, ["#4575b4", "#bdbdbd", "#d9d9d9", "#969696", "#ececec"]))
n = len(share)
# Name the segments over the top bar when every name fits its segment, else a legend
names_fit = all(share.iloc[-1][c] > 0.013 * len(str(c)) + 0.01 for c in comps)
fig, ax = plt.subplots(figsize=(9, 0.7 * n + 2), dpi=150)
left = np.zeros(n)
for c in comps:
    w = share[c].values
    ax.barh(range(n), w, left=left, height=0.7, color=colors[c], edgecolor="white",
            linewidth=1.5, label=c)
    lum = np.dot(to_rgb(colors[c]), [0.299, 0.587, 0.114])
    for i, (x0, wi) in enumerate(zip(left, w)):
        if wi >= 0.07:  # label only segments wide enough to hold it
            ax.text(x0 + wi / 2, i, f"{wi:.0%}", ha="center", va="center", fontsize=10.5,
                    weight="semibold", color="white" if lum < 0.6 else "dimgrey")
    if names_fit:
        ax.text(left[-1] + 0.005, n - 0.55, c, ha="left", va="bottom", fontsize=10.5,
                weight="semibold", color=colors[c] if c == focus else "dimgrey")
    left += w
if not names_fit:
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=len(comps), frameon=True,
              facecolor="white", framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey")

ax.set_yticks(range(n), [f"{g}  (n={n_obs[g]:,})" for g in share.index], fontsize=11)
ax.set_xlim(0, 1)
ax.set_ylim(-0.5, n - (0.1 if names_fit else 0.5))
ax.set_xticks([])
ax.grid(False)

# --- Title + takeaway subtitle (computed) ---
hi, lo = share[focus].idxmax(), share[focus].idxmin()
ratio = f" ({share.loc[hi, focus] / share.loc[lo, focus]:.1f}x)" if share.loc[lo, focus] > 0 else ""
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold",
             pad=26 if names_fit else 52)
ax.annotate(f"{focus}: {share.loc[hi, focus]:.0%} in {hi} vs {share.loc[lo, focus]:.0%} in {lo}{ratio}",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8 if names_fit else 34),
            textcoords="offset points", ha="left", va="bottom", fontsize=10.5, color="dimgrey")
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- The component the takeaway is about sits at the baseline (left) in `#4575b4`; the rest in light greys, segments separated by white edges.
- Percent labels inside segments only when wide enough (white on dark, dimgrey on light); component names over the top bar (a legend above the plot only when a name will not fit); value axis hidden.

**Guidance:**
- 100% bars compare shares; plain stacked bars (`left` from counts, no `normalize`) compare totals too — but only the baseline component can then be compared precisely.
- ≤ 5 components; the template folds the rest into "Other" and puts it last (rightmost).
- When no single component is the story, colour components from `CATEGORICAL` in order and keep the white edges.
- Groups with a natural order (class, age band, rating) keep it; nominal groups sort by the focus share.
- Show `n=` in the group labels when group sizes differ; a 90% share of 12 people is not a 90% share of 1,200.

## Stacked area

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
import matplotlib.ticker as mticker
from matplotlib.colors import to_rgb

# --- Data: long format x / component / value; adapt the column names ---
df = pd.read_csv("data.csv").dropna(subset=["x", "component", "value"])
wide = df.pivot_table(index="x", columns="component", values="value", aggfunc="sum").fillna(0)
if wide.shape[1] > 5:  # at most 5 bands: fold the smallest into "Other"
    keep = wide.sum().nlargest(4).index
    wide = wide[keep].assign(Other=wide.drop(columns=keep).sum(axis=1))
share = wide.div(wide.sum(axis=1), axis=0) * 100  # shares; plot `wide` for totals
first, last = share.iloc[0], share.iloc[-1]
focus = (last - first).abs().drop("Other", errors="ignore").idxmax()  # share moved most
order = [focus] + [c for c in last.sort_values(ascending=False).index if c not in (focus, "Other")]
order += ["Other"] if "Other" in share else []  # Other on top
colors = dict(zip(order, ["#4575b4", "#bdbdbd", "#d9d9d9", "#969696", "#ececec"]))

fig, ax = plt.subplots(figsize=(11, 6), dpi=150)
ax.stackplot(share.index, [share[c] for c in order], colors=[colors[c] for c in order],
             edgecolor="white", linewidth=0.5)

# Direct labels inside each band at the right end (outside when the band is thin)
x0, x1 = share.index[0], share.index[-1]
mid = share[order].cumsum(axis=1) - share[order] / 2
prev = -np.inf
for c in order:
    h, y = last[c], mid.loc[x1, c]
    inside = h >= 8
    if not inside:  # thin bands: label outside, nudged apart
        y = prev = max(y, prev + 6)
    lum = np.dot(to_rgb(colors[c]), [0.299, 0.587, 0.114])
    label = f"{c}\n{h:.0f}%" if inside else f"{c}  {h:.0f}%"
    ax.annotate(label, xy=(x1, y), xytext=(-10 if inside else 8, 0),
                textcoords="offset points", ha="right" if inside else "left", va="center",
                fontsize=10.5, weight="semibold",
                color="white" if inside and lum < 0.6 else "dimgrey")

# The focus component's biggest one-step gain, inside its band where it happens
step = share[focus].diff()
xj = step.idxmax()
ax.annotate(f"{step[xj]:+.0f} pts\nin {xj}", xy=(xj, share.loc[xj, focus] / 2), xytext=(6, 0),
            textcoords="offset points", ha="left", va="center", fontsize=10, color="white")

ax.set_xlim(x0, x1)
ax.set_ylim(0, 100)
ax.margins(0)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax.set_ylabel("Share of total", fontsize=12, labelpad=8, color="dimgrey")
ax.set_xlabel("")
ax.grid(False)

# --- Title + takeaway subtitle (computed) ---
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold", pad=26)
verb = "grew" if last[focus] > first[focus] else "fell"
ax.annotate(f"{focus} {verb} from {first[focus]:.0f}% to {last[focus]:.0f}% of the total, {x0}–{x1}",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- `ax.stackplot` with white band separators (`edgecolor="white", linewidth=0.5`); the focus component at the bottom so it has a common baseline.
- Direct labels (name + latest share) inside each band at the right end; no legend.

**Guidance:**
- Shares (0–100%) when the question is about the mix; totals (`wide`) when the total matters too. Totals: y from 0, units in the label.
- Colour: grey + `#4575b4` for one story component; `CATEGORICAL` in order when every component matters. Stacking order = legend order = label order.
- ≤ 5 bands; the template folds the smallest into "Other" at the top.
- The subtitle verb follows the sign of the change. Annotate a turning point (a crossover, a policy year) at the data rather than in a footer.
- Only the bottom band and the total can be read precisely; if the reader must compare a middle band over time, plot it as its own line (other-charts.md) instead.
