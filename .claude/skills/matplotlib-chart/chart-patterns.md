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
    ax.text(_x, _y, f"{value:.1f}", ha="left", va="center",
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

**Rules:**
- Always use `sns.barplot` — never use `ax.barh()` directly. Pass `palette="Blues_d"` to `sns.barplot`.
- Always use `palette="Blues_d"` — never substitute cubehelix, rocket, or single-color palettes. The Blues_d gradient distinguishes ranked bars.
- Figsize `(4, 7)` is the default for 8-15 bars. For fewer bars (3-5), use `(6, 4)`. Always keep `dpi=150`.
- Annotation format is just the number with no prefixes or suffixes: `f"{value:.1f}"` for decimals, `f"{value:,.0f}"` for large integers. Never prepend `$` or append `%`, `" mpg"`, `" USD"`, or any other unit — the title provides context.
- Annotation styling is fixed: `weight="semibold", size=10, color="dimgrey"`. Do not vary size.
- `set_xlabel("")` — do not add an x-axis label; value labels on bar ends make it redundant.
- `set_ylabel("")` — category names on the y-axis are self-explanatory.
- `set_xticks([])` — always hide x-axis ticks; the bar-end labels carry the values.
- Title: `fontsize=14, loc="left", pad=7` — do not use fontsize=12 or 13.
- Do not add a separate `tick_params(axis="y", labelsize=...)` call — let `font_scale=1.0` control y-tick label size.

**Customize:** Replace `"Blues_d"` with a custom palette list for selective emphasis (e.g., one red bar among grey).

---

## 2. Vertical Bar Chart

**When to use:** Comparisons across categories, ranked values, model scores.
**Palette:** `"rocket"` for ≥5 bars (sequential ranking). For ≤4 categorical bars, slice `DIVERGING_COLORBLIND`: `["#d73027", "#fc8d59", "#fee090", "#4575b4"][:n]`. Do not invent semantic colors — always use these exact hex values.
**Bar order:** Sort by value descending so the tallest bar is on the left.
**Data:** Always read from the CSV — never hardcode values from the file.
**API:** Always use `sns.barplot` — never use `ax.bar` directly.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

df_sorted = df.sort_values("value", ascending=False)

sns.barplot(x="category", y="value", hue="category", data=df_sorted, palette="rocket", legend=False, ax=ax)

for p in ax.patches:
    value = p.get_height()
    space = df_sorted["value"].max() * 0.02
    _x = p.get_x() + p.get_width() / 2
    _y = p.get_y() + value + space
    ax.text(_x, _y, f"{value:,.0f}", ha="center", va="bottom",
            weight="semibold", size=12, color="dimgrey")

sns.despine(left=True, bottom=True)
ax.grid(alpha=0.7, linewidth=1, axis="y")
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_xlabel("")
ax.set_ylabel("Y-Axis Label", fontsize=13, labelpad=10, color="dimgrey")
ax.set_title("Chart Title", loc="left", fontsize=14, pad=7)
```

**Rules:**
- Palette slice order is left-to-right: for 3 bars use `["#d73027", "#fc8d59", "#fee090"]`, for 4 use all four. Do not rearrange, skip, or substitute colors.
- Annotation format is just the number: `f"{value:,.0f}"` for integers, `f"{value:.2f}"` for decimals. Do not append unit suffixes (e.g., " MWh", " K") — units belong in the y-axis label.
- `set_xlabel("")` — do not add an x-axis label; category names on the x-axis are self-explanatory
- Do not manually adjust `set_ylim` — let matplotlib auto-scale; `bbox_inches="tight"` handles clipping

**Customize:** For rotated x-labels, add `ax.set_xticklabels(ax.get_xticklabels(), rotation=90)`. For ≥5 bars, switch palette to `"rocket"`.

---

## 3. Time Series with Rolling Average

**When to use:** Time series visualization with annual/periodic aggregation and smoothing trend line. Also suitable for predicted vs actual (see Customize).
**Palette:** `#4575b4` (blue) for negative/below-average values, `#d73027` (red) for positive/above-average values. Rolling line: cubehelix `pal[5]`.
**Data:** Always read from CSV — aggregate with `.groupby().mean()` for annual data. Filter partial periods (keep only periods with ≥6 observations). Never hardcode values.
**Rolling:** Use `pd.DataFrame.rolling(10, center=True).mean()` — never `np.convolve`. Default window is 10.
**Figsize:** `(12, 6)` for single-panel time series.
**API:** Always use `ax.bar()` for the main data — never use `ax.scatter()`, `fill_between`, colorbars, or line-only variants for the primary layer.
**Annotations:** Do not add data point annotations unless the user explicitly requests them.
**Legend:** Exactly 3 items: above-average Patch, below-average Patch, rolling mean Line2D. Do not add extra entries for the zero baseline.

```python
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

fig, ax = plt.subplots(figsize=(12, 6), dpi=150)

# Colored bars: positive vs negative
bar_colors = ["#d73027" if v >= 0 else "#4575b4" for v in df_annual["value"]]
ax.bar(df_annual["year"], df_annual["value"],
       color=bar_colors, alpha=0.55, width=0.9, zorder=2)

# Rolling mean trend line
ax.plot(df_annual["year"], df_annual["rolling"],
        color=pal[5], linewidth=2.5, label="10-year rolling mean", zorder=4)

# Zero baseline
ax.axhline(y=0, color="lightgrey", linewidth=0.8, zorder=1)

ax.set_xlabel("Year", fontsize=12, labelpad=8, color="dimgrey")
ax.set_ylabel("Y-Axis Label (Unit)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7)

# Legend with Patch handles for bar colors + Line2D for rolling
legend_handles = [
    Patch(facecolor="#d73027", alpha=0.55, label="Above average"),
    Patch(facecolor="#4575b4", alpha=0.55, label="Below average"),
    Line2D([0], [0], color=pal[5], linewidth=2.5, label="10-year rolling mean"),
]
ax.legend(handles=legend_handles, loc="upper left", fontsize=10,
         frameon=True, facecolor="white", framealpha=0.8,
         edgecolor="lightgrey", labelcolor="dimgrey")

ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.grid(False)
sns.despine(left=True, bottom=True)
```

**Customize:** Adjust rolling window size (default 10). For predicted-vs-actual, replace bars with `ax.plot()` for true values (`#4575b4`, linewidth=1) and `ax.scatter()` for predictions (grey, alpha=0.4, s=2), compute rolling on predictions via `pd.rolling()`, and add RMSE/R² annotation box. Use `ax.annotate()` with `arrowprops=dict(arrowstyle="-", color="dimgrey", lw=0.8)` for notable data points.

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
**Data:** Always read from CSV — aggregate with `.groupby().agg(min, mean, max)`. Sort by avg ascending so the highest-value category is at the top. Never hardcode values.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)
darkblue = pal[5]  # "#1f253f"
lightblue = pal[2]  # "#58849f"

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

