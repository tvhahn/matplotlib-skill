# Training Diagnostics: Learning Curves / Confusion Matrix

**Use for:** model training reports — train vs validation loss (and accuracy) per
epoch, and a confusion matrix from true/predicted labels. Threshold curves → P9;
decision regions → P6.
**Exemplars:** `exemplars/P13-training.png` (loss on a log scale + accuracy, best epoch marked) and `exemplars/P13-confusion.png` (3 classes, row-normalised). Fixed: validation solid red, train dashed blue, best-epoch guide; confusion cells show % and n. Varies: log scale, second panel, the error the subtitle names.

## Contents
- Training curves (loss, optional accuracy panel)
- Confusion matrix

## Training curves

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
import matplotlib.patheffects as pe
import matplotlib.ticker as mticker

# --- Data: one row per epoch; adapt the column names ---
df = pd.read_csv("data.csv").dropna(subset=["epoch", "train_loss", "val_loss"])
best, last = df.loc[df["val_loss"].idxmin()], df.iloc[-1]
metrics = [("loss", "Loss")] + ([("acc", "Accuracy")] if "val_acc" in df else [])

VAL, TRAIN = "#d73027", "#4575b4"  # validation solid red, train dashed blue
HALO = [pe.withStroke(linewidth=3, foreground="white")]
fig, axes = plt.subplots(len(metrics), 1, sharex=True, dpi=150, squeeze=False,
                         figsize=(10, 3.2 + 2.6 * len(metrics)),
                         gridspec_kw={"height_ratios": [3, 2][: len(metrics)], "hspace": 0.12})
for ax, (m, name) in zip(axes[:, 0], metrics):
    tr, va = df[f"train_{m}"], df[f"val_{m}"]
    ax.plot(df["epoch"], tr, color=TRAIN, lw=2, ls="--")
    ax.plot(df["epoch"], va, color=VAL, lw=2)
    ax.axvline(best["epoch"], color="lightgrey", lw=1, zorder=0)
    ax.plot(best["epoch"], best[f"val_{m}"], "o", ms=7, color=VAL, mec="white", zorder=4)
    # Direct labels right of the line ends; the higher sits above, the lower below
    for y, other, lab, c in ((va.iloc[-1], tr.iloc[-1], "Validation", VAL),
                             (tr.iloc[-1], va.iloc[-1], "Train", TRAIN)):
        up = y >= other
        ax.annotate(lab, xy=(last["epoch"], y), xytext=(6, 1 if up else -1),
                    textcoords="offset points", ha="left", va="bottom" if up else "top",
                    fontsize=10.5, color=c, weight="semibold")
    if m == "loss" and df[["train_loss", "val_loss"]].max().max() / df[["train_loss", "val_loss"]].min().min() > 10:
        ax.set_yscale("log")  # loss spans >10x: log shows the late epochs
        ax.yaxis.set_major_locator(mticker.LogLocator(subs=(1, 2, 5)))
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}"))
        name += " (log scale)"
    if m == "acc":
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=None))
    ax.set_ylabel(name, fontsize=12, labelpad=8, color="dimgrey")
    ax.grid(axis="x", visible=False)
    ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
    ax.patch.set_edgecolor("lightgrey")
    ax.patch.set_linewidth(0.8)

# The best epoch, annotated at the data (haloed: it may cross a curve)
ax0 = axes[0, 0]
t = ax0.annotate(f"Best validation loss {best['val_loss']:.3f}\nat epoch {best['epoch']:.0f}",
                 xy=(best["epoch"], best["val_loss"]), xytext=(12, 14), textcoords="offset points",
                 ha="left", va="bottom", fontsize=10, color="dimgrey",
                 arrowprops=dict(arrowstyle="-", color="dimgrey", lw=0.8))
t.set_path_effects(HALO)
axes[-1, 0].set_xlabel("Epoch", fontsize=12, labelpad=8, color="dimgrey")
axes[-1, 0].xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# --- Title + takeaway subtitle (computed) ---
rise = last["val_loss"] / best["val_loss"] - 1
msg = (f"Validation loss bottoms out at epoch {best['epoch']:.0f} and ends {rise:.0%} higher: "
       "stop there" if rise > 0.05 else f"Validation loss is still near its low at epoch {last['epoch']:.0f}")
