# PR/ROC Curves

**Use for:** evaluating a classifier, usually across cross-validation folds. Panel (a) precision-recall, panel (b) ROC.

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
baseline = data["baseline"].item()          # stored as a 1-element array

# AP/AUC — recall_avg is in decreasing order (sklearn convention),
# so sort ascending before integrating to get a positive area.
sorted_pr = np.argsort(recall_avg)
ap = float(np.trapezoid(precision_avg[sorted_pr], recall_avg[sorted_pr]))
auc = float(np.trapezoid(tpr_avg, fpr_avg))  # fpr_avg is already ascending

# --- Plot ---
fig, axes = plt.subplots(1, 2, figsize=(12, 6), dpi=150)
fig.suptitle("Dataset Name — N-Fold Cross-Validation", fontsize=14, x=0.07, ha="left",
             color="dimgrey", weight="semibold")

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

# PR panel — iterate over fold rows
n_folds = precision_array.shape[0]
for i in range(n_folds):
    label = "k-fold models" if i == n_folds - 1 else None
    axes[0].plot(recall_array[i], precision_array[i],
                 color="grey", alpha=0.5, linewidth=1, label=label)

axes[0].plot(recall_avg, precision_avg, label=f"Average (AP = {ap:.3f})",
             color=pal[5], linewidth=2)

axes[0].plot([0, 1], [baseline, baseline], linestyle="--",
             label="No skill", color="orange", linewidth=2, zorder=0)

axes[0].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
               labelcolor="dimgrey", loc="upper right", fontsize=10)
axes[0].set_title(r"$\bf{(a)}$" + " Precision-Recall Curve", loc="left", fontsize=12, pad=7,
                  color="dimgrey")
axes[0].set_xlabel("Recall", fontsize=12, labelpad=8, color="dimgrey")
axes[0].set_ylabel("Precision", fontsize=12, labelpad=8, color="dimgrey")

# ROC panel
for i in range(n_folds):
    label = "k-fold models" if i == n_folds - 1 else None
    axes[1].plot(fpr_array[i], tpr_array[i],
                 color="grey", alpha=0.5, linewidth=1, label=label)

axes[1].plot(fpr_avg, tpr_avg, label=f"Average (AUC = {auc:.3f})",
             color=pal[5], linewidth=2)

axes[1].plot([0, 1], [0, 1], linestyle="--",
             label="No skill", color="orange", linewidth=2, zorder=0)

axes[1].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
               labelcolor="dimgrey", loc="lower right", fontsize=10)
axes[1].set_title(r"$\bf{(b)}$" + " ROC Curve", loc="left", fontsize=12, pad=7,
                  color="dimgrey")
axes[1].set_xlabel("False Positive Rate", fontsize=12, labelpad=8, color="dimgrey")
axes[1].set_ylabel("True Positive Rate", fontsize=12, labelpad=8, color="dimgrey")

# --- Caption under each panel: spread across folds (the average is already in the legend) ---
def area(x, y):
    o = np.argsort(x)
    return float(np.trapezoid(y[o], x[o]))

fold_ap = [area(recall_array[i], precision_array[i]) for i in range(n_folds)]
fold_auc = [area(fpr_array[i], tpr_array[i]) for i in range(n_folds)]
for ax, name, avg, folds in ((axes[0], "PR AUC", ap, fold_ap), (axes[1], "ROC AUC", auc, fold_auc)):
    ax.text(0, -0.16, f"{name} ranges {min(folds):.3f}–{max(folds):.3f} across {n_folds} folds",
            transform=ax.transAxes, ha="left", va="top", fontsize=10, color="dimgrey")

for ax in axes.flatten():
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
    ax.grid(False)
    ax.patch.set_edgecolor("lightgrey")
    ax.patch.set_linewidth(0.8)

sns.despine(left=True, bottom=True)
fig.tight_layout()
```

Apply style-reference invariants.

**Signature:**
- PR first (a), ROC second (b) — panel order is fixed.
- Three line layers per panel: grey k-fold lines, the average in cubehelix `pal[5]` (same on both panels), and an orange dashed no-skill baseline (`color="orange", linestyle="--"`).
- Subplot outlines: `ax.patch.set_edgecolor("lightgrey")`, `ax.patch.set_linewidth(0.8)`.

**Guidance:**
- Default: load pre-computed data from NPZ files with `np.load()`. The `recall_avg` array is in **decreasing** order (sklearn convention) — sort ascending with `np.argsort` before computing AP via `np.trapezoid`. Do **not** use `abs()` as a workaround. Allow sklearn import when the user provides a fitted model and explicitly requests cross-validation.
- Include metric values in legend labels (e.g., `f"Average (AP = {ap:.3f})"`).
- Do NOT use `fill_between` unless the user explicitly requests confidence intervals.
- Adjust k-fold line `alpha` for number of folds: lower (0.3) for 20+ folds, higher (0.5-0.6) for 5-10.
- Both panels default to `set_xlim(0, 1)` and `set_ylim(0, 1.05)`.
- Suptitle names the dataset, the positive class, and the fold count ("Churn model (positive = churned) — 5-fold CV").
- Put the metric caption under each panel (average and range across folds), as in the template. Add an `ax.annotate` at a curve feature only when it tells the reader something (e.g. where precision collapses).
- Move legend `loc` if it occludes curves — e.g., `loc="center left"` for PR panel when baseline is high.

- Single model (no CV): one `pal[5]` line and the baseline; drop the fold lines and the range in the caption.