DOT_SIZE = 150

# connecting lines (draw first, behind dots)
ax.hlines(y=df["name"], xmin=df["min"], xmax=df["max"],
          color="grey", alpha=0.4, lw=4, zorder=0)

# min/max dots
ax.scatter(x=df["min"], y=df["name"], s=DOT_SIZE,
           color=darkblue, edgecolors="white", label="Min/Max", zorder=3)
ax.scatter(x=df["max"], y=df["name"], s=DOT_SIZE,
           color=darkblue, edgecolors="white", zorder=3)

# avg dots (on top)
ax.scatter(x=df["avg"], y=df["name"], s=DOT_SIZE,
           color=lightblue, edgecolors="white", label="Average", zorder=4)

# avg value annotations (centered above each avg dot)
for i in range(df.shape[0]):
    ax.text(x=df["avg"].iloc[i], y=i + 0.15, s=f'{df["avg"].iloc[i]:,.0f}',
            ha="center", va="bottom", size=10,
            color="dimgrey", weight="medium")

ax.grid(False)
sns.despine(left=True, bottom=True)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_ylabel("")
ax.set_xlabel("")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7)

ax.legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
         labelcolor="dimgrey", loc="lower right", fontsize=11)
```

**Rules:**
- Only annotate avg values centered above each dot (`y=i + 0.15`, `ha="center"`, `va="bottom"`) — do not annotate min/max values unless the user explicitly requests it
- `grid(False)` — no x-grid or y-grid
- DOT_SIZE = 150 for all dots; do not change the dot size
- Connecting lines: `lw=4`, `alpha=0.4`, `color="grey"`, `zorder=0` — only one `hlines` call (min to max range); do not add extra lollipop sticks from zero
- Exactly 2 legend items: "Average" (lightblue) and "Min/Max" (darkblue) — do not add a Range line handle
- Legend: `loc="lower right"`, `fontsize=11` — do not use `bbox_to_anchor` unless the chart is very dense
- Annotation size: `size=10` — do not use string sizes like `"x-large"`
- Format string adapts to data: use `f'{value:,.0f}'` for large numbers/currency, `f'{value:.2f}'` for decimals
- Title: `fontsize=14`, `loc="left"`, `pad=7` — do not change these values
- Do not add `axvline` baselines, subtitle text annotations, or other decorative elements not shown in the pattern code

**Customize:** Add leading lines with `ax.plot([x_end + 0.02, x_label], [i, i], lw=1, color="grey", alpha=0.4, zorder=0)`. Add classifier name text at left margin. For min/max value labels, add `ax.text()` calls at `y=i - 0.15` with `va="top"`, `size=8.5`.

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

**Rules:**
- Colors must be DIVERGING_COLORBLIND: `["#d73027", "#4575b4", "#fc8d59"]` — do not substitute Tableau, seaborn, or custom color palettes
- Background must use probability-sized dots (`s=40 * yy_prob**3`, `alpha=0.3`) — do not use `contourf` filled regions
- Classifier: `KNeighborsClassifier(n_neighbors=15)` unless the user specifies a different classifier or k value
- Two separate legends positioned outside the plot with `bbox_to_anchor=(1.05, ...)`: class legend (lower) and confidence legend (upper). Use `ax.add_artist(legend1)` to keep both visible.
- `set_aspect(1)` for square-ish proportions — do not use `set_aspect("auto")`
- Title: `fontsize=14`, `loc="left"`, `pad=7` — single line, no multiline titles
- Contour lines: solid (default), not dashed

**Customize:** Swap `KNeighborsClassifier` for any sklearn classifier. Adjust `h` for mesh resolution. For 2-class problems, remove `orangeish` from the palette.

---

## 7. Heatmap / Spectrogram

**When to use:** Correlation matrices, frequency-time plots, spectrograms, pcolormesh data.
**Palette:** `RdBu_r` for correlation heatmaps (diverging — positive/negative need distinct colors), `inferno` for spectrograms.

### Correlation Heatmap

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

# Select only meaningful numeric columns — exclude IDs, years, indices
num_cols = [c for c in df.select_dtypes("number").columns
            if c.lower() not in ("year", "id", "index")]
corr = df[num_cols].corr()

sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", ax=ax,
            vmin=-1, vmax=1, center=0,
            linewidths=0.5, linecolor="white", square=True,
            cbar_kws={"shrink": 0.8},
            annot_kws={"size": 11, "weight": "medium"})

ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
ax.set_title("Correlation Matrix", fontsize=14, loc="left", pad=7)
sns.despine(left=True, bottom=True)
```

