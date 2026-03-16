# Violin + Strip Plot

**When to use:** Distribution comparisons, showing individual observations within categories.
**Palette:** White violins with black strip overlay.
**Orientation:** Horizontal by default (`orient="h"`).

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data ---
df = pd.read_csv("data.csv").dropna(subset=["value", "category"])

# Scale height to category count
n_cats = df["category"].nunique()
fig, ax = plt.subplots(figsize=(12, max(5, 2 + n_cats * 1.2)), dpi=150)

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

**Rules (identity):**
- Use horizontal orientation (`orient="h"`) by default. Only use vertical if the user explicitly requests it.
- `color="white"` on violinplot and `color="black"` on stripplot — the white-with-black-dots look is the pattern's signature. Do not use colored fills or per-category palettes.
- Violin core params: `density_norm="width", inner=None, cut=0`.
- Title uses bold-prefix convention: `r"$\bf{(a)}$"` with `loc="left"`.
- Always use `dpi=150`. Save PDF+PNG with `bbox_inches="tight"`.

**Adapt when:**
- Scale height for 8+ categories (add ~1 inch per additional 4 categories).
- Adjust strip `alpha` for data density: lower (0.05) for thousands of points, higher (0.2) for sparse data.
- Add median markers or reference lines if the user requests them or if the insight requires comparing central tendency across groups.
- Add value annotations if the user says "annotate", "label", or "add median values".
- Use `density_norm="count"` for proportional widths when category sizes differ meaningfully.

**Customize:** Adjust `alpha` on stripplot for density. Use `density_norm="count"` for proportional widths.
