# PR/ROC Curves

**When to use:** Classification model evaluation, cross-validation performance.
**Palette:** Cubehelix `pal[5]` for average, grey for k-folds, orange dashed for baseline.
**Panel order:** (a) Precision-Recall first, (b) ROC second. Do not swap.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

fig, axes = plt.subplots(1, 2, figsize=(12, 6), dpi=150)
fig.tight_layout(pad=5.0)

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

for i, (p, r) in enumerate(zip(precision_array, recall_array)):
    label = "k-fold models" if i == len(precision_array) - 1 else None
    axes[0].plot(r, p, color="grey", alpha=0.5, linewidth=1, label=label)

axes[0].plot(recall_avg, precision_avg, label="Average",
             color=pal[5], linewidth=2)

axes[0].plot([0, 1], [baseline, baseline], linestyle="--",
             label="No skill", color="orange", linewidth=2, zorder=0)

axes[0].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
               labelcolor="dimgrey", loc="upper right", fontsize=10)
axes[0].set_title(r"$\bf{(a)}$" + " Precision-Recall Curve", loc="left", fontsize=12, pad=7)
axes[0].set_xlabel("Recall", fontsize=12, labelpad=8, color="dimgrey")
axes[0].set_ylabel("Precision", fontsize=12, labelpad=8, color="dimgrey")

# ROC curve panel
for i, (t, f) in enumerate(zip(tpr_array, fpr_array)):
    label = "k-fold models" if i == len(tpr_array) - 1 else None
    axes[1].plot(f, t, color="grey", alpha=0.5, linewidth=1, label=label)

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

**Rules:**
- Do not import sklearn or run cross-validation — assume `precision_array`, `recall_array`, `tpr_array`, `fpr_array`, `precision_avg`, `recall_avg`, `tpr_avg`, `fpr_avg`, `baseline` are already in memory. Each fold is a grey line; the average is `pal[5]`.
- Panel order is fixed: **(a) PR first**, **(b) ROC second**. Do not swap.
- Three line layers per panel: (1) grey k-fold lines (`color="grey", alpha=0.5, linewidth=1`), (2) average line (`pal[5], linewidth=2`), (3) baseline (`"orange", linestyle="--", linewidth=2, zorder=0`). Use exactly `alpha=0.5` for fold lines — not 0.3 or 0.4.
- Average line color is always `pal[5]` on both panels — do not use `pal[4]` or any other index.
- Do not add `fill_between` shading under curves — the pattern uses lines only.
- Do not add `sharex=True` or `sharey=True` to `plt.subplots` — PR axes (Recall/Precision) and ROC axes (FPR/TPR) are different.
- Do not add `fig.suptitle` — the panel titles carry all context. If dataset/model info is needed, put it in the panel title suffix or omit.
- Do not add freestanding `ax.text` metric annotations — include metric values (AP, AUC) in legend labels instead (e.g., `f"Average (AP = {ap:.3f})"`).
- Add subplot outlines on both panels: `ax.patch.set_edgecolor("lightgrey")` and `ax.patch.set_linewidth(0.8)` — frames each panel visually (consistent with multi-panel pattern).
- Legend: `loc="upper right"` for PR panel, `loc="lower right"` for ROC panel, `fontsize=10`.
- Axis labels: `fontsize=12, labelpad=8, color="dimgrey"` on all four axis labels (xlabel + ylabel on both panels).
- `tight_layout(pad=5.0)` — do not change the pad value.
- Default legend labels: `"k-fold models"` for fold lines (only on last fold), `"Average"` for average (append metric in parens if available, e.g., `f"Average (AP = {ap:.3f})"`), `"No skill"` for baseline. Adapt if context requires (e.g., single model without CV — use model name instead of "k-fold models").
- Baseline: always use `ax.plot([0, 1], [baseline, baseline], ...)` for PR and `ax.plot([0, 1], [0, 1], ...)` for ROC. Do not use `axhline`.
- Do not add explicit axis limits (`set_xlim`, `set_ylim`) — let matplotlib auto-scale.
**Customize:** Add AUC/AP values in legend labels. For single model (no CV), plot one line with `pal[5]` and the baseline — omit the grey fold lines.
