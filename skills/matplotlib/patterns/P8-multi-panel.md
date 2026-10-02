# Multi-Panel Grid (GridSpec)

**Use for:** small multiples — the same metric across groups or conditions (2x2, 3x2, 3x3), or related views of the same data.
**Layout:** `gridspec.GridSpec(rows, cols)` with at least 2 columns; a "3x2 grid" is 3 rows × 2 columns. Prefer balanced grids over N×1 stacks or 1×N strips, which make panels squat. For 5 items use 3x2 and hide the 6th cell.

```python
from matplotlib import gridspec

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data: drop missing values only in the plotted columns ---
df = pd.read_csv("data.csv").dropna(subset=["group", "x", "y"])

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
          left=0.08, right=0.99, top=0.89, bottom=0.07)
axes_list = [plt.subplot(gs[i, j]) for i in range(n_rows) for j in range(n_cols)]
fig.suptitle("Main Title", fontsize=15, x=0.08, y=0.995, ha="left",
             color="dimgrey", weight="semibold")

# Shared y-axis: compute global limits BEFORE the loop
y_global_min = all_values.min()
y_global_max = all_values.max()
y_pad = (y_global_max - y_global_min) * 0.1

n_panels = n_rows * n_cols
labels = [chr(ord('a') + i) for i in range(n_panels)]
titles = ["Dataset 1", "Dataset 2", "Dataset 3", "Dataset 4", "Dataset 5", "Dataset 6"]

end_values = {}
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

    # Label the end value (the comparison point), nudged up-left to stay inside the panel
    ax.annotate(f"{y_last:,.0f}", xy=(x_last, y_last), xytext=(-4, 6),
                textcoords="offset points", ha="right", va="bottom",
                fontsize=9, color="dimgrey", weight="semibold")
    end_values[title] = y_last

    ax.set_ylim(y_global_min - y_pad, y_global_max + y_pad)
    ax.set_title(r"$\bf{(" + label + r")}$" + f"  {title}", loc="left", fontsize=11, pad=7,
                 color="dimgrey")

    # Axis labels: left column gets y-label, bottom row gets x-label
    if col == 0:
        ax.set_ylabel("Y Label", fontsize=9, labelpad=6, color="dimgrey")
    else:
        ax.tick_params(labelleft=False)  # hide redundant y-ticks on right column
    if row == n_rows - 1:
        ax.set_xlabel("X Label", fontsize=9, labelpad=6, color="dimgrey")

# --- Cross-panel takeaway as a subtitle under the suptitle (computed from data) ---
best = max(end_values, key=end_values.get)
worst = min(end_values, key=end_values.get)
fig.text(0.08, 0.955, f"{best} ends highest ({end_values[best]:,.0f}), "
         f"{end_values[best] / end_values[worst]:.1f}x {worst}",
         ha="left", va="top", fontsize=10.5, color="dimgrey")

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
- Many raw series per panel (e.g. one line per subject): draw them thin and grey (`alpha≈0.3`) and overlay the group mean in `line_color` — the mean is what the reader compares.
- When N items don't fit a standard grid, round up: 3-4 → 2x2, 5-6 → 3x2, 7-9 → 3x3. Hide extras with `ax.set_visible(False)`. Prefer balanced multi-column grids over Nx1 vertical stacks.
- **Spacing:** `wspace=0.08` keeps columns tight — do not exceed 0.12. Right-column panels omit y-tick labels when y-axis is shared (`ax.tick_params(labelleft=False)`) so the gap can be narrow. Use `hspace=0.30` for 2x2, `hspace=0.35` for 3x2, `hspace=0.40` for 3x3. Do not inflate hspace beyond these values.
- **Figure margins:** `left=0.08, right=0.99, top=0.89, bottom=0.07`. `top=0.89` leaves room for the suptitle and the takeaway line; raise it to ~0.93 if there is no takeaway line. Check spacing with the checker and by eye — the suptitle should sit close to, but not touch, the first row's titles.
- Scale `figsize` for panel count and content density: `(10, 8)` for 2x2, `(14, 9)` for 3x2, `(14, 12)` for 3x3. Template values are starting points.
- Use `fill_between`, `axvline`/`axhline`, or reference lines when they help communicate the data (e.g., confidence intervals, thresholds, baselines).
- Panel content varies: use horizontal bars, violins, scatter, or line+scatter per panel as appropriate — keep a single y-axis per panel (no twinx/dual-axis). When a panel would contain more than 8–10 items (bars, lines, categories), filter to top-N or aggregate to keep the panel readable.
- Label the end value of each panel's main line (the comparison point); skip start values when every panel starts at the same place. Keep end labels inside the panel (`ha="right"` with a left offset near the right edge).
- State the cross-panel finding in the line under the suptitle (which group is highest, steepest, most variable). Compute it from the data. Panel-level callouts go at the data with `ax.annotate`.

**Customize:** For prediction plots, add `ax.scatter(x, y_pred, alpha=0.4, c="grey", s=2)` and metric annotation box. Remove `ax.patch.set_edgecolor/linewidth` if panel borders are not desired.
