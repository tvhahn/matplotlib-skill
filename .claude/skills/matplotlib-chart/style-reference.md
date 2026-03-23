# Style Reference

Complete aesthetic specification for Tim's publication-quality matplotlib/seaborn charts.
Claude reads this file as reference material when generating chart code.

## Identity vs. Defaults

This spec distinguishes two kinds of values:

**Identity tokens (immutable)** — these define the visual signature and must not change:
- Palette hex codes and family assignments (Blues_d, RdBu_r, DIVERGING_COLORBLIND, cubehelix, etc.)
- Font family: DejaVu Sans
- Despine convention: `sns.despine(left=True, bottom=True)`
- Annotation color: `"dimgrey"`
- Legend frame: `frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey"`
- Tick styling: `length=0, labelcolor="dimgrey"`
- DPI: 150 standard / 300 publication
- Save format: PDF+PNG with `bbox_inches="tight"`
- Panel frame (when used): `ax.patch` with `edgecolor="lightgrey"`, `linewidth=0.8`

**Default values (flexible)** — these appear in templates as good starting points but should adapt to data properties:
- `fontsize` on titles, labels, annotations — scale with figure size and content density
- `alpha` on overlapping elements — adjust for data density
- `figsize` tuples — scale for category count, label length, panel count
- `pad`, `labelpad`, `wspace`, `hspace` — adjust for content spacing needs
- `DOT_SIZE`, `linewidth`, `s` — scale for data volume and figure size
- Format strings (`f"{value:.1f}"`, `f"{value:,.0f}"`) — match data type and precision

When a pattern template shows a specific numeric value (e.g., `fontsize=14`, `alpha=0.55`, `DOT_SIZE=150`), treat it as a sensible default, not an immutable constraint. Adapt based on data properties, figure size, and content density. Only values listed in a pattern's **Signature** section define the visual identity.

## Invariants Shorthand

Pattern files say "Apply style-reference invariants" instead of repeating these.
Every chart MUST include:

1. `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")`
2. `sns.despine(left=True, bottom=True)`
3. `dpi=150` (300 only on explicit publication request)
4. `bbox_inches="tight"` on every `savefig`; PDF+PNG dual save
5. Legend frame: `frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey"`
6. Annotation color: `"dimgrey"`
7. Tick styling: `ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")`
8. Data: read from CSV/NPZ; apply `df.dropna()` after loading

## Base Configuration

Always inline this style setup block at the top of the plotting section:

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
```

Then override with per-axes cleanup (despine, grid off, tick marks off) as shown below.

## Color Palettes

### DIVERGING_COLORBLIND
```python
["#d73027", "#fc8d59", "#fee090", "#4575b4"]
# redish, orangeish, yellowish, blueish
```
**Use for:** Comparisons, predicted-vs-actual, classification boundaries, multi-class overlays.
Source: ColorBrewer RdYlBu diverging, confirmed colorblind-safe.

### CUBEHELIX_6
```python
pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)
# Hex: ['#90c1c6', '#72a5b4', '#58849f', '#446485', '#324465', '#1f253f']
```
**Use for:** General sequential data, line plots, lollipop charts, PR/ROC curves.
Access individual colors with `pal[3]` (medium), `pal[5]` (darkest).

### GREYSCALE
```python
pal = sns.color_palette("Greys_r")
```
**Use for:** Monochromatic bar charts, neutral backgrounds.
Pair with `ACCENT_RED` for selective emphasis on one bar.

### BLUES_D
```python
palette="Blues_d"
```
**Use for:** Ranked/percentage horizontal bar charts. Pass directly to seaborn `palette=` parameter.

### ROCKET
```python
palette="rocket"
```
**Use for:** Vertical bar charts showing ranked scores. Not for correlation heatmaps (use `RdBu_r` instead).

### RdBu_r
```python
cmap="RdBu_r"
```
**Use for:** Correlation heatmaps. Diverging palette — positive correlations show red/warm, negative show blue/cool. Always pair with `vmin=-1, vmax=1, center=0`.

### INFERNO
```python
cmap="inferno"
```
**Use for:** Spectrograms, heatmaps via `pcolormesh`. Pass to `cmap=` parameter.

### ACCENT_RED
```python
"#bd0c0c"
```
**Use for:** Selective emphasis on a single bar or element among otherwise grey/neutral items.

### TRAFFIC_LIGHT
```python
["#33a02c", "#fdbf6f", "#e31a1c"]
# green, amber, red
```
**Use for:** Pass/warn/fail status indicators, threshold-based coloring.

## Spine & Grid Rules

Remove all spines and grid by default, then selectively re-enable:

```python
sns.despine(left=True, bottom=True)
ax.grid(False)
```

When a single-axis grid improves readability (e.g., bar charts):
```python
ax.grid(alpha=0.7, linewidth=1, axis="x")  # horizontal bars (omit when value labels are present)
ax.grid(alpha=0.7, linewidth=1, axis="y")  # vertical bars
```

For horizontal bar charts with value labels, disable grid but add a baseline:
```python
ax.axvline(x=0, color="lightgrey", linewidth=0.8, zorder=0)  # anchors bar origins
ax.grid(False)
```

For spectrograms/heatmaps, also remove the right spine:
```python
sns.despine(left=True, bottom=True, right=True)
```

### Panel Frames

A subtle rectangular border around an axes background patch. This frames the
chart visually without re-enabling axis spines:

```python
for ax in axes_list:
    ax.patch.set_edgecolor("lightgrey")
    ax.patch.set_linewidth(0.8)
