# Decision Boundary / Scatter

**When to use:** Classification visualization, probability maps, cluster visualization.
**Palette:** Colorblind diverging (`#d73027`, `#4575b4`, `#fc8d59`).

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

fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

# probability dots (sized by confidence)
colormap = np.array(colors[:len(class_names)])
ax.scatter(mesh_points[:, 0], mesh_points[:, 1], c=colormap[yy_hat.ravel()],
           alpha=0.3, s=40 * yy_prob.ravel()**3, linewidths=0)

# contour lines at decision boundaries
ax.contour(xx0, xx1, yy_hat,
           levels=len(class_names) - 1, linewidths=1,
           colors=colors[:len(class_names)])

# true data points
ax.scatter(X[:, 0], X[:, 1], c=colormap[y], s=50,
           zorder=3, linewidths=0.7, edgecolor="k")

ax.set_ylabel(r"$x_1$")
ax.set_xlabel(r"$x_0$")
ax.set_aspect(1)
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_title("Decision Boundary", fontsize=14, loc="left", pad=7)

# class legend
class_handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c,
                        markersize=8, markeredgecolor="k", markeredgewidth=0.7,
                        label=n) for c, n in zip(colors, class_names)]
legend1 = ax.legend(handles=class_handles, loc="center",
                    bbox_to_anchor=(1.05, 0.35), frameon=True, facecolor="white",
                    framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey", title="Class")

# probability legend
prob_sizes = [0.4, 0.7, 1.0]
prob_labels = ["Low", "Med", "High"]
prob_handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor="grey",
                       markersize=s * 10, label=l) for s, l in zip(prob_sizes, prob_labels)]
ax.legend(handles=prob_handles, loc="center",
          bbox_to_anchor=(1.05, 0.65), frameon=True, facecolor="white",
          framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey", title="Prob")
ax.add_artist(legend1)

sns.despine(left=True, bottom=True)
```

**Rules (identity):**
- Colors: DIVERGING_COLORBLIND `["#d73027", "#4575b4", "#fc8d59"]`. For 2-class, use `["#d73027", "#4575b4"]`. Do not substitute Tableau, seaborn, or custom palettes.
- Background uses probability-sized dots (`s=40 * yy_prob**3`, `alpha=0.3`) — not `contourf` or `pcolormesh` filled regions. Contour lines use `colors=colors[:len(class_names)]` — the same DIVERGING_COLORBLIND hex codes, not grey or black.
- Assume `xx0`, `xx1`, `yy_hat`, `yy_prob`, `X`, `y`, `class_names` are in memory — do not import sklearn or fit classifiers.
- Two separate legends positioned outside with `bbox_to_anchor`: class legend and confidence legend. Use `ax.add_artist()` to keep both visible.
- `set_aspect(1)` for square proportions.
- Always use `dpi=150`. Save PDF+PNG with `bbox_inches="tight"`.

**Adapt when:**
- Adjust `figsize` if feature ranges are very asymmetric — `(8, 6)` is the default but `(10, 6)` works for wide feature ranges.
- Adjust `bbox_to_anchor` positions if legends overlap with data points.
- Use descriptive feature names instead of `$x_0$`/`$x_1$` when feature names are available and meaningful.
- Adjust probability dot `s` scaling factor for mesh density.

**Customize:** Assumes `xx0`, `xx1`, `yy_hat`, `yy_prob`, `X`, `y`, `class_names` are already in memory.
