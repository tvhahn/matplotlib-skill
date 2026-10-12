# expect: clean
"""Scatter with an RMSE / R^2 metric box and a bold panel letter."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

x = rng.uniform(0, 10, 120)
y = x + rng.normal(0, 1, 120)
ax.scatter(x, y, color="#446485", s=18, alpha=0.7)
ax.plot([0, 10], [0, 10], color="dimgrey", linewidth=1, linestyle="--")
rmse = np.sqrt(np.mean((y - x) ** 2))
r2 = 1 - np.sum((y - x) ** 2) / np.sum((y - y.mean()) ** 2)
ax.text(0.03, 0.95, f"RMSE = {rmse:.3f}\n$R^2$ = {r2:.3f}", transform=ax.transAxes,
        va="top", ha="left", fontsize=9, color="dimgrey")
ax.set_xlabel(r"$\bf{(a)}$  Predicted", fontsize=12, color="dimgrey")
ax.set_ylabel("Observed", fontsize=12, color="dimgrey")
ax.patch.set_edgecolor("lightgrey")
ax.patch.set_linewidth(0.8)

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
