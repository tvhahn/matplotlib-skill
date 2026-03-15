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
- Always use `cmap="RdBu_r"` with `vmin=-1, vmax=1, center=0` for correlation matrices — never use sequential palettes (rocket, inferno) for correlation data
- Use `annot_kws={"size": 11, "weight": "medium"}` — do not set annotation `color`; let seaborn auto-contrast (dark text on light cells, white on dark cells)
- Use `cbar_kws={"shrink": 0.8}` — do not add a colorbar label
- Rotate x-tick labels 30° with `ha="right"` for readability
- Assume `corr` (a DataFrame) is already in memory — do not compute `.corr()` on raw data
- Show full matrix by default — do not mask the triangle unless the user requests it
- Do not add `color="dimgrey"` to the title — only annotations and tick labels use dimgrey

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
