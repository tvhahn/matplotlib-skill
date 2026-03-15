# PR/ROC Curves

**When to use:** Classification model evaluation, cross-validation performance.
**Palette:** Cubehelix `pal[5]` for average, grey for k-folds, orange dashed for baseline.
**Panel order:** (a) Precision-Recall first, (b) ROC second.

```python
import numpy as np
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data (load from NPZ) ---
data = np.load("data/raw/precomputed/p9/dataset.npz")
precision_array = data["precision_array"]   # shape (n_folds, n_points)
recall_array = data["recall_array"]
tpr_array = data["tpr_array"]
fpr_array = data["fpr_array"]
precision_avg = data["precision_avg"]       # shape (n_points,)
recall_avg = data["recall_avg"]
tpr_avg = data["tpr_avg"]
fpr_avg = data["fpr_avg"]
baseline = float(data["baseline"])          # scalar

# --- Plot ---
fig, axes = plt.subplots(1, 2, figsize=(12, 6), dpi=150)
fig.tight_layout(pad=5.0)

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

# PR panel — iterate over fold rows
n_folds = precision_array.shape[0]
for i in range(n_folds):
    label = "k-fold models" if i == n_folds - 1 else None
    axes[0].plot(recall_array[i], precision_array[i],
                 color="grey", alpha=0.5, linewidth=1, label=label)

axes[0].plot(recall_avg, precision_avg, label="Average",
             color=pal[5], linewidth=2)

axes[0].plot([0, 1], [baseline, baseline], linestyle="--",
             label="No skill", color="orange", linewidth=2, zorder=0)

axes[0].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
               labelcolor="dimgrey", loc="upper right", fontsize=10)
axes[0].set_title(r"$\bf{(a)}$" + " Precision-Recall Curve", loc="left", fontsize=12, pad=7)
axes[0].set_xlabel("Recall", fontsize=12, labelpad=8, color="dimgrey")
axes[0].set_ylabel("Precision", fontsize=12, labelpad=8, color="dimgrey")

# ROC panel
for i in range(n_folds):
    label = "k-fold models" if i == n_folds - 1 else None
    axes[1].plot(fpr_array[i], tpr_array[i],
                 color="grey", alpha=0.5, linewidth=1, label=label)

axes[1].plot(fpr_avg, tpr_avg, label="Average",
             color=pal[5], linewidth=2)

axes[1].plot([0, 1], [0, 1], linestyle="--",
             label="No skill", color="orange", linewidth=2, zorder=0)

axes[1].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
               labelcolor="dimgrey", loc="lower right", fontsize=10)
axes[1].set_title(r"$\bf{(b)}$" + " ROC Curve", loc="left", fontsize=12, pad=7)
axes[1].set_xlabel("False Positive Rate", fontsize=12, labelpad=8, color="dimgrey")
axes[1].set_ylabel("True Positive Rate", fontsize=12, labelpad=8, color="dimgrey")

for ax in axes.flatten():
    ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
    ax.grid(False)
    ax.patch.set_edgecolor("lightgrey")
    ax.patch.set_linewidth(0.8)

sns.despine(left=True, bottom=True)
```

**Rules (identity):**
- Do not import sklearn or run cross-validation — load pre-computed data from NPZ files with `np.load()`. Extract `baseline` as `float(data["baseline"])`.
- Panel order: **(a) PR first**, **(b) ROC second**.
- Three line layers per panel: (1) grey k-fold lines (`alpha=0.5`), (2) average line with `pal[5]`, (3) orange dashed baseline. Do not use `fill_between`.
- Average line color is always `pal[5]` from `sns.cubehelix_palette(6, rot=-0.25, light=0.7)`.
- Subplot outlines: `ax.patch.set_edgecolor("lightgrey")`, `ax.patch.set_linewidth(0.8)`.
- Baseline: use `ax.plot([0, 1], ...)` — not `axhline`. Do not use `sharex`/`sharey`.
- Include metric values in legend labels when available (e.g., `f"Average (AP = {ap:.3f})"`).
- Always use `dpi=150`. Save PDF+PNG with `bbox_inches="tight"`.

**Adapt when:**
- Adjust k-fold line `alpha` for number of folds: lower (0.3) for 20+ folds, default (0.5) for 5-10.
- For single model (no CV), plot one `pal[5]` line and baseline — omit grey fold lines.
- Adapt legend labels to context (e.g., model name instead of "k-fold models" for a single model).
- Adjust `tight_layout(pad=...)` if panel spacing looks off.

**Customize:** Add AUC/AP values in legend labels. For single model (no CV), plot one line with `pal[5]` and the baseline — omit the grey fold lines.
