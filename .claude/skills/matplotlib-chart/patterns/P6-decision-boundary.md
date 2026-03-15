# Decision Boundary / Scatter

**When to use:** Classification visualization, probability maps, cluster visualization.
**Palette:** Colorblind diverging (`#d73027`, `#4575b4`, `#fc8d59`).

```python
from matplotlib.lines import Line2D

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

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

**Rules:**
1. Colors must be DIVERGING_COLORBLIND: `["#d73027", "#4575b4", "#fc8d59"]` — do not substitute Tableau, seaborn, or custom color palettes. For 2-class problems, use `["#d73027", "#4575b4"]` (drop orangeish only).
2. Background must use probability-sized dots (`s=40 * yy_prob**3`, `alpha=0.3`) — do not use `contourf` or `pcolormesh` filled regions. This applies to ALL cases including binary classification.
3. Do not import sklearn or fit classifiers — assume `xx0`, `xx1`, `yy_hat`, `yy_prob`, `X`, `y`, `class_names` are already in memory.
4. Two separate legends positioned outside the plot with `bbox_to_anchor=(1.05, ...)`: class legend at `(1.05, 0.35)` and confidence legend at `(1.05, 0.65)`. Use `ax.add_artist(legend1)` to keep both visible. This dual-legend layout is mandatory even for 2-class problems.
5. `figsize=(8, 6)` — do not change to (9, 6) or other sizes.
6. `set_aspect(1)` for square-ish proportions — do not use `set_aspect("auto")`.
7. Title: `fontsize=14`, `loc="left"`, `pad=7` — single line, no multiline titles. Do not use fontsize=13.
8. Contour lines: solid (default), not dashed.
9. Axis labels: use `r"$x_0$"` and `r"$x_1$"` or descriptive feature names — not both.
10. Always use `dpi=150`. Save PDF+PNG with `bbox_inches="tight"`. Use relative paths for data.

**Customize:** Assumes `xx0`, `xx1`, `yy_hat`, `yy_prob`, `X`, `y`, `class_names` are already in memory.
