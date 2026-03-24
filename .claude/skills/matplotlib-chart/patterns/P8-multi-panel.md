# Multi-Panel Grid (GridSpec)

**When to use:** 2x2, 3x2, 3x3, or irregular layouts showing the same metric across different datasets/conditions, or different but related views of the same data.
**Layout:** Always use `gridspec.GridSpec(rows, cols)` with at least 2 columns. A "3x2 grid" means 3 rows × 2 columns. Never create single-column layouts — no `GridSpec(N, 1)`, no `plt.subplots(N, 1)`, no Nx1 grids. For 5 items use `GridSpec(3, 2)` and hide the 6th panel.
**Line color:** Default to `pal[5]` (darkest cubehelix) for line+scatter panels showing the same metric — consistent color emphasizes that the metric is identical across panels.

```python
from matplotlib import gridspec

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data: always call .dropna() to handle missing values ---
df = pd.read_csv("data.csv").dropna()

# --- Single color for all panels (same metric across groups) ---
line_color = sns.cubehelix_palette(6, rot=-0.25, light=0.7)[5]

# --- Dynamic grid dimensions and figsize ---
n_rows, n_cols = 3, 2  # derive from data: 2x2 for ≤4, 3x2 for 5-6, 3x3 for 7-9
grid_figsize = {(2, 2): (10, 8), (3, 2): (14, 9), (3, 3): (14, 12), (2, 3): (14, 8)}
fig_w, fig_h = grid_figsize.get((n_rows, n_cols), (14, 9))
hspace_map = {2: 0.30, 3: 0.35}

fig = plt.figure(figsize=(fig_w, fig_h), dpi=150)
gs = gridspec.GridSpec(n_rows, n_cols)
gs.update(wspace=0.08, hspace=hspace_map.get(n_rows, 0.35),
          left=0.08, right=0.99, top=0.93, bottom=0.07)
axes_list = [plt.subplot(gs[i, j]) for i in range(n_rows) for j in range(n_cols)]
fig.suptitle("Main Title", fontsize=14, y=0.98, color="dimgrey")

# Shared y-axis: compute global limits BEFORE the loop
y_global_min = all_values.min()
y_global_max = all_values.max()
y_pad = (y_global_max - y_global_min) * 0.1

n_panels = n_rows * n_cols
labels = [chr(ord('a') + i) for i in range(n_panels)]
titles = ["Dataset 1", "Dataset 2", "Dataset 3", "Dataset 4", "Dataset 5", "Dataset 6"]

for i, (ax, label, title) in enumerate(zip(axes_list, labels, titles)):
    row, col = divmod(i, n_cols)

    ax.grid(False)
    ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")

    # --- subplot outline (frames each panel) ---
    ax.patch.set_edgecolor("lightgrey")
    ax.patch.set_linewidth(0.8)

    # Line + scatter per panel (same color across all panels)
    ax.plot(x_data, y_data, color=line_color, linewidth=2, zorder=3)
    ax.scatter(x_data, y_data, color=line_color, s=40, zorder=4,
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
    else:
        ax.tick_params(labelleft=False)  # hide redundant y-ticks on right column
    if row == n_rows - 1:
        ax.set_xlabel("X Label", fontsize=9, labelpad=6, color="dimgrey")

# --- Figure-level insight annotation ---
# Compute a summary finding across all panels (e.g., highest peak, steepest trend)
fig.text(0.99, 0.01, "Panel (c) shows the steepest growth (+42%)",
         ha="right", va="bottom", fontsize=9, color="dimgrey", style="italic")

sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Grid dimension order: rows first, columns second. `GridSpec(3, 2)` = 3 rows × 2 columns.
- Subplot outlines: `ax.patch.set_edgecolor("lightgrey")`, `ax.patch.set_linewidth(0.8)`.
- Panel labels: counter-based `chr(ord('a') + i)` with bold prefix.
- Axis labels: left column panels get `set_ylabel`, bottom row panels get `set_xlabel` — other panels omit these.

**Guidance:**
- Default to single `line_color` (cubehelix darkest `pal[5]`) when panels show the same metric (same y-axis unit). Use per-panel colors when panels display different metrics or when color encodes a meaningful category.
- Default shared y-axis limits for same metric (compute global min/max before the loop). Use independent y-axes when panels show different metrics or scales.
- `ax.grid(False)` on every panel.
- When N items don't fit a standard grid, round up: 3-4 → 2x2, 5-6 → 3x2, 7-9 → 3x3. Hide extras with `ax.set_visible(False)`. Prefer balanced multi-column grids over Nx1 vertical stacks.
- **Spacing:** `wspace=0.08` keeps columns tight — do not exceed 0.12. Right-column panels omit y-tick labels when y-axis is shared (`ax.tick_params(labelleft=False)`) so the gap can be narrow. Use `hspace=0.30` for 2x2, `hspace=0.35` for 3x2, `hspace=0.40` for 3x3. Do not inflate hspace beyond these values.
- **Figure margins:** `left=0.08, right=0.99, top=0.93, bottom=0.07`. The `right=0.99` pushes the right column panels flush against the figure edge. Combined with `bbox_inches="tight"`, this eliminates dead space on the right. `top=0.93` reserves suptitle space; `bottom=0.07` reserves insight annotation space.
- Scale `figsize` for panel count and content density: `(10, 8)` for 2x2, `(14, 9)` for 3x2, `(14, 12)` for 3x3. Template values are starting points.
- Use `fill_between`, `axvline`/`axhline`, or reference lines when they help communicate the data (e.g., confidence intervals, thresholds, baselines).
- Panel content varies: use horizontal bars, violins, scatter, or line+scatter per panel as appropriate — keep a single y-axis per panel (no twinx/dual-axis). When a panel would contain more than 8–10 items (bars, lines, categories), filter to top-N or aggregate to keep the panel readable.
- Annotate first/last values by default for trends; omit for bar-type panels.
- Always add a figure-level insight annotation (`fig.text()`) that highlights a cross-panel finding (e.g., "Panel (c) shows the steepest growth"). Compute the finding dynamically from data — do not hardcode.

**Customize:** For prediction plots, add `ax.scatter(x, y_pred, alpha=0.4, c="grey", s=2)` and metric annotation box. Remove `ax.patch.set_edgecolor/linewidth` if panel borders are not desired.
