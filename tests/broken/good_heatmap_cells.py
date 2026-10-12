# expect: clean
"""Annotated heatmap: auto white/black cell labels, dimgrey elsewhere."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

fig.clf()
ax = fig.add_subplot()
data = np.corrcoef(rng.normal(size=(5, 40)) + rng.normal(size=40))
labels = ["Alpha", "Bravo", "Charlie", "Delta", "Echo"]
sns.heatmap(data, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, center=0,
            square=True, linewidths=0.5, linecolor="white", ax=ax,
            xticklabels=labels, yticklabels=labels, annot_kws={"fontsize": 9})
cbar = ax.collections[0].colorbar
cbar.ax.tick_params(length=0, labelcolor="dimgrey")
cbar.set_label("Pearson r", color="dimgrey")

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
sns.despine(left=True, bottom=True, right=True)
