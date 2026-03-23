# Vertical Bar Chart

**When to use:** Comparisons across categories, ranked values, model scores.
**Palette:** `"rocket"` for ≥5 bars (sequential ranking). For ≤4 categorical bars, slice `DIVERGING_COLORBLIND`: `["#d73027", "#fc8d59", "#fee090", "#4575b4"][:n]`.
**Bar order:** Sort by value descending so the tallest bar is on the left.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

df_sorted = df.sort_values("value", ascending=False)

# Palette selection: DIVERGING_COLORBLIND for ≤4 bars, "rocket" for ≥5
n_bars = df_sorted.shape[0]
pal = ["#d73027", "#fc8d59", "#fee090", "#4575b4"][:n_bars] if n_bars <= 4 else "rocket"

sns.barplot(x="category", y="value", hue="category", data=df_sorted, palette=pal,
           order=df_sorted["category"].tolist(), legend=False, ax=ax)

for p in ax.patches:
    value = p.get_height()
    space = df_sorted["value"].max() * 0.02
    _x = p.get_x() + p.get_width() / 2
    _y = p.get_y() + value + space
    ax.text(_x, _y, f"{value:,.0f}", ha="center", va="bottom",
            weight="semibold", size=12, color="dimgrey")
# --- Insight annotation (highlight top performer or notable gap) ---
top = df_sorted.iloc[0]
ax.text(0.98, 0.98, f'{top["category"]} leads at {top["value"]:,.0f}',
        transform=ax.transAxes, ha="right", va="top",
        fontsize=9, color="dimgrey", style="italic")

sns.despine(left=True, bottom=True)
ax.grid(alpha=0.7, linewidth=1, axis="y")
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_xlabel("")
ax.set_ylabel("Y-Axis Label", fontsize=13, labelpad=10, color="dimgrey")
ax.set_title("Chart Title", loc="left", fontsize=14, pad=7)
```

Apply style-reference invariants.

**Signature:**
- Sort data descending by value before plotting.
- Palette family: `DIVERGING_COLORBLIND` for ≤4 bars, `"rocket"` for ≥5 bars.

**Guidance:**
- Always read data from the CSV file using `pd.read_csv()` — never hardcode data values inline. If the data needs aggregation (groupby, filter by year, etc.), perform it in pandas after loading.
- Default `sns.barplot()` for the bar layer. Always pass `order=df_sorted["column"].tolist()` to enforce descending sort — seaborn ignores DataFrame order and re-sorts by category name without this. Template shows bar-end labels via `ax.patches` loop with `color="dimgrey"`, `weight="semibold"`.
- Always include an insight annotation (e.g., top performer, gap between #1 and #2). Position in upper-right using `transform=ax.transAxes`. Compute findings dynamically from the data — do not hardcode values.
- Widen `figsize` to `(12, 6)` for >8 bars if labels would overlap.
- Add unit suffixes when values are ambiguous without axis context — omit when y-axis label or title is sufficient.
- Adapt annotation format to the data domain: `$` prefix for currency, `%` suffix for rates, unit suffix when the y-axis label alone doesn't suffice. Use `f"{value:,.0f}"` for integers, `f"{value:.2f}"` for decimals.
- Scale `fontsize` on ylabel and title proportionally to figure size.
- Rotate x-tick labels with `ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")` when labels overlap.

**Customize:** For rotated x-labels, add `ax.set_xticklabels(ax.get_xticklabels(), rotation=90)`. For ≥5 bars, switch palette to `"rocket"`.
