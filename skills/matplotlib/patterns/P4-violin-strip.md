# Violin + Strip Plot

**Use for:** comparing distributions across categories while showing every observation.
**Exemplars:** `exemplars/P4-a.png` (2 groups with a long right tail) and `exemplars/P4-b.png` (3 species, one decimal). Fixed: white violins with black points, red median ticks with haloed labels. Varies: height, strip alpha, units, subtitle comparison.

```python
import matplotlib.patheffects as pe

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
HALO = [pe.withStroke(linewidth=3, foreground="white")]

# --- Data ---
df = pd.read_csv("data.csv").dropna(subset=["value", "category"])
medians = df.groupby("category")["value"].median().sort_values(ascending=False)
order = medians.index.tolist()  # one explicit order shared by every layer
n_cats = len(order)

fig, ax = plt.subplots(figsize=(11, max(4.5, 1.3 * n_cats + 1.8)), dpi=150)
sns.violinplot(data=df, x="value", y="category", order=order, orient="h",
               density_norm="width", inner=None, cut=0, linewidth=1.8,
               color="white", saturation=1, width=0.8, zorder=0, ax=ax)
sns.stripplot(data=df, x="value", y="category", order=order, orient="h",
              size=5, jitter=0.18, color="black", alpha=0.15, linewidth=0,
              zorder=3, ax=ax)

# --- Median markers + labels, positioned by the shared order ---
for i, cat in enumerate(order):
    med = medians[cat]
    ax.plot(med, i, marker="|", color="#d73027", markersize=22, markeredgewidth=2.5, zorder=5)
    t = ax.annotate(f"{med:,.0f}", xy=(med, i), xytext=(0, 14), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, color="dimgrey", weight="semibold",
                    zorder=6)
    t.set_path_effects(HALO)  # the label sits over strip points: halo, not a box

# --- Title + takeaway subtitle ---
gap = medians.iloc[0] - medians.iloc[-1]
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey",
             weight="semibold", pad=26)
ax.annotate(f"{order[0]} median is {gap:,.0f} units above {order[-1]}",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")

ax.set_xlabel("Value (units)", fontsize=12, labelpad=10, color="dimgrey")
ax.set_ylabel("")
ax.grid(axis="y", visible=False)
ax.grid(axis="x", alpha=0.7, linewidth=1)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey", labelsize=11)
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- White violins (`color="white"`) with black strip points: the white-with-black-dots look.
- Violin params `density_norm="width", inner=None, cut=0`.

**Guidance:**
- Pass the same `order=` to every layer and to the label loop — positions are indices into that order.
- Horizontal by default (room for long labels). Vertical suits 2–3 categories with short labels.
- Median marker: a short `#d73027` tick so it stands out from the black points, with its value above it in a white halo (style-reference Craft) so the label stays readable over the strip. Use `,.0f` for counts and large units, `.1f` for small decimals; add units in the axis label.
- Strip `alpha`: ~0.05 for thousands of points, ~0.3 for under 100. Lower `jitter` if points spill past narrow violins.
- Add `n=` to category tick labels (`f"{cat}\nn={count}"`) when group sizes differ.
- `density_norm="count"` when the difference in group size is itself part of the story.
- Subtitle states the comparison the reader came for (gap between medians, which group is most spread). Annotate a notable outlier at its point if there is one.
- Panel frame optional — consider it with 3+ categories and lots of white space.
