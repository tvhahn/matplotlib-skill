# Chart Patterns

9 self-contained code patterns for common chart types, all following Tim's aesthetic.
Claude reads this file and adapts the closest pattern to the user's data.

---

## 1. Horizontal Bar Chart

**When to use:** Ranked percentages, category comparisons, survey results.
**Palette:** `Blues_d` for neutral ranking, or `Greys_r` + `ACCENT_RED` for selective emphasis.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(4, 7), dpi=150)

sns.barplot(x="percent", y="category", hue="category", data=df, palette="Blues_d", legend=False, ax=ax)

for p in ax.patches:
    space = 1.5
    _x = p.get_x() + p.get_width() + space
    _y = p.get_y() + p.get_height() / 2
    value = p.get_width()
    ax.text(_x, _y, f"{value:.1f}%", ha="left", va="center",
            weight="semibold", size=10, color="dimgrey")

ax.set_ylabel("")
ax.set_xlabel("")
ax.axvline(x=0, color="lightgrey", linewidth=0.8, zorder=0)
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_xticks([])
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7)
sns.despine(left=True, bottom=True)
```

**Customize:** Replace `"Blues_d"` with a custom palette list for selective emphasis (e.g., one red bar among grey). Add `ax.tick_params(axis="y", labelsize=16)` to increase label size.

---

## 2. Vertical Bar Chart

**When to use:** Correlations, scored rankings, model comparisons.
**Palette:** `rocket` for sequential, diverging colorblind palette for pos/neg values.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

sns.barplot(x="category", y="value", hue="category", data=df, palette="rocket", legend=False, ax=ax)

for i, p in enumerate(ax.patches):
    space = abs(df["value"].max()) * 0.1
    value = p.get_height()
    _y = p.get_y() + p.get_height() + space
    _x = p.get_x() + p.get_width() / 2
    ax.text(_x, _y, f"{value:.2f}", ha="center", va="center",
            weight="semibold", size=12, color="dimgrey")

sns.despine(left=True, bottom=True)
ax.grid(alpha=0.7, linewidth=1, axis="y")
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_title(r"$\bf{(a)}$" + " Chart Title", loc="left", fontsize=14, pad=7)
```

**Customize:** For rotated x-labels, add `ax.set_xticklabels(ax.get_xticklabels(), rotation=90)`.

---

## 3. Time Series with Predictions

**When to use:** Predicted vs actual with rolling average, RUL estimation, regression results.
**Palette:** `#4575b4` (blue) for true, `#d73027` (red) for rolling avg, grey scatter for predictions.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")

ax.plot(y_true_sorted, label="True Values", alpha=1, color="#4575b4", linewidth=1, zorder=0)

ax.scatter(np.arange(len(y_pred)), y_pred_sorted, label="Predicted",
           alpha=0.4, c="grey", edgecolors="none", s=2)

window_size = 12
rolling_avg = np.convolve(y_pred_sorted, np.ones(window_size), "valid") / window_size
ax.plot(np.arange(len(y_pred))[window_size - 1:], rolling_avg,
        color="#d73027", alpha=1, label="Rolling Avg", linewidth=1.5)

# metric annotation box
rmse = 0.042
r2 = 0.95
x_min, x_max = ax.get_xlim()
y_min, y_max = ax.get_ylim()
ax.text(
    (x_max - x_min) * 0.03 + x_min,
    y_max - (y_max - y_min) * 0.05,
    f"RMSE = {rmse:.3f}\n$R^2$ = {r2:.3f}",
    fontsize=9, fontweight="normal", color="dimgrey",
    verticalalignment="top", horizontalalignment="left",
    bbox={"facecolor": "gray", "alpha": 0.0, "pad": 6},
)

ax.set_xlabel("Time")
ax.set_ylabel("Value")
ax.legend(loc="lower right", fontsize=10, frameon=True, facecolor="white",
         framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey")
ax.set_title(r"$\bf{(a)}$" + " Prediction Results", loc="left", fontsize=12, pad=7)
sns.despine(left=True, bottom=True)
```

**Customize:** Adjust `window_size` for smoothing. Change x-axis labels to time units. Use `*100` to convert to percentages.

---

## 4. Violin + Strip Plot

**When to use:** Distribution comparisons, showing individual observations within categories.
**Palette:** White violins with black strip overlay.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(12, 5), dpi=150)

sns.violinplot(
    x="value", y="category", data=df,
    density_norm="width", inner=None, linewidth=2,
    color="white", saturation=1, cut=0,  # white fill is the signature look
    orient="h", zorder=0, width=0.8, ax=ax,
)

sns.stripplot(
    x="value", y="category", data=df,
    size=6, jitter=0.2, color="black", linewidth=0.5,  # black dots on white violins
    marker="o", edgecolor=None, alpha=0.1,
    zorder=4, orient="h", ax=ax,
)

ax.grid(axis="x", alpha=0.7, linewidth=1)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.yaxis.label.set_visible(False)
ax.tick_params(axis="x", labelsize=12)
ax.set_xlabel("Value", labelpad=10, fontsize=12)
ax.set_title(r"$\bf{(a)}$" + " Distribution Title", fontsize=12, loc="left", pad=7)
sns.despine(left=True, bottom=True)
```

**Customize:** Adjust `alpha` on stripplot for density. Use `density_norm="count"` for proportional widths. For vertical orientation, swap x/y and set `orient="v"`. Keep `color="white"` on violins — the white-fill-with-black-dots aesthetic is distinctive; only use colored fills when the user explicitly requests it.

---

## 5. Lollipop / Dumbbell Chart

**When to use:** Showing min/max/avg ranges, model comparison across k-folds.
**Palette:** Cubehelix for dots, grey for connecting lines, dimgrey for text.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)
darkblue = pal[5]  # "#1f253f"
lightblue = pal[2]  # "#58849f"