**Rules:**
- Always use `cmap="RdBu_r"` with `vmin=-1, vmax=1, center=0` for correlation matrices — never use sequential palettes (rocket, inferno) for correlation data
- Use `annot_kws={"size": 11, "weight": "medium"}` — do not set annotation `color`; let seaborn auto-contrast (dark text on light cells, white on dark cells)
- Use `cbar_kws={"shrink": 0.8}` — do not add a colorbar label
- Rotate x-tick labels 30° with `ha="right"` for readability
- Filter out non-measurement columns (year, id, index) before computing `.corr()`
- Show full matrix by default — do not mask the triangle unless the user requests it
- Do not add `color="dimgrey"` to the title — only annotations and tick labels use dimgrey

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

**When to use:** 2x2, 3x2, 3x3, or irregular layouts showing same metric across different datasets/conditions.
**Layout:** Always use `gridspec.GridSpec(rows, cols)` — rows first. A "3x2 grid" means 3 rows × 2 columns.
**Line color:** Use a single color `pal[5]` (darkest cubehelix) for the line across all panels — do not vary color per panel. All panels show the same metric, so color should be consistent.
**Figsize:** `(14, 9)` for 3x2, `(14, 12)` for 3x3. Always use `dpi=150`.

```python
from matplotlib import gridspec

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

fig = plt.figure(figsize=(14, 9), dpi=150)
gs = gridspec.GridSpec(3, 2)
axes_list = [plt.subplot(gs[i, j]) for i in range(3) for j in range(2)]
gs.update(wspace=0.3, hspace=0.5)

labels = [chr(ord('a') + i) for i in range(6)]
titles = ["Dataset 1", "Dataset 2", "Dataset 3", "Dataset 4", "Dataset 5", "Dataset 6"]

for i, (ax, label, title) in enumerate(zip(axes_list, labels, titles)):
    row, col = divmod(i, 2)

    ax.grid(False)
    ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")

    # --- subplot outline (frames each panel) ---
    ax.patch.set_edgecolor("lightgrey")
    ax.patch.set_linewidth(0.8)

    # Line + scatter per panel (same color across all panels)
    ax.plot(x_data, y_data, color=pal[5], linewidth=2, zorder=3)
    ax.scatter(x_data, y_data, color=pal[5], s=40, zorder=4,
               edgecolors="white", linewidths=0.8)

    # Annotate first and last values
    ax.text(x_first, y_first, f"{y_first:.1f}", fontsize=8,
            color="dimgrey", ha="right", va="center")
    ax.text(x_last, y_last, f"{y_last:.1f}", fontsize=8,
            color="dimgrey", ha="left", va="center")

    ax.set_title(r"$\bf{(" + label + r")}$" + f"  {title}", loc="left", fontsize=11, pad=7)

    # Axis labels: left column gets y-label, bottom row gets x-label
    if col == 0:
        ax.set_ylabel("Y Label", fontsize=9, labelpad=6, color="dimgrey")
    if row == 2:
        ax.set_xlabel("X Label", fontsize=9, labelpad=6, color="dimgrey")

sns.despine(left=True, bottom=True)
```

**Rules:**
- Grid dimension order: rows first, columns second. `GridSpec(3, 2)` = 3 rows × 2 columns.
- Single line color `pal[5]` across all panels — do not use per-panel colors or per-group colors
- Include scatter dots on data points (`s=40`, `edgecolors="white"`, `linewidths=0.8`) — do not use `fill_between`
- Annotate first and last values per panel (`fontsize=8`, `color="dimgrey"`) — do not add "yrs" or unit suffixes to annotations
- Share y-axis limits across all panels when showing the same metric (set `set_ylim` identically)
- Axis labels: left column panels get `set_ylabel`, bottom row panels get `set_xlabel` — other panels omit these labels
- Suptitle: `fontsize=14`, centered above the grid — do not add `color="dimgrey"` to suptitle (keep default black for the main title)
- `wspace=0.3, hspace=0.5` — adjust for readability but keep consistent spacing

**Customize:** Adjust GridSpec dimensions for different layouts (2x2, 3x3). For prediction plots, add `ax.scatter(x, y_pred, alpha=0.4, c="grey", s=2)` and metric annotation box. Remove `ax.patch.set_edgecolor/linewidth` if panel borders are not desired.

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
