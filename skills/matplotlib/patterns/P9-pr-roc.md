# PR/ROC Curves

**Use for:** evaluating a classifier, usually across cross-validation folds. Panel (a) precision-recall, panel (b) ROC.
**Exemplars:** `exemplars/P9-a.png` (moderate model, folds vary) and `exemplars/P9-b.png` (weak class; PR legend moved off the curves). Fixed: PR then ROC, grey folds + cubehelix average + orange dashed baseline, panel frames. Varies: legend position, subtitle verdict (stable vs varying).

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
def area(x, y):
    o = np.argsort(x)
    return float(np.trapezoid(y[o], x[o]))

ap = area(recall_avg, precision_avg)
auc = area(fpr_avg, tpr_avg)
n_folds = precision_array.shape[0]
fold_ap = [area(recall_array[i], precision_array[i]) for i in range(n_folds)]
fold_auc = [area(fpr_array[i], tpr_array[i]) for i in range(n_folds)]

# --- Plot ---
fig, axes = plt.subplots(1, 2, figsize=(12, 6), dpi=150)
fig.suptitle(f"Dataset Name (positive = class) — {n_folds}-Fold Cross-Validation",
             fontsize=14, x=0.07, y=0.995, ha="left", color="dimgrey", weight="semibold")
# Takeaway subtitle: the lift over the no-skill baseline, computed from the data
spread = max(fold_auc) - min(fold_auc)
stability = "stable across folds" if spread < 0.05 else "varying across folds"
fig.text(0.07, 0.935, f"Average precision {ap:.2f} against a {baseline:.2f} no-skill baseline; "
         f"ROC AUC {auc:.2f}, {stability} ({min(fold_auc):.2f}–{max(fold_auc):.2f})",
         ha="left", va="bottom", fontsize=10.5, color="dimgrey")

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

# PR panel — iterate over fold rows
for i in range(n_folds):
    label = "k-fold models" if i == n_folds - 1 else None
    axes[0].plot(recall_array[i], precision_array[i],
                 color="grey", alpha=0.5, linewidth=1, label=label)

axes[0].plot(recall_avg, precision_avg,
             label=f"Average (AP = {ap:.3f}; folds {min(fold_ap):.2f}–{max(fold_ap):.2f})",
             color=pal[5], linewidth=2)

axes[0].plot([0, 1], [baseline, baseline], linestyle="--",
             label="No skill", color="orange", linewidth=2, zorder=0)

axes[0].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
               labelcolor="dimgrey", loc="lower left", fontsize=10)
axes[0].set_title(r"$\bf{(a)}$" + " Precision-Recall Curve", loc="left", fontsize=12, pad=7,
                  color="dimgrey")
axes[0].set_xlabel("Recall", fontsize=12, labelpad=8, color="dimgrey")
axes[0].set_ylabel("Precision", fontsize=12, labelpad=8, color="dimgrey")

# ROC panel
for i in range(n_folds):
    label = "k-fold models" if i == n_folds - 1 else None
    axes[1].plot(fpr_array[i], tpr_array[i],
                 color="grey", alpha=0.5, linewidth=1, label=label)

axes[1].plot(fpr_avg, tpr_avg,
             label=f"Average (AUC = {auc:.3f}; folds {min(fold_auc):.2f}–{max(fold_auc):.2f})",
             color=pal[5], linewidth=2)

axes[1].plot([0, 1], [0, 1], linestyle="--",
             label="No skill", color="orange", linewidth=2, zorder=0)

axes[1].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
               labelcolor="dimgrey", loc="lower right", fontsize=10)
axes[1].set_title(r"$\bf{(b)}$" + " ROC Curve", loc="left", fontsize=12, pad=7,
                  color="dimgrey")
axes[1].set_xlabel("False Positive Rate", fontsize=12, labelpad=8, color="dimgrey")
axes[1].set_ylabel("True Positive Rate", fontsize=12, labelpad=8, color="dimgrey")

for ax in axes.flatten():
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
    ax.grid(False)
    ax.patch.set_edgecolor("lightgrey")
    ax.patch.set_linewidth(0.8)

sns.despine(left=True, bottom=True)
fig.subplots_adjust(left=0.07, right=0.98, bottom=0.11, top=0.85, wspace=0.18)
```

Apply style-reference invariants.

**Signature:**
- PR first (a), ROC second (b) — panel order is fixed.
- Three line layers per panel: grey k-fold lines, the average in cubehelix `pal[5]` (same on both panels), and an orange dashed no-skill baseline (`color="orange", linestyle="--"`).
- Subplot outlines: `ax.patch.set_edgecolor("lightgrey")`, `ax.patch.set_linewidth(0.8)`.

**Guidance:**
- Default: load pre-computed data from NPZ files with `np.load()`. The `recall_avg` array is in **decreasing** order (sklearn convention) — sort ascending with `np.argsort` before computing AP via `np.trapezoid`. Do **not** use `abs()` as a workaround. Allow sklearn import when the user provides a fitted model and explicitly requests cross-validation.
- Include metric values and the fold range in legend labels (e.g., `f"Average (AP = {ap:.3f}; folds 0.91–0.96)"`).
- Do NOT use `fill_between` unless the user explicitly requests confidence intervals.
- Adjust k-fold line `alpha` for number of folds: lower (0.3) for 20+ folds, higher (0.5-0.6) for 5-10.
- Both panels default to `set_xlim(0, 1)` and `set_ylim(0, 1.05)`.
- Suptitle names the dataset, the positive class, and the fold count ("Churn model (positive = churned) — 5-fold CV").
- The takeaway goes in the subtitle under the suptitle (lift over the baseline, fold stability), computed from the data. No caption below the panels. Add an `ax.annotate` at a curve feature only when it tells the reader something (e.g. where precision collapses); for a crowded low-FPR corner, a zoom inset (see style-reference Craft) beats a callout.
- Move legend `loc` if it occludes curves. A good classifier's PR curve hugs the top, so the template puts the PR legend lower left; move it to `"center left"` when the baseline is low and the curve sags.

- Single model (no CV): one `pal[5]` line and the baseline; drop the fold lines and the fold ranges.
