# Style Reference

The aesthetic every chart follows. Read it before writing chart code.

## Contents
- Invariants (every chart)
- Identity vs. defaults
- Colour: choosing a palette, palette definitions
- Spines, grid, panel frames
- Typography, titles and takeaways
- Annotations
- Legends
- Multi-panel conventions
- Figure sizing
- Saving

## Invariants

Every chart includes these. Pattern files say "Apply style-reference invariants"
instead of repeating them.

1. `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")`
2. `sns.despine(left=True, bottom=True)` — all spines removed
3. `ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")`
4. All text other than data colours is `"dimgrey"`: title, axis labels, annotations, legend text, colorbar label and ticks
5. Legend frame: `frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey"`
6. `savefig(..., dpi=150, bbox_inches="tight")` to both PDF and PNG (300 DPI only on explicit publication request; PNG only for "quick"/"exploratory")
7. Data is read from the file and aggregated in code; missing values are dropped only in the plotted columns (`df.dropna(subset=[...])`)

## Identity vs. defaults

**Identity (keep):** the palette families and hex codes below, DejaVu Sans, the
despine convention, dimgrey text, the legend frame, zero-length ticks, 150/300 DPI,
PDF+PNG with tight bbox, and the lightgrey panel frame when one is used.

**Defaults (adapt):** font sizes, alpha, figsize, padding and spacing, marker and
line sizes, number formats. Template values are starting points; scale them to
category count, label length, value range, and point density. Only a pattern's
**Signature** items are fixed.

## Colour

### Choosing a palette

Match the palette to what colour encodes:

| Colour encodes | Use | Avoid |
|---|---|---|
| Nothing (one series) | One colour: `pal[3]` cubehelix, a mid `Blues_d` shade, or grey | Gradients that only repeat bar length |
| Emphasis on one or two items | Grey (`#bdbdbd`) for the rest + `ACCENT_RED` or `#4575b4` | Many saturated colours |
| Unordered categories (≤ 6) | `CATEGORICAL`, taken in order; add marker or line style from the 4th category on | Sequential palettes (cubehelix, rocket, Blues) — adjacent shades are indistinguishable |
| Ordered magnitude / rank | Sequential: cubehelix, `Blues_d`, `rocket` | — |
| Signed values around zero | Diverging: `RdBu_r` centred at 0, or red/blue from `DIVERGING_COLORBLIND` | — |

With more than six categories, colour stops working: highlight the few that matter
and grey the rest, facet (P8), or label directly. When a sequential palette's light
end nears white, trim it: `sns.color_palette("rocket", n + 2)[:n]`.

### Palette definitions

```python
DIVERGING_COLORBLIND = ["#d73027", "#fc8d59", "#fee090", "#4575b4"]  # red, orange, yellow, blue (ColorBrewer RdYlBu)
pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)
# ['#90c1c6', '#72a5b4', '#58849f', '#446485', '#324465', '#1f253f']; pal[3] medium, pal[5] darkest
CATEGORICAL = ["#d73027", "#4575b4", "#555555", "#fc8d59", "#91bfdb", "#1f253f"]
# red, blue, dark grey, orange, light blue, navy — ordered so the first 3 are maximally distinct
ACCENT_RED = "#bd0c0c"                    # emphasis on one element among grey
TRAFFIC_LIGHT = ["#33a02c", "#fdbf6f", "#e31a1c"]  # pass / warn / fail
# Named seaborn/matplotlib maps:
# "Blues_d"  ranked horizontal bars     "rocket"  ranked vertical bars, pivot heatmaps
# "RdBu_r"   correlation heatmaps (vmin=-1, vmax=1, center=0)
# "inferno"  spectrograms / pcolormesh   "Greys_r" monochrome bars
```

`#fee090` (yellow) is too light for thin lines or small markers on white; use it
only for filled areas or swap in `#555555`.

## Spines, grid, panel frames

Despine everything, then add back only what the reader needs:

```python
sns.despine(left=True, bottom=True)
ax.grid(False)                                  # default when values are labelled
ax.grid(axis="y", alpha=0.7, linewidth=1)       # value axis only, when no value labels
```

Horizontal bars with value labels: no grid, a baseline instead —
`ax.axvline(0, color="lightgrey", linewidth=0.8, zorder=0)`.
Spectrograms and heatmaps: `sns.despine(left=True, bottom=True, right=True)`.

**Panel frame** — a lightgrey border from the axes patch (spines stay off):

```python
ax.patch.set_edgecolor("lightgrey")
ax.patch.set_linewidth(0.8)
```

Use for multi-panel layouts, curves or point clouds that float in the plot area, and
bounded axes such as 0–1 probabilities. Omit for bars, lollipops, and heatmaps,
which define their own edges.

## Typography, titles and takeaways

