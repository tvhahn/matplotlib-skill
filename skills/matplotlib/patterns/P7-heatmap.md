# Heatmap / Spectrogram

**Use for:** correlation matrices, pivot tables (e.g. month × year), spectrograms and other `pcolormesh` grids.
**Exemplars:** `exemplars/P7-a.png` (11 variables, smaller cell text) and `exemplars/P7-b.png` (7 variables). Fixed: lower triangle, RdBu_r centred at 0, annotated cells. Varies: size, annotation font size, subtitle.

## Contents
- Correlation heatmap / pivot table
- Spectrogram (pcolormesh)

## Correlation heatmap

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

corr = pd.read_csv("data.csv", index_col=0)
# Lower triangle without the diagonal: drop the first row and last column, mask the rest
tri = corr.iloc[1:, :-1]
mask = np.triu(np.ones_like(tri, dtype=bool), k=1)
n = tri.shape[0]

fig, ax = plt.subplots(figsize=(max(6, 1.2 * n + 2), max(5, n + 1)), dpi=150)
sns.heatmap(tri, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, center=0,
            square=True, linewidths=0.5, linecolor="white", ax=ax,
            annot_kws={"size": max(7, 13 - n), "weight": "medium"},
            cbar_kws={"shrink": 0.75, "label": "Pearson r"})

# Colorbar text follows the dimgrey rule
cbar = ax.collections[0].colorbar
cbar.ax.tick_params(length=0, labelcolor="dimgrey")
cbar.ax.yaxis.label.set_color("dimgrey")
cbar.outline.set_visible(False)

# --- Title + takeaway subtitle: the strongest relationship with the variable that matters ---
target = corr.columns[0]  # or the variable the user asked about
partner = corr[target].drop(target).abs().idxmax()
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey",
             weight="semibold", pad=26)
ax.annotate(f"{target} is most strongly related to {partner} (r = {corr.loc[target, partner]:.2f})",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")

ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
ax.grid(False)  # whitegrid lines would show through masked cells
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Correlations: `cmap="RdBu_r"`, `vmin=-1, vmax=1, center=0`, `square=True`. Pivot tables (non-correlation values): `cmap="rocket"` without vmin/vmax/center.
- Annotated cells (`annot=True`); let seaborn pick the text colour for contrast.

**Guidance:**
- Symmetric correlation matrices: show the lower triangle without the diagonal (as in the template). Pivot tables: show the full grid.
- Format cells to the data: `.2f` for correlations, `,.0f` for counts; skip `annot` above ~15×15 and say so in the subtitle.
- Subtitle names the relationship that answers the question — usually the target variable's strongest partner, not just the largest off-diagonal value.
- Rotate x labels only when they are long (≥ 6 characters). Reduce `linewidths` to 0.3 above 12×12.
- Label the colorbar with the metric ("Pearson r", "Orders (thousands)").
- Data is usually pre-computed: `pd.read_csv(path, index_col=0)`. Compute `.corr(numeric_only=True)` when given raw data.
- No panel frame — the cells form their own edge.

## Spectrogram (pcolormesh)

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, axes = plt.subplots(1, 2, figsize=(11, 4), dpi=150)
panels = [(time_axis, freq_axis, data, "Frequency (Hz)", "Spectrogram"),
          (time_axis, bins, binned_data, "Frequency bin", "Binned")]
for i, (ax, (x, yv, z, ylabel, title)) in enumerate(zip(axes, panels)):
    ax.pcolormesh(x, yv, z, cmap="inferno", shading="auto",
                  vmax=np.percentile(z, 99))  # clip outliers so structure is visible
    ax.set_xlabel("Runtime (days)", color="dimgrey")
    ax.set_ylabel(ylabel, color="dimgrey")
    ax.set_title(r"$\bf{(" + chr(ord("a") + i) + r")}$" + f"  {title}",
                 loc="left", fontsize=12, pad=7, color="dimgrey")
    ax.grid(False)
    ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
    ax.patch.set_edgecolor("lightgrey")
    ax.patch.set_linewidth(0.8)
sns.despine(left=True, bottom=True, right=True)
```

**Guidance:** set `vmax` (a high percentile) so a few spikes don't wash out the rest; use white text for labels placed over the dark map.