fig, ax = plt.subplots(figsize=(10, 8), dpi=150)

DOT_SIZE = 150

# avg dots
ax.scatter(x=df["avg"], y=df["name"], s=DOT_SIZE, alpha=1,
           label="Average", color=lightblue, edgecolors="white")
# min/max dots
ax.scatter(x=df["min"], y=df["name"], s=DOT_SIZE, alpha=1,
           color=darkblue, label="Min/Max", edgecolors="white")
ax.scatter(x=df["max"], y=df["name"], s=DOT_SIZE, alpha=1,
           color=darkblue, edgecolors="white")

# connecting lines
ax.hlines(y=df["name"], xmin=df["min"], xmax=df["max"],
          color="grey", alpha=0.4, lw=4, zorder=0)

# value annotations
for i in range(df.shape[0]):
    ax.text(x=df["avg"].iloc[i], y=i + 0.15, s=f'{df["avg"].iloc[i]:.2f}',
            ha="center", va="bottom", size="x-large",
            color="dimgrey", weight="medium")

ax.grid(False)
sns.despine(left=True, bottom=True)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.tick_params(axis="x", pad=20, labelsize="x-large")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7)

ax.legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
         bbox_to_anchor=(0.6, 1.05), ncol=2, fontsize="x-large", labelcolor="dimgrey")
```

**Customize:** Add leading lines with `ax.plot([x_end + 0.02, x_label], [i, i], lw=1, color="grey", alpha=0.4, zorder=0)`. Add classifier name text at left margin.

---

## 6. Decision Boundary / Scatter

**When to use:** Classification visualization, probability maps, cluster visualization.
**Palette:** Colorblind diverging (`#d73027`, `#4575b4`, `#fc8d59`).

```python
from sklearn.neighbors import KNeighborsClassifier
from matplotlib.lines import Line2D

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

redish = "#d73027"
blueish = "#4575b4"
orangeish = "#fc8d59"
colors = [redish, blueish, orangeish]
class_names = ["Class 0", "Class 1", "Class 2"]

# --- fit classifier ---
clf = KNeighborsClassifier(n_neighbors=15)
clf.fit(X, y)

# --- mesh grid for decision surface ---
h = 0.02  # step size
x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
xx0, xx1 = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
mesh_points = np.c_[xx0.ravel(), xx1.ravel()]
yy_hat = clf.predict(mesh_points)
yy_prob = clf.predict_proba(mesh_points).max(axis=1)

fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

# probability dots (sized by confidence)
colormap = np.array(colors)
ax.scatter(mesh_points[:, 0], mesh_points[:, 1], c=colormap[yy_hat],
           alpha=0.3, s=40 * yy_prob**3, linewidths=0)

# contour lines at decision boundaries
ax.contour(xx0, xx1, yy_hat.reshape(xx0.shape),
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

**Customize:** Swap `KNeighborsClassifier` for any sklearn classifier. Adjust `h` for mesh resolution. Use `clf.predict_proba` for probability-sized dots. For 2-class problems, remove `orangeish` from the palette.

---

## 7. Heatmap / Spectrogram

**When to use:** Correlation matrices, frequency-time plots, spectrograms, pcolormesh data.
**Palette:** `rocket` for correlation heatmaps, `inferno` for spectrograms.

### Correlation Heatmap

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

corr = df.select_dtypes("number").corr()

sns.heatmap(corr, annot=True, fmt=".2f", cmap="rocket", ax=ax,
            linewidths=0.5, linecolor="white", square=True,
            cbar_kws={"shrink": 0.8})

ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_title("Correlation Matrix", fontsize=14, loc="left", pad=7)
sns.despine(left=True, bottom=True)
```

### Spectrogram (pcolormesh)

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(1, 2, figsize=(11, 4), dpi=150)

ax[0].pcolormesh(time_axis, freq_axis, data, cmap="inferno",
                 vmax=vmax_val, shading="auto")
ax[0].set_ylabel("Frequency (Hz)")
ax[0].set_xlabel("Runtime (days)")
ax[0].grid(False)
ax[0].tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax[0].set_title(r"$\bf{(a)}$" + " Spectrogram", loc="left", fontsize=12, pad=7)

ax[1].pcolormesh(time_axis, bins, binned_data, cmap="inferno",
                 vmax=vmax_val2, shading="auto")
