# Heatmap / Spectrogram

**When to use:** Correlation matrices, frequency-time plots, spectrograms, pcolormesh data.
**Palette:** `RdBu_r` for correlation heatmaps (diverging — positive/negative need distinct colors), `inferno` for spectrograms.

### Correlation Heatmap

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", ax=ax,
            vmin=-1, vmax=1, center=0,
            linewidths=0.5, linecolor="white", square=True,
            cbar_kws={"shrink": 0.8},
            annot_kws={"size": 11, "weight": "medium"})

ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")
ax.set_title("Correlation Matrix", fontsize=14, loc="left", pad=7)
sns.despine(left=True, bottom=True)
```

**Rules:**
1. `cmap="RdBu_r"` with `vmin=-1, vmax=1, center=0` for correlation matrices. For non-correlation heatmaps (pivot tables), use `cmap="rocket"` without vmin/vmax/center.
2. `annot=True, fmt=".2f"` — always annotate cells. Use `annot_kws={"size": 11, "weight": "medium"}`. Do not set annotation `color` — let seaborn auto-contrast.
3. `linewidths=0.5, linecolor="white"` — default for matrices ≤12×12; reduce to `0.3` or omit for larger matrices.
4. `square=True` — always use square cells for correlation matrices.
5. `cbar_kws={"shrink": 0.8}` — do not add a colorbar label.
6. `figsize=(8, 6)` — default; scale up for matrices >10×10 (e.g., `(10, 8)` for 15×15).
7. `ax.set_title("Title", fontsize=14, loc="left", pad=7)` — do not add `color="dimgrey"` to the title.
8. `ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")` — default; omit rotation for short labels (<6 chars).
9. `ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")` — remove tick marks.
10. Data is pre-computed: load with `pd.read_csv(path, index_col=0)`. Do not compute `.corr()`.
11. Show full matrix by default — do not mask the triangle unless the user requests it.
12. `ax.grid(False)` is NOT needed for sns.heatmap — seaborn handles this. Do not add it.

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

**Customize:** For the heatmap, use `mask=np.triu(np.ones_like(corr, dtype=bool))` to show only the lower triangle. Adjust `vmax` on spectrograms to control color scaling. For spectrograms with dark backgrounds, use white text for panel labels.
