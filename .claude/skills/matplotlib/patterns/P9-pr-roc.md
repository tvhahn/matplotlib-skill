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

# AP/AUC — recall_avg is in decreasing order (sklearn convention),
# so sort ascending before integrating to get a positive area.
sorted_pr = np.argsort(recall_avg)
ap = float(np.trapezoid(precision_avg[sorted_pr], recall_avg[sorted_pr]))
auc = float(np.trapezoid(tpr_avg, fpr_avg))  # fpr_avg is already ascending

# --- Plot ---
fig, axes = plt.subplots(1, 2, figsize=(12, 6), dpi=150)
fig.suptitle("Dataset Name — N-Fold Cross-Validation Performance",
             fontsize=14, y=1.02)
fig.tight_layout(pad=3.0, rect=[0, 0.03, 1, 0.97])

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

# PR panel — iterate over fold rows
n_folds = precision_array.shape[0]
for i in range(n_folds):
    label = "k-fold models" if i == n_folds - 1 else None
    axes[0].plot(recall_array[i], precision_array[i],
                 color="grey", alpha=0.5, linewidth=1, label=label)

# CRITICAL: average line MUST use pal[5] (cubehelix dark blue) — not orange, not grey
axes[0].plot(recall_avg, precision_avg, label=f"Average (AP = {ap:.3f})",
             color=pal[5], linewidth=2)

# CRITICAL: baseline MUST be orange dashed — not grey, not black
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

# CRITICAL: average line MUST use pal[5] — same color on both panels
axes[1].plot(fpr_avg, tpr_avg, label=f"Average (AUC = {auc:.3f})",
             color=pal[5], linewidth=2)

# CRITICAL: baseline MUST be orange dashed — same on both panels
axes[1].plot([0, 1], [0, 1], linestyle="--",
             label="No skill", color="orange", linewidth=2, zorder=0)

axes[1].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
               labelcolor="dimgrey", loc="lower right", fontsize=10)
axes[1].set_title(r"$\bf{(b)}$" + " ROC Curve", loc="left", fontsize=12, pad=7)
axes[1].set_xlabel("False Positive Rate", fontsize=12, labelpad=8, color="dimgrey")
axes[1].set_ylabel("True Positive Rate", fontsize=12, labelpad=8, color="dimgrey")

# --- Figure-level insight ---
quality = "Strong" if auc > 0.85 else "Moderate" if auc > 0.70 else "Weak"
fig.text(0.99, 0.01, f"{quality} classifier: AUC = {auc:.3f}, AP = {ap:.3f}",
         ha="right", va="bottom", fontsize=9, color="dimgrey", style="italic")

for ax in axes.flatten():
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
    ax.grid(False)
    ax.patch.set_edgecolor("lightgrey")
    ax.patch.set_linewidth(0.8)

sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- PR first (a), ROC second (b) — panel order is fixed.
- Three line layers per panel: (1) grey k-fold lines, (2) average line with cubehelix `pal[5]`, (3) orange dashed baseline.
- Subplot outlines: `ax.patch.set_edgecolor("lightgrey")`, `ax.patch.set_linewidth(0.8)`.

**Guidance:**
- Default: load pre-computed data from NPZ files with `np.load()`. The `recall_avg` array is in **decreasing** order (sklearn convention) — sort ascending with `np.argsort` before computing AP via `np.trapezoid`. Do **not** use `abs()` as a workaround. Allow sklearn import when the user provides a fitted model and explicitly requests cross-validation.
- Include metric values in legend labels (e.g., `f"Average (AP = {ap:.3f})"`).
- Do NOT use `fill_between` unless the user explicitly requests confidence intervals.
- Adjust k-fold line `alpha` for number of folds: lower (0.3) for 20+ folds, higher (0.5-0.6) for 5-10.
- Both panels default to `set_xlim(0, 1)` and `set_ylim(0, 1.05)`.
- Replace "Dataset Name" in the `fig.suptitle()` template with the actual dataset name and fold count.
- Always add a figure-level insight annotation. Compute dynamically from AP and AUC.
- Move legend `loc` if it occludes curves — e.g., `loc="center left"` for PR panel when baseline is high.

**Customize:** Add AUC/AP values in legend labels. For single model (no CV), plot one line with `pal[5]` and the baseline — omit the grey fold lines.