- DejaVu Sans throughout (set by `sns.set_theme`)
- Title 12–16 pt, `loc="left"`, `color="dimgrey"`, `weight="semibold"`
- Axis labels 11–13 pt, dimgrey; include units: "Revenue ($M)"
- Value labels `"semibold"`/`"medium"`; descriptive text `"normal"`
- Math with raw strings: `r"$R^2$"`, panel labels `r"$\bf{(a)}$"`
- Escape literal dollar signs in any text as `\$` (`f"\${v:,.0f}"`): two unescaped `$` in one string switch on mathtext and render "$6 to $230" as italic "6to230"

**Title + subtitle.** The title names what is plotted ("On-Time Rate by
Airline"). When the chart has a clear takeaway, state it in a one-line subtitle
directly under the title, where the reader starts:

```python
ax.set_title("On-Time Rate by Airline", loc="left", fontsize=14,
             color="dimgrey", weight="semibold", pad=26)
ax.annotate("Only two airlines beat the 80% target; the worst misses it by 14 points",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8),
            textcoords="offset points", ha="left", va="bottom",
            fontsize=10.5, color="dimgrey")
```

Increase `pad` if the subtitle wraps to two lines. For multi-panel figures, put the
takeaway under `fig.suptitle` with `fig.text`, and check the spacing.

## Annotations

An annotation earns its place when it tells the reader something they would not
get from the marks and axis alone: a comparison ("3x"), a turning point, a record,
an outlier, a caveat. Place it **at the data it describes**:

```python
ax.annotate(f"Peak: {peak_val:,.0f} ({peak_year})", xy=(peak_year, peak_val), xytext=(-60, 10),
            textcoords="offset points", ha="right", fontsize=10, color="dimgrey",
            arrowprops=dict(arrowstyle="-", color="dimgrey", lw=0.8))
```

- Compute annotated values from the data; never type them in.
- One to three annotations per panel. If every mark is labelled, the reader cannot
  tell what matters.
- Don't restate a value that is already printed on a bar.
- Avoid a detached footer sentence in a figure corner; use the subtitle or put the
  note at the data.
- Supporting marks (raw points, fold curves, context lines): grey, `alpha≈0.4`.

**Value labels on bar ends** (horizontal bars):

```python
for p in ax.patches:
    ax.text(p.get_width() + pad, p.get_y() + p.get_height() / 2, f"{p.get_width():.1f}%",
            ha="left", va="center", weight="semibold", size=11, color="dimgrey")
```

`ax.bar_label(container, fmt=..., padding=3, color="dimgrey")` is equivalent and
handles grouped bars. Match format to data: `f"{v:,.0f}"` large integers,
`f"{v:.2f}"` small decimals, `$` for currency, `%` for rates.

**Metric box** (RMSE/R², AUC) in the top-left of a panel:

```python
ax.text(0.03, 0.95, f"RMSE = {rmse:.3f}\n$R^2$ = {r2:.3f}", transform=ax.transAxes,
        va="top", ha="left", fontsize=9, color="dimgrey")
```

## Legends

```python
ax.legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
          labelcolor="dimgrey", loc="upper left")
```

- Prefer direct labels (text at line ends, labels on bars) when there are few series;
  then drop the legend rather than showing both.
- Place the legend where it covers no data — an empty corner, or outside with
  `bbox_to_anchor`. A horizontal legend above the plot (`ncol=n`) works well for
  2–4 entries.
- Single-series charts need no legend.

## Multi-panel conventions

- Bold panel letters in titles: `ax.set_title(r"$\bf{(a)}$" + "  Description", loc="left", fontsize=12)`,
  generated with `chr(ord("a") + i)`.
- `gridspec.GridSpec(rows, cols)`; tune `wspace`/`hspace` to the content.
- Share y-limits when panels show the same metric so they can be compared.
- y-label on the left column only, x-label on the bottom row only.
- Hide unused grid cells with `ax.set_visible(False)`.

## Figure sizing

| Chart | figsize |
|---|---|
| Horizontal bars | (6–8, 0.5 × n + 1.5) |
| Vertical bars | (max(6, 4 + n), 6) |
| Line / time series | (11, 6) |
| Scatter | (10, 6.5) |
| Violin + strip | (10–12, 1.2 × n + 2) |
| Lollipop | (10, 0.9 × n + 1) |
| Heatmap | (1.2 × n + 2, n + 1) |
| PR/ROC pair | (12, 5.5) |
| Grids 2x2 / 3x2 / 3x3 | (10, 8) / (14, 9) / (14, 12) |

## Saving

```python
Path("./figures").mkdir(exist_ok=True)
for ext in ("pdf", "png"):
    fig.savefig(f"./figures/chart_name.{ext}", dpi=150, bbox_inches="tight")
```

Publication request: `dpi=300`. Quick/exploratory: PNG only.
