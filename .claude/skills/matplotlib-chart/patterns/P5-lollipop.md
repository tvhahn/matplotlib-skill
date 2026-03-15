# Lollipop / Dumbbell Chart

**When to use:** Showing min/max/avg ranges, model comparison across k-folds.
**Palette:** Cubehelix for dots, grey for connecting lines, dimgrey for text.

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