ax[1].set_xlabel("Runtime (days)")
ax[1].set_ylabel("Frequency Bin")
ax[1].grid(False)
ax[1].tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax[1].set_title(r"$\bf{(b)}$" + " Binned", loc="left", fontsize=12, pad=7)

sns.despine(left=True, bottom=True, right=True)
```

**Customize:** For the heatmap, use `mask=np.triu(np.ones_like(corr, dtype=bool))` to show only the lower triangle. Adjust `vmax` on spectrograms to control color scaling. For spectrograms with dark backgrounds, use white text for panel labels.

---

## 8. Multi-Panel Grid (GridSpec)

**When to use:** 2x2, 3x3, or irregular layouts showing same metric across different datasets/conditions.
**Layout:** GridSpec with shared formatting, enumerated panel labels.

```python
from matplotlib import gridspec

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig = plt.figure(figsize=(14, 12), dpi=150)
gs = gridspec.GridSpec(3, 3)
axes_list = [plt.subplot(gs[i, j]) for i in range(3) for j in range(3)]
gs.update(wspace=0.15, hspace=0.4)

labels = [chr(ord('a') + i) for i in range(9)]
titles = [f"Dataset {i+1}" for i in range(9)]

for i, (ax, label, title) in enumerate(zip(axes_list, labels, titles)):
    ax.grid(False)
    ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")

    # --- subplot outline (frames each panel) ---
    ax.patch.set_edgecolor("lightgrey")
    ax.patch.set_linewidth(0.8)

    # Example: line + scatter per panel (adapt to your data)
    ax.plot(x_data, y_true, color="#4575b4", linewidth=1, label="True")
    ax.scatter(x_data, y_pred, alpha=0.4, c="grey", s=2, edgecolors="none", label="Predicted")
    ax.plot(x_data, y_rolling, color="#d73027", linewidth=1.5, label="Rolling Avg")

    # metric annotation box
    ax.text(0.97, 0.95, f"RMSE = {rmse:.3f}\n$R^2$ = {r2:.3f}",
            transform=ax.transAxes, fontsize=8, color="dimgrey",
            va="top", ha="right",
            bbox={"facecolor": "gray", "alpha": 0.0, "pad": 4})

    ax.set_title(r"$\bf{(" + label + r")}$" + f" {title}", loc="left", fontsize=12, pad=7)

    if i == 0:
        ax.set_xlabel("X Label")
        ax.set_ylabel("Y Label")
        ax.legend(loc="lower right", fontsize=10, frameon=True, facecolor="white",
                 framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey")
    else:
        ax.set_yticklabels([])

sns.despine(left=True, bottom=True)
```

**Customize:** Adjust GridSpec dimensions. Only label axes on the first panel (i==0). Use `gs.update(wspace=, hspace=)` for spacing. Remove `ax.patch.set_edgecolor/linewidth` lines if panel borders are not desired.

---

## 9. PR/ROC Curves

**When to use:** Classification model evaluation, cross-validation performance.
**Palette:** Cubehelix `pal[5]` for average, grey for k-folds, orange dashed for baseline.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True, dpi=150)
fig.tight_layout(pad=5.0)

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

# PR curve panel
for i, (p, r) in enumerate(zip(precision_array, recall_array)):
    label = "k-fold models" if i == len(precision_array) - 1 else None
    axes[0].plot(r, p, color="grey", alpha=0.5, linewidth=1, label=label)

axes[0].plot(recall_avg, precision_avg, label="Average model",
             color=pal[5], linewidth=2)

axes[0].plot([0, 1], [baseline, baseline], linestyle="--",
             label="No skill model", color="orange", linewidth=2, zorder=0)

axes[0].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
               labelcolor="dimgrey")
axes[0].set_title(r"$\bf{(a)}$" + " Precision-Recall Curve", loc="left", fontsize=12, pad=7)
axes[0].set_xlabel("Recall")
axes[0].set_ylabel("Precision")

# ROC curve panel
for i, (t, f) in enumerate(zip(tpr_array, fpr_array)):
    label = "k-fold models" if i == len(tpr_array) - 1 else None
    axes[1].plot(f, t, color="grey", alpha=0.5, linewidth=1, label=label)

axes[1].plot(fpr_avg, tpr_avg, label="Average of k-folds",
             color=pal[5], linewidth=2)

axes[1].plot([0, 1], [0, 1], linestyle="--",
             label="No skill", color="orange", linewidth=2, zorder=0)

axes[1].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
               labelcolor="dimgrey")
axes[1].set_title(r"$\bf{(b)}$" + " ROC Curve", loc="left", fontsize=12, pad=7)
axes[1].set_xlabel("False Positive Rate")
axes[1].set_ylabel("True Positive Rate")

for ax in axes.flatten():
    ax.yaxis.set_tick_params(labelleft=True, which="major")
    ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
    ax.grid(False)

sns.despine(left=True, bottom=True)
```

**Customize:** Add AUC text annotations below each panel. Adjust `x_axis_n` for curve smoothing resolution.
