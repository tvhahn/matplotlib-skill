# expect: clean
"""Pivot heatmap with white labels on dark rocket cells."""

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
data = rng.uniform(40, 100, (4, 6))
sns.heatmap(data, annot=True, fmt=".0f", cmap="rocket", vmin=0, vmax=100, ax=ax,
            annot_kws={"color": "white", "fontsize": 10}, cbar=False,
            linewidths=0.5, linecolor="white")
ax.set_xlabel("Month", color="dimgrey")

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