```

Apply **after** `sns.despine()`. Spines remain removed; the border comes from
the axes background patch, not the spine objects.

**When to use a frame:**
- Multi-panel layouts (always — frames separate panels visually)
- Charts where data floats in the coordinate space without touching the edges (curves, violin shapes, scatter clouds)
- Charts with bounded semantic axes (e.g., 0–1 probability ranges)

**When to omit a frame:**
- Bar charts (bars anchor to a baseline, creating their own visual edge)
- Lollipop charts (lines span the chart width, creating horizontal structure)
- Heatmaps (the cell grid creates its own visual boundary)
- Any chart where data elements fill the plot area

The pattern's Guidance section provides chart-type-specific recommendations. When not specified, omit the frame (the existing default).

## Typography

- **Font family:** DejaVu Sans (set via `sns.set_theme(font="DejaVu Sans")`)
- **Title size:** 12-16pt depending on figure complexity
- **Axis label size:** 12-14pt
- **Annotation text color:** `"dimgrey"` -- used for value labels, descriptions, score annotations
- **Annotation weight:** `"medium"` or `"semibold"` for values, `"normal"` for descriptions
- **LaTeX notation:** Use raw strings for math: `r"$R^2$"`, `r"$\bf{(a)}$"`

## Figure Sizing Lookup

| Chart Type | figsize | Notes |
|---|---|---|
| Single bar chart | (4, 7) | Narrow, tall for horizontal bars |
| Side-by-side bars (2 panel) | (14, 7) | Wide for comparison |
| Correlation bars (stacked 2 panel) | (10, 12) | Tall for stacked vertical |
| Violin + strip (2 panel) | (12, 5) | Wide, short |
| Time series (2x2 grid) | (11, 8) | Square-ish |
| Time series (3x3 grid) | (14, 12) | Large square |
| Spectrogram (1x2) | (11, 4) | Wide, short |
| PR/ROC curves (1x2) | (12, 6) | Wide, moderate height |
| Lollipop chart | (10, 6) | Moderate |
| Decision boundary | (8, 6) | Moderate with aspect=1 |
| Simple single panel | (10, 6) | General default |

## Saving Convention

Always save with tight bounding box.

**Standard render** (default):
```python
plt.savefig("./figures/chart_name.pdf", dpi=150, bbox_inches="tight")
plt.savefig("./figures/chart_name.png", dpi=150, bbox_inches="tight")
```

**Publication render** (only when user explicitly requests "publication", "300 DPI", or "high resolution"):
```python
plt.savefig("./figures/chart_name.pdf", dpi=300, bbox_inches="tight")
plt.savefig("./figures/chart_name.png", dpi=300, bbox_inches="tight")
```

**Exploratory render** (user says "quick plot"):
```python
plt.savefig("./figures/chart_name.png", dpi=150, bbox_inches="tight")
```

## Legend Convention

```python
ax.legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
          labelcolor="dimgrey", bbox_to_anchor=(0.6, 1.05), ncol=2, fontsize="x-large")
```

- **Always:** `frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey"` (white box with subtle outline)
- **Text color:** `labelcolor="dimgrey"` inline in the legend constructor (requires mpl>=3.3)
- **Position:** `bbox_to_anchor` for outside placement, or `loc="lower right"` / `loc="upper left"` for inside

## Subplot Convention

### Bold letter prefixes in titles
```python
ax.set_title(r"$\bf{(a)}$" + " Description Here", loc="left", fontsize=12)
```

Use counter-based generation for grids:
```python
labels = [chr(ord('a') + i) for i in range(n_panels)]
# produces: ['a', 'b', 'c', ...]
```

### GridSpec for complex layouts
```python
from matplotlib import gridspec

fig = plt.figure(figsize=(14, 12), dpi=150)
gs = gridspec.GridSpec(3, 3)
ax1 = plt.subplot(gs[0, 0])
# ...
# Adjust wspace/hspace for content density — no single "right" value
gs.update(wspace=0.3, hspace=0.4)
```

### Title padding
```python
ax.set_title("Title", pad=7)
```

## Annotation Patterns

### Value labels on bar ends
```python
for p in ax.patches:
    space = 0.5
    _x = p.get_x() + p.get_width() + space
    _y = p.get_y() + p.get_height() / 2
    value = p.get_width()
    ax.text(_x, _y, f"{value:.1f} %", ha="left", va="center",
            weight="semibold", size=12)
```

### Metric text box (RMSE/R2)
```python
x_min, x_max = ax.get_xlim()
y_min, y_max = ax.get_ylim()
print_text = f"RMSE = {rmse:.3f}\n$R^2$ = {r2:.3f}"
ax.text(
    (x_max - x_min) * 0.03 + x_min,
    y_max - (y_max - y_min) * 0.05,
    print_text,
    fontsize=9, fontweight="normal",
    verticalalignment="top", horizontalalignment="left",
    bbox={"facecolor": "gray", "alpha": 0.0, "pad": 6},
)
```

### Supporting visual elements
Use `alpha=0.4` for scatter points, background lines, and other non-primary elements:
```python
ax.scatter(x, y, alpha=0.4, c="grey", edgecolors="none", s=2)
```

### Remove tick marks and soften tick labels
```python
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
```

The `labelcolor="dimgrey"` keeps tick labels consistent with annotations and legend text. Apply to all patterns.
