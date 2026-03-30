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

# --- Dynamic figsize (match data aspect ratio for set_aspect(1)) ---
x_span = X[:, 0].max() - X[:, 0].min()
y_span = X[:, 1].max() - X[:, 1].min()
data_aspect = x_span / y_span if y_span > 0 else 1.0
base = 7
fig_w = base * max(1.0, data_aspect) + 2.0  # extra width for outside legends
fig_h = base * max(1.0, 1.0 / data_aspect)

fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)

# probability-sized dots ONLY — never use pcolormesh or contourf
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

ax.set_ylabel(r"$x_1$")
ax.set_xlabel(r"$x_0$")
ax.set_aspect(1)  # mandatory — decision boundaries must be square
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_title("Decision Boundary", fontsize=14, loc="left", pad=7)

# --- Insight annotation (per-class counts from data) ---
class_counts = [np.sum(y == i) for i in range(len(class_names))]
counts_str = " · ".join(f"{n} ({c})" for n, c in zip(class_names, class_counts))
ax.text(0.02, 0.02, f"{len(class_names)} classes · {counts_str}",
        transform=ax.transAxes, ha="left", va="bottom",
        fontsize=9, color="dimgrey", style="italic")

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
                       markersize=s * 8, label=l) for s, l in zip(prob_sizes, prob_labels)]
ax.legend(handles=prob_handles, loc="center",
          bbox_to_anchor=(1.05, 0.65), frameon=True, facecolor="white",
          framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey", title="Prob")
ax.add_artist(legend1)

sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Colors: DIVERGING_COLORBLIND `["#d73027", "#4575b4", "#fc8d59"]`. For 2-class, use `["#d73027", "#4575b4"]`.
- Background uses probability-sized dots — not `contourf` or `pcolormesh` filled regions.
- Two separate legends: class legend and confidence legend. Use `ax.add_artist()` to keep both visible.
- `set_aspect(1)` for square proportions.

**Guidance:**
- Default: load pre-computed data from NPZ (`xx0`, `xx1`, `yy_hat`, `yy_prob`, `X`, `y`, `class_names`). Allow sklearn import when the user provides raw data and explicitly requests fitting.
- Position legends outside with `bbox_to_anchor`; adjust positions to avoid occlusion with the data.
- Contour lines use `colors=colors[:len(class_names)]` — the same DIVERGING_COLORBLIND hex codes, not grey or black.
- Dynamic figsize is computed from data aspect ratio in the template. Do not hardcode `figsize=(8, 6)` — use the template's `data_aspect` computation.
- Use descriptive feature names instead of `$x_0$`/`$x_1$` when feature names are available and meaningful.
- The precomputed mesh is ~50×50 (~2,500 dots). The `s=25 * prob` linear scaling is tuned for this density. Do not subsample or resize the mesh.
- Use classical titles that describe the chart (e.g., "KNN Decision Boundary — Iris Species"). Insight annotations carry findings, not the title.
- Always include an insight annotation: class count + sample size at minimum. If class_names are descriptive, mention the most/least separated classes. Position in lower-left using `transform=ax.transAxes`.

**Customize:** Assumes `xx0`, `xx1`, `yy_hat`, `yy_prob`, `X`, `y`, `class_names` are already in memory.
