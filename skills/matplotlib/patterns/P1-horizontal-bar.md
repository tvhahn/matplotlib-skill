# Horizontal Bar Chart

**When to use:** Ranked percentages, category comparisons, survey results.
**Palette:** `Blues_d` for neutral ranking, or `Greys_r` + `ACCENT_RED` for selective emphasis.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# Scale height for category count
n_cats = df["category"].nunique()
fig_h = max(4, 1 + n_cats * 0.7)
fig, ax = plt.subplots(figsize=(max(4, fig_h * 0.6), fig_h), dpi=150)

sns.barplot(x="percent", y="category", hue="category", data=df, palette="Blues_d", legend=False, ax=ax)

for p in ax.patches:
    space = 1.5
    _x = p.get_x() + p.get_width() + space
    _y = p.get_y() + p.get_height() / 2
    value = p.get_width()
    ax.text(_x, _y, f"{value:.1f}", ha="left", va="center",
            weight="semibold", size=10, color="dimgrey")

# --- Insight annotation (highlight top item or notable gap) ---
top = df.sort_values("percent", ascending=False).iloc[0]
fig.text(0.98, 0.01, f'{top["category"]} leads at {top["percent"]:.1f}',
         ha="right", va="bottom",
         fontsize=9, color="dimgrey", style="italic")

ax.set_ylabel("")
ax.set_xlabel("")
ax.axvline(x=0, color="lightgrey", linewidth=0.8, zorder=0)
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_xticks([])
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7, color="dimgrey")
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Bar-end value labels with hidden x-ticks (`set_xticks([])`); the labels carry the numbers, not the axis.
- Annotations use `color="dimgrey"`.

**Guidance:**
- Default `sns.barplot()` for the bar layer. Template shows `palette="Blues_d"` for neutral ranking. When one bar clearly dominates (e.g., top value >2× the median), consider `Greys_r` + `ACCENT_RED` (`"#bd0c0c"`) on the standout bar to reinforce the finding visually.
- Scale `figsize` for category count: `(4, 7)` for 8-15 bars, `(6, 4)` for 3-5 bars, wider for 15+.
- Use classical titles that describe the metric (e.g., "Collisions per Billion Miles by State"). Insight annotations carry findings, not the title.
- Adapt annotation format to the data domain: `$` prefix for currency, `%` suffix for rates, unit suffix (e.g., "mpg") when the axis label alone doesn't suffice. Add unit prefixes/suffixes when values are ambiguous — omit when the title provides enough context.
- Adjust annotation `size` proportionally if bars are very narrow or figure is compact.
- Scale title `fontsize` with figure size (12 for compact figures, 14-16 for large ones).
- Always include an insight annotation (e.g., top performer, notable gap between top-2). Position BELOW the axes using `fig.text(0.98, 0.01, ..., ha="right", va="bottom")` — never inside the axes area where it can overlap data rows. Compute the finding dynamically — do not hardcode values.

**Customize:** Replace `"Blues_d"` with a custom palette list for selective emphasis (e.g., one red bar among grey).
