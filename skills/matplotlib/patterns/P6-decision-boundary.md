# Decision Boundary

**Use for:** a classifier's decision regions and confidence over two features. For an ordinary scatter plot use `other-charts.md`.
**Exemplars:** `exemplars/P6-a.png` (features on different scales → square panel) and `exemplars/P6-b.png` (same-scale features → equal aspect). Fixed: probability-sized background dots, coloured contours, two outside legends. Varies: aspect handling, circled errors, feature labels.

```python
from matplotlib.lines import Line2D

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data (load from NPZ) ---
data = np.load("data.npz", allow_pickle=True)
xx0, xx1 = data["mesh_x0"], data["mesh_x1"]
yy_hat, yy_prob = data["yy_hat"], data["yy_prob"]
X, y = data["X"], data["y"]
class_names = data["class_names"].tolist()

# --- Palette (DIVERGING_COLORBLIND only) ---
redish = "#d73027"
blueish = "#4575b4"
orangeish = "#fc8d59"
colors = [redish, blueish, orangeish]

mesh_points = np.c_[xx0.ravel(), xx1.ravel()]

# --- Square plot: equal data scaling only when both features share a scale ---
x_span = X[:, 0].max() - X[:, 0].min()
y_span = X[:, 1].max() - X[:, 1].min()
data_aspect = x_span / y_span if y_span > 0 else 1.0
equal_scale = 0.5 <= data_aspect <= 2  # e.g. two lengths in mm with similar ranges
base = 7
if equal_scale:
    fig_w = base * max(1.0, data_aspect) + 2.0  # extra width for outside legends
    fig_h = base * max(1.0, 1.0 / data_aspect)
else:
    fig_w, fig_h = base + 2.0, base

fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)

# probability-sized background dots (the pattern's look; not contourf/pcolormesh)
colormap = np.array(colors[:len(class_names)])
ax.scatter(mesh_points[:, 0], mesh_points[:, 1], c=colormap[yy_hat.ravel()],
           alpha=0.3, s=25 * yy_prob.ravel(), linewidths=0)

# contour lines at decision boundaries
ax.contour(xx0, xx1, yy_hat,
           levels=len(class_names) - 1, linewidths=1,
           colors=colors[:len(class_names)])

# true data points
ax.scatter(X[:, 0], X[:, 1], c=colormap[y], s=50,
           zorder=3, linewidths=0.7, edgecolor="k")

ax.set_ylabel(r"$x_1$", fontsize=12, labelpad=8, color="dimgrey")
ax.set_xlabel(r"$x_0$", fontsize=12, labelpad=8, color="dimgrey")
if equal_scale:
    ax.set_aspect(1)      # one unit on x = one unit on y
else:
    ax.set_box_aspect(1)  # square panel; features on different scales
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
# --- Insight: how many points fall in another class's region (nearest mesh cell) ---
ix = np.abs(xx0[0][None, :] - X[:, [0]]).argmin(axis=1)
iy = np.abs(xx1[:, 0][None, :] - X[:, [1]]).argmin(axis=1)
wrong = yy_hat[iy, ix] != y
ax.scatter(X[wrong, 0], X[wrong, 1], s=110, facecolors="none", edgecolors="dimgrey",
           linewidths=1.2, zorder=4)

ax.set_title("KNN Decision Boundary — Dataset Name", fontsize=14, loc="left", pad=26,
             color="dimgrey", weight="semibold")
ax.annotate(f"{wrong.sum()} of {len(y)} points (circled) fall inside another class's region",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")

# class legend
class_handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c,
                        markersize=8, markeredgecolor="k", markeredgewidth=0.7,
                        label=n) for c, n in zip(colors, class_names)]
legend1 = ax.legend(handles=class_handles, loc="center left",
                    bbox_to_anchor=(1.02, 0.35), frameon=True, facecolor="white",
                    framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey", title="Class")

# probability legend
prob_sizes = [0.4, 0.7, 1.0]
prob_labels = ["Low", "Med", "High"]
prob_handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor="grey",
                       markersize=s * 8, label=l) for s, l in zip(prob_sizes, prob_labels)]
ax.legend(handles=prob_handles, loc="center left",
          bbox_to_anchor=(1.02, 0.68), frameon=True, facecolor="white",
          framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey", title="Prob")
ax.add_artist(legend1)
for leg in (legend1, ax.get_legend()):
    leg.get_title().set_color("dimgrey")

sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Colors: DIVERGING_COLORBLIND `["#d73027", "#4575b4", "#fc8d59"]`. For 2-class, use `["#d73027", "#4575b4"]`.
- Background of probability-sized dots, not `contourf`/`pcolormesh` fills.
- Two separate legends: class legend and confidence legend. Use `ax.add_artist()` to keep both visible.
- Square proportions: `set_aspect(1)` when both features share a scale, else `set_box_aspect(1)`.

**Guidance:**
- Default: load pre-computed data from NPZ (`xx0`, `xx1`, `yy_hat`, `yy_prob`, `X`, `y`, `class_names`). Allow sklearn import when the user provides raw data and explicitly requests fitting.
- Position legends outside with `bbox_to_anchor`; adjust positions to avoid occlusion with the data.
- Contour lines use `colors=colors[:len(class_names)]` — the same DIVERGING_COLORBLIND hex codes, not grey or black.
- Size the figure from the data aspect ratio as the template does, so `set_aspect(1)` doesn't leave large empty margins. Features in different units or with very different ranges get a square panel (`set_box_aspect(1)`) instead of a long strip.
- Use descriptive feature names instead of `$x_0$`/`$x_1$` when feature names are available and meaningful.
- `s=25 * prob` suits a ~50×50 mesh; scale `s` inversely with mesh density for finer meshes.
- Use classical titles that describe the chart (e.g., "KNN Decision Boundary — Iris Species"); the finding goes in the subtitle beneath it.
- The template circles points that sit in another class's region and counts them in the subtitle — a finding the reader can't get from the legend. If one cluster of errors stands out, label it at the data with a haloed annotation (style-reference Craft).

