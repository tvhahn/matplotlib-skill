# Multi-Panel Grid (GridSpec)

**When to use:** 2x2, 3x2, 3x3, or irregular layouts showing the same metric across different datasets/conditions, or different but related views of the same data.
**Layout:** Use `gridspec.GridSpec(rows, cols)` — rows first. A "3x2 grid" means 3 rows × 2 columns. You may also use `plt.subplots()` for regular grids.
**Line color:** Default to `pal[5]` (darkest cubehelix) for line+scatter panels showing the same metric — consistent color emphasizes that the metric is identical across panels.

```python
from matplotlib import gridspec

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data: always call .dropna() to handle missing values ---
df = pd.read_csv("data.csv").dropna()

# --- Palette: pal[5] for all panels (same metric across groups) ---
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

**Rules (identity):**
1. Grid dimension order: rows first, columns second. `GridSpec(3, 2)` = 3 rows × 2 columns.
2. Default color is `pal[5]` for all panels. Share y-axis limits when panels show the same metric (compute global min/max before the loop).
3. Subplot outlines: `ax.patch.set_edgecolor("lightgrey")`, `ax.patch.set_linewidth(0.8)`.
4. `ax.grid(False)` on every panel.
5. Axis labels: left column panels get `set_ylabel`, bottom row panels get `set_xlabel` — other panels omit these.
6. Panel labels: counter-based `chr(ord('a') + i)` with bold prefix.
7. When N items don't fit a standard grid, round up: 3-4 → 2x2, 5-6 → 3x2, 7-9 → 3x3. Hide extras with `ax.set_visible(False)`.
8. Always use `dpi=150`. Save PDF+PNG with `bbox_inches="tight"`.

**Adapt when:**
- Panel content varies: use horizontal bars, violins, scatter, or line+scatter per panel as appropriate — keep a single y-axis per panel (no twinx/dual-axis). The grid layout is the pattern's identity, not the panel content type.
- Scale `figsize` and spacing (`wspace`/`hspace`) for panel count and content density: `(10, 8)` for 2x2, `(14, 9)` for 3x2, `(14, 12)` for 3x3.
- Annotate first/last values by default for trends; omit for bar-type panels.
- Use per-panel colors only when the user explicitly requests it or panels display fundamentally incomparable metrics (e.g., temperature vs. pressure on different y-axes). Default to `pal[5]`.

**Customize:** For prediction plots, add `ax.scatter(x, y_pred, alpha=0.4, c="grey", s=2)` and metric annotation box. Remove `ax.patch.set_edgecolor/linewidth` if panel borders are not desired.
