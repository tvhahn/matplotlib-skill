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

# ALWAYS horizontal: x=numeric, y=categorical, orient="h"
# Do NOT use vertical orientation even for 2 categories
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

# --- Median annotations (default: always show) ---
medians = df.groupby("category")["value"].median()
for i, cat in enumerate(df["category"].unique()):
    med = medians[cat]
    ax.plot(med, i, marker="|", color="dimgrey", markersize=14, markeredgewidth=2, zorder=5)
    ax.text(med, i - 0.45, f"{med:.1f}", ha="center", va="bottom",
            fontsize=10, color="dimgrey", weight="semibold")

ax.set_title("Chart Title", fontsize=14, loc="left", pad=7, color="dimgrey")

ax.grid(axis="x", alpha=0.7, linewidth=1)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.yaxis.label.set_visible(False)
ax.tick_params(axis="x", labelsize=12)
ax.set_xlabel("Descriptive X-Axis Label (units)", labelpad=10, fontsize=12, color="dimgrey")
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- `color="white"` on violinplot and `color="black"` on stripplot — the white-with-black-dots look is the pattern's signature.
- Violin core params: `density_norm="width", inner=None, cut=0`.

**Guidance:**
- Default horizontal orientation (`orient="h"`). Use vertical when it better suits the data (e.g., 2-3 categories with short labels).
- Scale height for 8+ categories (add ~1 inch per additional 4 categories).
- Adjust strip `alpha` for data density: lower (0.05) for thousands of points, higher (0.2) for sparse data.
- Always include median markers (`"|"` marker) with value annotations by default — this satisfies Design Principle P6 (annotate the insight). Omit only if the user explicitly says no annotations.
- Format median annotations to match the data precision (`.1f` for continuous, `,.0f` for counts). Position labels above the marker (`va="bottom"`) to avoid overlapping strip points.
- Use `density_norm="count"` for proportional widths when category sizes differ meaningfully.
- Use classical titles that describe the metric (e.g., "Body Mass Distribution by Species"). Insight annotations carry findings, not the title. For multi-panel context, add bold-prefix: `r"$\bf{(a)}$"` before the description.
- Do not add an insight annotation below the axes. The median markers and value labels provide sufficient context. Let the data speak for itself.
- Adapt annotation format to the data domain: `$` prefix for currency, unit suffix (e.g., "g", "mpg") when the axis label alone doesn't suffice.
- **Panel frame:** Consider adding a panel frame (`ax.patch.set_edgecolor("lightgrey")`, `ax.patch.set_linewidth(0.8)`) when violins float with significant white space above and below, especially with 3+ categories. Omit for compact 2-category charts or when the chart is embedded in a multi-panel layout that already provides framing.

**Customize:** Adjust `alpha` on stripplot for density. Use `density_norm="count"` for proportional widths.
