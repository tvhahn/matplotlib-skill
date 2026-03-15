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

# min/max value annotations (below each dot, smaller text)
for i in range(df.shape[0]):
    ax.text(x=df["min"].iloc[i], y=i - 0.15, s=f'{df["min"].iloc[i]:,.0f}',
            ha="center", va="top", size=8.5,
            color="dimgrey", weight="normal")
    ax.text(x=df["max"].iloc[i], y=i - 0.15, s=f'{df["max"].iloc[i]:,.0f}',
            ha="center", va="top", size=8.5,
            color="dimgrey", weight="normal")

ax.grid(False)
sns.despine(left=True, bottom=True)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_ylabel("")
ax.set_xlabel("X-Axis Label", fontsize=12, labelpad=8, color="dimgrey")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7)

ax.legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
         labelcolor="dimgrey", loc="lower right", fontsize=11)
```

**Rules:**
1. Palette: always define `pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)`, then `darkblue = pal[5]` and `lightblue = pal[2]`. Use `darkblue` for min/max dots and `lightblue` for avg dots. Do not substitute amber, orange, colormap-mapped values, or any other colors.
2. Three separate `ax.scatter()` calls required: one for min dots (`color=darkblue`), one for max dots (`color=darkblue`), one for avg dots (`color=lightblue`). Do not combine min/max into one scatter, do not omit min/max dots, do not use a colormap.
3. Annotate all three values per row: avg centered above (`y=i + 0.15`, `size=10`, `weight="medium"`), min and max centered below (`y=i - 0.15`, `size=8.5`, `weight="normal"`). All annotations `color="dimgrey"`. Omit min/max labels only if the user explicitly says "clean" or "minimal".
4. `grid(False)` — no x-grid or y-grid.
5. DOT_SIZE = 150 for all dots; do not change the dot size.
6. Connecting lines: `lw=4`, `alpha=0.4`, `color="grey"`, `zorder=0` — only one `hlines` call (min to max range); do not add extra lollipop sticks from zero.
7. Exactly 2 legend items: "Average" (`lightblue`) and "Min/Max" (`darkblue`) — do not add a Range line handle.
8. Legend: `loc="lower right"`, `fontsize=11` — do not use `bbox_to_anchor` unless the chart is very dense.
9. Annotation size: `size=10` — do not use string sizes like `"x-large"`.
10. Format string adapts to data: use `f'{value:,.0f}'` for large numbers/currency, `f'{value:.2f}'` for decimals.
11. Title: `fontsize=14`, `loc="left"`, `pad=7` — do not change these values.
12. Do not add `axvline` baselines, subtitle text annotations, `fig.text()` overlays, or other decorative elements not shown in the pattern code.
13. Always set a descriptive x-axis label: `ax.set_xlabel("Label", fontsize=12, labelpad=8, color="dimgrey")`. The label should describe the measurement (e.g., "Score", "AUC", "Spending (USD)"). Do not use `set_xlabel("")`.

**Customize:** Add leading lines with `ax.plot([x_end + 0.02, x_label], [i, i], lw=1, color="grey", alpha=0.4, zorder=0)`. Add classifier name text at left margin.
