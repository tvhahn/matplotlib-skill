# Multi-Panel Grid (GridSpec)

**When to use:** 2x2, 3x2, 3x3, or irregular layouts showing same metric across different datasets/conditions.
**Layout:** Always use `gridspec.GridSpec(rows, cols)` — rows first. A "3x2 grid" means 3 rows × 2 columns.
**Line color:** Use a single color `pal[5]` (darkest cubehelix) for the line across all panels — do not vary color per panel. All panels show the same metric, so color should be consistent.
**Figsize:** `(10, 8)` for 2x2, `(14, 9)` for 3x2, `(14, 12)` for 3x3. Always use `dpi=150`.

```python
from matplotlib import gridspec

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

fig = plt.figure(figsize=(14, 9), dpi=150)
gs = gridspec.GridSpec(3, 2)
axes_list = [plt.subplot(gs[i, j]) for i in range(3) for j in range(2)]
gs.update(wspace=0.3, hspace=0.5)
fig.suptitle("Main Title", fontsize=14, y=0.98)

# Shared y-axis: compute global limits BEFORE the loop
y_global_min = all_values.min()
y_global_max = all_values.max()
y_pad = (y_global_max - y_global_min) * 0.1

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

    ax.set_ylim(y_global_min - y_pad, y_global_max + y_pad)
    ax.set_title(r"$\bf{(" + label + r")}$" + f"  {title}", loc="left", fontsize=11, pad=7)

    # Axis labels: left column gets y-label, bottom row gets x-label
    if col == 0:
        ax.set_ylabel("Y Label", fontsize=9, labelpad=6, color="dimgrey")
    if row == 2:
        ax.set_xlabel("X Label", fontsize=9, labelpad=6, color="dimgrey")

sns.despine(left=True, bottom=True)
```

**Rules:**
1. Grid dimension order: rows first, columns second. `GridSpec(3, 2)` = 3 rows × 2 columns.
2. SINGLE line color `pal[5]` for ALL panels — never `pal[i]`, never per-panel/per-group colors. Every `ax.plot()` and `ax.scatter()` call must use `color=pal[5]`.
3. Every panel MUST have `ax.scatter(...)` dots on data points (`s=40`, `edgecolors="white"`, `linewidths=0.8`, `zorder=4`). Do NOT use `fill_between`, SEM shading, area fills, error bands, or bar charts.
4. Annotate BOTH first AND last values per panel with `ax.text(...)` — `fontsize=8`, `color="dimgrey"`. Format as plain number (`f"{val:.1f}"`) — no `$`, `%`, unit suffixes, or "Peak:" labels. No arrows or `ax.annotate()`.
5. `ax.grid(False)` on every panel — do NOT add back any grid lines (no `yaxis.grid()`, no `xaxis.grid()`).
6. Share y-axis limits across all panels: compute global min/max BEFORE the loop, then call `ax.set_ylim(y_global_min, y_global_max)` in every panel.
7. Axis labels: left column panels get `set_ylabel`, bottom row panels get `set_xlabel` — other panels omit these labels.
8. Suptitle: `fontsize=14`, centered above the grid — do not add `color="dimgrey"` to suptitle (keep default black for the main title).
9. `gs.update(wspace=0.3, hspace=0.5)` — these are starting defaults. Adjust during Phase 5 visual review if gaps between panels or between suptitle and panels look excessive.
10. Figsize by layout: `(10, 8)` for 2x2, `(14, 9)` for 3x2, `(14, 12)` for 3x3. Do not invent other sizes.
11. Do NOT use `ax.annotate()` with arrows, "Peak:" labels, or `axvline`/`axhline` reference lines. Only `ax.text()` for first/last annotations.
12. Do NOT add per-event/per-category color schemes (e.g., blue for "cue", red for "stim"). All panels use `pal[5]`.
13. ALWAYS use `gridspec.GridSpec` — never `plt.subplots()` or `fig.add_subplot()`. This pattern requires GridSpec for all layouts.
14. When N items don't fit a standard grid, round up: 3-4 items → 2x2, 5-6 items → 3x2, 7-9 items → 3x3. Leave extra panels empty (hide with `ax.set_visible(False)`).

**Customize:** For prediction plots, add `ax.scatter(x, y_pred, alpha=0.4, c="grey", s=2)` and metric annotation box. Remove `ax.patch.set_edgecolor/linewidth` if panel borders are not desired.
