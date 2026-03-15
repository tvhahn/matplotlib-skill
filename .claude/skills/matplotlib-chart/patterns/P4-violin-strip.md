# Violin + Strip Plot

**When to use:** Distribution comparisons, showing individual observations within categories.
**Palette:** White violins with black strip overlay.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(12, 5), dpi=150)

sns.violinplot(
    x="value", y="category", data=df,
    density_norm="width", inner=None, linewidth=2,
    color="white", saturation=1, cut=0,  # white fill is the signature look
    orient="h", zorder=0, width=0.8, ax=ax,
)

sns.stripplot(
    x="value", y="category", data=df,
    size=6, jitter=0.2, color="black", linewidth=0.5,  # black dots on white violins
    marker="o", edgecolor=None, alpha=0.1,
    zorder=4, orient="h", ax=ax,
)

ax.grid(axis="x", alpha=0.7, linewidth=1)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.yaxis.label.set_visible(False)
ax.tick_params(axis="x", labelsize=12)
ax.set_xlabel("Value", labelpad=10, fontsize=12)
ax.set_title(r"$\bf{(a)}$" + " Distribution Title", fontsize=12, loc="left", pad=7)
sns.despine(left=True, bottom=True)
```

**Rules:**
1. Always use horizontal orientation (`orient="h"`, `x="value_col"`, `y="category_col"`). Never use vertical orientation unless the user explicitly says "vertical".
2. `color="white"` on violinplot and `color="black"` on stripplot — the white-with-black-dots look is mandatory. Never use colored fills, per-category palettes, or hue-based coloring.
3. `ax.grid(axis="x", alpha=0.7, linewidth=1)` — exact params. Always `axis="x"` for horizontal.
4. Do NOT add ANY text annotations, median markers, `ax.text()` value labels, `ax.annotate()` arrows, `ax.axvline()` reference lines, colored overlays, box plots, or legends. The strip dots ARE the data visualization — no embellishment needed. Only add annotations if the user explicitly says "annotate", "label", or "add median values".
5. Title: `fontsize=12, loc="left", pad=7` with bold-prefix `r"$\bf{(a)}$"`. Do not use fontsize=14.
6. `figsize=(12, 5)` default. Use `dpi=150`. Scale height only for 8+ categories.
7. Violin params are fixed: `density_norm="width", inner=None, linewidth=2, saturation=1, cut=0, width=0.8, zorder=0`.
8. Strip params: `size=6, jitter=0.2, linewidth=0.5, marker="o", edgecolor=None, alpha=0.1, zorder=4`.

**Customize:** Adjust `alpha` on stripplot for density. Use `density_norm="count"` for proportional widths.
