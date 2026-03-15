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

**Customize:** Adjust `alpha` on stripplot for density. Use `density_norm="count"` for proportional widths. For vertical orientation, swap x/y and set `orient="v"`. Keep `color="white"` on violins — the white-fill-with-black-dots aesthetic is distinctive; only use colored fills when the user explicitly requests it.