ax0.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold", pad=26)
ax0.annotate(msg, xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
             ha="left", va="bottom", fontsize=10.5, color="dimgrey")
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Validation solid `#d73027`, train dashed `#4575b4` (colour *and* linestyle), labelled at the line ends instead of a legend.
- The best validation epoch: a marker on the curve, a lightgrey vertical guide through every panel, and a haloed label with value and epoch.

**Guidance:**
- Log y when loss spans more than 10x (the template switches automatically); accuracy stays linear, as a percent.
- Drop the accuracy panel when the file has no accuracy columns, or when the user only asks about loss; add other metrics (F1, AUC) as further shared-x panels.
- The subtitle says what to do: where to stop (early stopping), whether the gap between train and validation is growing (overfitting), or that the curves are still falling (train longer).
- Several runs or folds: draw each in light grey (`alpha≈0.4`) and the mean in colour.
- Noisy per-step curves: plot a rolling mean in colour over the raw curve in light grey.

## Confusion matrix

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data: one row per prediction; adapt the column names ---
df = pd.read_csv("data.csv").dropna(subset=["y_true", "y_pred"])
classes = sorted(set(df["y_true"]) | set(df["y_pred"]))  # or the natural class order
counts = pd.crosstab(df["y_true"], df["y_pred"]).reindex(index=classes, columns=classes,
                                                         fill_value=0)
rate = counts.div(counts.sum(axis=1), axis=0)  # row-normalised: recall on the diagonal
k = len(classes)

cmap = plt.get_cmap("Blues")
fig, ax = plt.subplots(figsize=(1.4 * k + 2.5, 1.4 * k + 1.8), dpi=150)
sns.heatmap(rate, cmap=cmap, vmin=0, vmax=1, square=True, cbar=False, annot=False,
            linewidths=2, linecolor="white", ax=ax)
for i in range(k):
    for j in range(k):
        lum = np.dot(cmap(rate.iat[i, j])[:3], [0.2126, 0.7152, 0.0722])
        color = "white" if lum < 0.45 else "dimgrey"
        ax.text(j + 0.5, i + 0.45, f"{rate.iat[i, j]:.0%}", ha="center", va="center",
                fontsize=13, color=color, weight="semibold" if i == j else "normal")
        ax.text(j + 0.5, i + 0.72, f"n={counts.iat[i, j]:,}", ha="center", va="center",
                fontsize=9, color=color)

ax.set_xlabel("Predicted class", fontsize=12, labelpad=8, color="dimgrey")
ax.set_ylabel("True class", fontsize=12, labelpad=8, color="dimgrey")
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
ax.grid(False)

# --- Title + takeaway subtitle: accuracy and the largest confusion (computed) ---
acc = np.trace(counts.values) / counts.values.sum()
off = rate.mask(np.eye(k, dtype=bool))
t, p = off.stack().idxmax()
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold", pad=26)
ax.annotate(f"Accuracy {acc:.1%}; most common error: {t} predicted as {p} "
            f"({off.loc[t, p]:.0%} of {t})",
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True, right=True)
```

Apply style-reference invariants.

**Signature:**
- Row-normalised share as colour (`Blues`, `vmin=0, vmax=1`), square cells with white gaps, each cell showing the percentage *and* the count.
- Cell text white on dark cells, dimgrey on light ones (by luminance); diagonal percentages semibold.

**Guidance:**
- Rows are the true class, columns the prediction; say "row-normalised" in the subtitle when a reader might expect column (precision) normalisation.
- No colorbar when every cell is annotated; add one labelled "Share of true class" (dimgrey ticks) only for large matrices without annotations.
- Over ~12 classes: drop the counts line, shrink the font, sort classes so confusable ones sit together, or show only the top-N confused pairs as P1 bars.
- Imbalanced classes: the counts matter — a 50% error on 4 samples is not a 50% error on 400.
- Binary problems: label the classes with their meaning ("Spam", "Not spam") and state precision and recall in the subtitle.
