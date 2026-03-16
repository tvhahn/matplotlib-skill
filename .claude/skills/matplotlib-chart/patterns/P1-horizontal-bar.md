# Horizontal Bar Chart

**When to use:** Ranked percentages, category comparisons, survey results.
**Palette:** `Blues_d` for neutral ranking, or `Greys_r` + `ACCENT_RED` for selective emphasis.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(4, 7), dpi=150)

sns.barplot(x="percent", y="category", hue="category", data=df, palette="Blues_d", legend=False, ax=ax)

for p in ax.patches:
    space = 1.5
    _x = p.get_x() + p.get_width() + space
    _y = p.get_y() + p.get_height() / 2
    value = p.get_width()
    ax.text(_x, _y, f"{value:.1f}", ha="left", va="center",
            weight="semibold", size=10, color="dimgrey")

ax.set_ylabel("")
ax.set_xlabel("")
ax.axvline(x=0, color="lightgrey", linewidth=0.8, zorder=0)
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_xticks([])
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7)
sns.despine(left=True, bottom=True)
```

**Rules (identity):**
- Use `sns.barplot()` — not `ax.barh()` directly.
- Use `palette="Blues_d"` for neutral ranking. Do not substitute cubehelix, rocket, or single-color palettes.
- Hide x-axis ticks with `set_xticks([])` — bar-end value labels carry the numbers.
- Annotations use `color="dimgrey"` with `weight="semibold"`.
- Always use `dpi=150`. Save PDF+PNG with `bbox_inches="tight"`.
- Always read data from CSV — never hardcode inline DataFrames.
- Apply `df.dropna()` or `df.dropna(subset=[...])` after loading CSV to prevent NaN errors.

**Adapt when:**
- Scale `figsize` for category count: `(4, 7)` for 8-15 bars, `(6, 4)` for 3-5 bars, wider for 15+.
- Add unit prefixes/suffixes (e.g., `$`, `%`) when values are ambiguous without them — omit when the title provides enough context.
- Adjust annotation `size` proportionally if bars are very narrow or figure is compact.
- Scale title `fontsize` with figure size (12 for compact figures, 14-16 for large ones).

**Customize:** Replace `"Blues_d"` with a custom palette list for selective emphasis (e.g., one red bar among grey).
