# Vertical Bar Chart

**When to use:** Comparisons across categories, ranked values, model scores.
**Palette:** `"rocket"` for ≥5 bars (sequential ranking). For ≤4 categorical bars, slice `DIVERGING_COLORBLIND`: `["#d73027", "#fc8d59", "#fee090", "#4575b4"][:n]`. Do not invent semantic colors — always use these exact hex values.
**Bar order:** Sort by value descending so the tallest bar is on the left.
**API:** Always use `sns.barplot` — never use `ax.bar` directly.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

df_sorted = df.sort_values("value", ascending=False)

sns.barplot(x="category", y="value", hue="category", data=df_sorted, palette="rocket", legend=False, ax=ax)

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
- Palette slice order is left-to-right: for 3 bars use `["#d73027", "#fc8d59", "#fee090"]`, for 4 use all four. Do not rearrange, skip, or substitute colors.
- Annotation format is just the number: `f"{value:,.0f}"` for integers, `f"{value:.2f}"` for decimals. Do not append unit suffixes (e.g., " MWh", " K") — units belong in the y-axis label.
- `set_xlabel("")` — do not add an x-axis label; category names on the x-axis are self-explanatory
- Do not manually adjust `set_ylim` — let matplotlib auto-scale; `bbox_inches="tight"` handles clipping

**Customize:** For rotated x-labels, add `ax.set_xticklabels(ax.get_xticklabels(), rotation=90)`. For ≥5 bars, switch palette to `"rocket"`.
