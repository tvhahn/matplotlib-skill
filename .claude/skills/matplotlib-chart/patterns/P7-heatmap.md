# Heatmap / Spectrogram

**When to use:** Correlation matrices, frequency-time plots, spectrograms, pcolormesh data.
**Palette:** `RdBu_r` for correlation heatmaps (diverging — positive/negative need distinct colors), `inferno` for spectrograms.

### Correlation Heatmap

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Dynamic figsize and annotation size for matrix dimensions ---
n_vars = corr.shape[0]
fig_w = max(6, 2 + n_vars * 1.2)    # wider for more columns
fig_h = max(5, 1 + n_vars * 1.0)    # taller for more rows
annot_size = max(7, 13 - n_vars)     # shrink text for large matrices

fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)

sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", ax=ax,
            vmin=-1, vmax=1, center=0,
            linewidths=0.5, linecolor="white", square=True,
            cbar_kws={"shrink": 0.8, "label": "Pearson r"},
            annot_kws={"size": annot_size, "weight": "medium"})

ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
ax.set_title("Correlation Matrix", fontsize=14, loc="left", pad=7, color="dimgrey")

# --- Insight annotation (strongest correlation from data) ---
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
upper = corr.where(mask)
strongest_val = upper.abs().max().max()
strongest_pair = upper.abs().stack().idxmax()
fig.text(0.98, 0.01,
         f"Strongest: {strongest_pair[0]} ↔ {strongest_pair[1]} (r = {corr.loc[strongest_pair]:.2f})",
         ha="right", va="bottom", fontsize=9, color="dimgrey", style="italic")

sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Correlation heatmaps: `cmap="RdBu_r"` with `vmin=-1, vmax=1, center=0`. For non-correlation heatmaps (pivot tables), use `cmap="rocket"` without vmin/vmax/center.
- Always annotate cells: `annot=True, fmt=".2f"`. Do not set annotation `color` — let seaborn auto-contrast.
- `square=True` for correlation matrices.

**Guidance:**
- Use classical titles that describe the chart (e.g., "Feature Correlation Matrix"). Insight annotations carry findings, not the title.
- Default: add a colorbar label (e.g., `"Pearson r"`) and an insight annotation below the chart (`fig.text(...)` or subtitle) highlighting the strongest or most notable correlation. Consider omitting the insight only for very large matrices (>15×15) where a single finding is not representative.
- Default: no additional colorbar label beyond the cbar. Consider adding one when the heatmap shows a non-obvious metric.
- Default: show full matrix. Consider masking with `np.triu`/`np.tril` when the user requests it or the matrix is large (>15×15) and symmetric.
- `ax.grid(False)` is NOT needed for `sns.heatmap` — seaborn handles this internally.
- Data is typically pre-computed: load with `pd.read_csv(path, index_col=0)`. Allow `.corr()` when the user provides raw data.
- Dynamic figsize and annotation size are computed from matrix dimensions in the template. Do not hardcode these.
- Reduce `linewidths` to 0.3 or omit for matrices >12×12.
- Omit tick label `rotation` for short labels (<6 chars).
- **Panel frame:** Correlation heatmaps do not need a panel frame — the cell grid creates its own visual boundary. For spectrograms (`pcolormesh`), add a panel frame (`ax.patch.set_edgecolor("lightgrey")`, `ax.patch.set_linewidth(0.8)`) to define the panel edges, especially for multi-panel layouts.

### Spectrogram (pcolormesh)

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(1, 2, figsize=(11, 4), dpi=150)

ax[0].pcolormesh(time_axis, freq_axis, data, cmap="inferno",
                 vmax=vmax_val, shading="auto")
ax[0].set_ylabel("Frequency (Hz)")
ax[0].set_xlabel("Runtime (days)")
ax[0].grid(False)
ax[0].tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax[0].set_title(r"$\bf{(a)}$" + " Spectrogram", loc="left", fontsize=12, pad=7)

ax[1].pcolormesh(time_axis, bins, binned_data, cmap="inferno",
                 vmax=vmax_val2, shading="auto")
ax[1].set_xlabel("Runtime (days)")
ax[1].set_ylabel("Frequency Bin")
ax[1].grid(False)
ax[1].tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax[1].set_title(r"$\bf{(b)}$" + " Binned", loc="left", fontsize=12, pad=7)

sns.despine(left=True, bottom=True, right=True)
```

**Customize:** Adjust `vmax` on spectrograms to control color scaling. For spectrograms with dark backgrounds, use white text for panel labels.
