# Multi-Panel Grid (GridSpec)

**Use for:** small multiples — the same metric across groups or conditions (2x2, 3x2, 3x3), or related views of the same data.
**Exemplars:** `exemplars/P8-a.png` (4 diets, 2x2) and `exemplars/P8-b.png` (5 continents, 3x2 with the 6th cell hidden). Fixed: lightgrey panel frames, bold (a)–(f) labels, outer-edge axis labels, shared y. Varies: grid shape, grey context lines, subtitle.
**Layout:** `gridspec.GridSpec(rows, cols)` with at least 2 columns; a "3x2 grid" is 3 rows × 2 columns. Prefer balanced grids over N×1 stacks or 1×N strips, which make panels squat. For 5 items use 3x2 and hide the 6th cell.

```python
from matplotlib import gridspec
import matplotlib.patheffects as pe

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data: drop missing values only in the plotted columns ---
df = pd.read_csv("data.csv").dropna(subset=["group", "x", "y"])
groups = sorted(df["group"].unique())
# one summary line per panel (the mean across raw series); raw series stay as context
mean = {g: df[df["group"] == g].groupby("x")["y"].mean() for g in groups}

# --- Single color for all panels (same metric across groups) ---
line_color = sns.cubehelix_palette(6, rot=-0.25, light=0.7)[5]
HALO = [pe.withStroke(linewidth=3, foreground="white")]

# --- Grid from the group count: 2x2 for ≤4, 3x2 for 5-6, 3x3 for 7-9 ---
n_rows, n_cols = (2, 2) if len(groups) <= 4 else (3, 2) if len(groups) <= 6 else (3, 3)
grid_figsize = {(2, 2): (10, 8), (3, 2): (14, 9), (3, 3): (14, 12)}
hspace = {(2, 2): 0.30, (3, 2): 0.35, (3, 3): 0.40}[(n_rows, n_cols)]

fig = plt.figure(figsize=grid_figsize[(n_rows, n_cols)], dpi=150)
gs = gridspec.GridSpec(n_rows, n_cols)
gs.update(wspace=0.08, hspace=hspace, left=0.08, right=0.97, top=0.88, bottom=0.07)
axes_list = [fig.add_subplot(gs[i, j]) for i in range(n_rows) for j in range(n_cols)]
fig.suptitle("Main Title", fontsize=15, x=0.08, y=0.995, ha="left",
             color="dimgrey", weight="semibold")

# Shared limits: compute global ranges BEFORE the loop
y_lo, y_hi = df["y"].min(), df["y"].max()
y_pad = (y_hi - y_lo) * 0.08
x_lo, x_hi = df["x"].min(), df["x"].max()

end_values = {}
for i, ax in enumerate(axes_list):
    if i >= len(groups):
        ax.set_visible(False)  # unused cell
        continue
    g = groups[i]
    row, col = divmod(i, n_cols)
    s = mean[g]

    ax.grid(False)
    ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
    ax.patch.set_edgecolor("lightgrey")
    ax.patch.set_linewidth(0.8)

    # Context: other groups' means in light grey; this group's mean on top
    for other in groups:
        if other != g:
            ax.plot(mean[other].index, mean[other].values, color="#d9d9d9", linewidth=1, zorder=1)
    ax.plot(s.index, s.values, color=line_color, linewidth=2.2, zorder=3)
    ax.scatter(s.index[-1], s.values[-1], color=line_color, s=36, zorder=4,
               edgecolors="white", linewidths=0.8)

    # End label to the right of the last point, in the margin reserved by xlim
    t = ax.annotate(f"{s.values[-1]:,.0f}", xy=(s.index[-1], s.values[-1]), xytext=(6, 0),
                    textcoords="offset points", ha="left", va="center",
                    fontsize=9, color="dimgrey", weight="semibold")
    t.set_path_effects(HALO)
    end_values[g] = s.values[-1]

    ax.set_xlim(x_lo, x_hi + (x_hi - x_lo) * 0.12)
    ax.set_ylim(y_lo - y_pad, y_hi + y_pad)
    ax.set_title(r"$\bf{(" + chr(ord("a") + i) + r")}$" + f"  {g}", loc="left",
                 fontsize=11, pad=7, color="dimgrey")

    # Axis labels: left column gets y-label, bottom row of used panels gets x-label
    if col == 0:
        ax.set_ylabel("Y Label (units)", fontsize=10, labelpad=6, color="dimgrey")
    else:
        ax.tick_params(labelleft=False)  # shared y: hide redundant tick labels
    if i + n_cols >= len(groups):
        ax.set_xlabel("X Label (units)", fontsize=10, labelpad=6, color="dimgrey")
    else:
        ax.tick_params(labelbottom=False)

# --- Cross-panel takeaway as a subtitle under the suptitle (computed from data) ---
best = max(end_values, key=end_values.get)
worst = min(end_values, key=end_values.get)
fig.text(0.08, 0.955, f"{best} ends highest ({end_values[best]:,.0f}), "
         f"{end_values[best] / end_values[worst]:.1f}x {worst} ({end_values[worst]:,.0f})",
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
- Many raw series per panel (e.g. one line per subject): draw them thin and grey (`alpha≈0.3`) and overlay the group mean in `line_color` — the mean is what the reader compares. Say "mean of n chicks" (or similar) in the subtitle or y-label, and note attrition when groups lose members over x.
- When N items don't fit a standard grid, round up: 3-4 → 2x2, 5-6 → 3x2, 7-9 → 3x3. Hide extras with `ax.set_visible(False)`. Prefer balanced multi-column grids over Nx1 vertical stacks.
- **Spacing:** `wspace=0.08` keeps columns tight — do not exceed 0.12. Right-column panels omit y-tick labels when y-axis is shared (`ax.tick_params(labelleft=False)`) so the gap can be narrow. Use `hspace=0.30` for 2x2, `hspace=0.35` for 3x2, `hspace=0.40` for 3x3. Do not inflate hspace beyond these values.
- **Figure margins:** `left=0.08, right=0.97, top=0.88, bottom=0.07`. `top=0.88` leaves room for the suptitle and the takeaway line; raise it to ~0.93 if there is no takeaway line. Check spacing with the checker and by eye — the suptitle should sit close to, but not touch, the first row's titles.
- Scale `figsize` for panel count and content density: `(10, 8)` for 2x2, `(14, 9)` for 3x2, `(14, 12)` for 3x3. Template values are starting points.
- Use `fill_between`, `axvline`/`axhline`, or reference lines when they help communicate the data (e.g., confidence intervals, thresholds, baselines).
- Panel content varies: use horizontal bars, violins, scatter, or line+scatter per panel as appropriate — keep a single y-axis per panel (no twinx/dual-axis). When a panel would contain more than 8–10 items (bars, lines, categories), filter to top-N or aggregate to keep the panel readable.
- Label the end value of each panel's main line (the comparison point); skip start values when every panel starts at the same place. Put end labels to the right of the last point, in a margin reserved with `set_xlim` (as in the template), with a white halo — never on top of the lines.
- Show the other groups as light grey context lines behind each panel's own line (style-reference Craft, "highlight one, grey the rest"): the reader compares without flicking between panels.
- State the cross-panel finding in the line under the suptitle (which group is highest, steepest, most variable). Compute it from the data. Panel-level callouts go at the data with `ax.annotate`.

**Customize:** For prediction plots, add `ax.scatter(x, y_pred, alpha=0.4, c="grey", s=2)` and metric annotation box. Remove `ax.patch.set_edgecolor/linewidth` if panel borders are not desired.
