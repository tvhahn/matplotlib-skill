# expect: bar-not-at-zero
"""Vertical bars on a y axis that starts at 90."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

cats = ["North", "South", "East", "West"]
ax.bar(cats, [92, 95, 97, 99], color="#446485")
ax.set_ylim(90, 100)
ax.grid(axis="y", alpha=0.7, linewidth=1)

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
