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

**Rules:**
- Always use `sns.barplot` — never use `ax.barh()` directly. Pass `palette="Blues_d"` to `sns.barplot`.
- Always use `palette="Blues_d"` — never substitute cubehelix, rocket, or single-color palettes. The Blues_d gradient distinguishes ranked bars.
- Figsize `(4, 7)` is the default for 8-15 bars. For fewer bars (3-5), use `(6, 4)`. Always keep `dpi=150`.
- Annotation format is just the number with no prefixes or suffixes: `f"{value:.1f}"` for decimals, `f"{value:,.0f}"` for large integers. Never prepend `$` or append `%`, `" mpg"`, `" USD"`, or any other unit — the title provides context.
- Annotation styling is fixed: `weight="semibold", size=10, color="dimgrey"`. Do not vary size.
- `set_xlabel("")` — do not add an x-axis label; value labels on bar ends make it redundant.
- `set_ylabel("")` — category names on the y-axis are self-explanatory.
- `set_xticks([])` — always hide x-axis ticks; the bar-end labels carry the values.
- Title: `fontsize=14, loc="left", pad=7` — do not use fontsize=12 or 13.
- Do not add a separate `tick_params(axis="y", labelsize=...)` call — let `font_scale=1.0` control y-tick label size.
- Always use `dpi=150`. Save PDF+PNG with `bbox_inches="tight"`. Use relative paths for data (e.g., `data/raw/...`).
- Always read data from the CSV file — never hardcode data as inline DataFrames or dictionaries.
- After loading CSV data, apply `df.dropna()` or `df.dropna(subset=[...])` to remove rows with missing values in key columns before plotting. This prevents silent NaN-related plotting errors.

**Customize:** Replace `"Blues_d"` with a custom palette list for selective emphasis (e.g., one red bar among grey).
