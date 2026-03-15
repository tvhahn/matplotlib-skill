# Vertical Bar Chart

**When to use:** Comparisons across categories, ranked values, model scores.
**Palette:** `"rocket"` for ≥5 bars (sequential ranking). For ≤4 categorical bars, slice `DIVERGING_COLORBLIND`: `["#d73027", "#fc8d59", "#fee090", "#4575b4"][:n]`. Do not invent semantic colors — always use these exact hex values.
**Bar order:** Sort by value descending so the tallest bar is on the left.
**API:** Always use `sns.barplot` — never use `ax.bar` directly.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

df_sorted = df.sort_values("value", ascending=False)

# Palette selection: DIVERGING_COLORBLIND for ≤4 bars, "rocket" for ≥5
n_bars = df_sorted.shape[0]
pal = ["#d73027", "#fc8d59", "#fee090", "#4575b4"][:n_bars] if n_bars <= 4 else "rocket"

sns.barplot(x="category", y="value", hue="category", data=df_sorted, palette=pal, legend=False, ax=ax)

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
1. Always use `sns.barplot(x=..., y=..., hue=..., data=..., palette=..., legend=False, ax=ax)` — never `ax.bar()`. The `hue` parameter must match the `x` column, and `legend=False` is mandatory.
2. Sort data descending by value before plotting: `df_sorted = df.sort_values("value_col", ascending=False)`.
3. Palette: `"rocket"` for ≥5 bars. For ≤4 bars use `["#d73027", "#fc8d59", "#fee090", "#4575b4"][:n]`. Slice order is left-to-right — do not rearrange, skip, or substitute.
4. Annotation: loop `ax.patches`, format as `f"{value:,.0f}"` for integers or `f"{value:.2f}"` for decimals. `weight="semibold"`, `size=12`, `color="dimgrey"`, `ha="center"`, `va="bottom"`. Do NOT append unit suffixes — units belong in the y-axis label only.
5. Grid: `ax.grid(alpha=0.7, linewidth=1, axis="y")` — exact parameters. No x-axis grid.
6. `ax.set_xlabel("")` — do not add an x-axis label; category names are self-explanatory.
7. `ax.set_ylabel("Label", fontsize=13, labelpad=10, color="dimgrey")` — defaults; adjust ±2 on fontsize/labelpad if label length requires it.
8. `ax.set_title("Title", loc="left", fontsize=14, pad=7)` — defaults; keep `loc="left"`.
9. Do not manually adjust `set_ylim` — let matplotlib auto-scale.
10. `figsize=(10, 6)` — default; widen to `(12, 6)` for >8 bars if labels would overlap.
11. Always use `dpi=150` in both `plt.subplots(dpi=150)` and `plt.savefig(dpi=150)`. Never use dpi=300 unless the user explicitly requests publication quality.
12. Always read data from the CSV file — never hardcode data values as inline DataFrames or dictionaries.
13. Do not add `ax.annotate()` arrows, editorial insight text, or italic annotations. The bar-end value labels (Rule 4) are the only annotations. Add commentary only if the user explicitly requests it.

**Customize:** For rotated x-labels, add `ax.set_xticklabels(ax.get_xticklabels(), rotation=90)`. For ≥5 bars, switch palette to `"rocket"`.
