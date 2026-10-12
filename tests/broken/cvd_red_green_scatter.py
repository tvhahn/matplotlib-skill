# expect: cvd-collision
"""Red and green dots with the same marker collapse under deuteranopia."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

a, b = rng.normal(0, 1, (2, 60)), rng.normal(3, 1, (2, 60))
ax.scatter(*a, color="#d73027", s=30, label="Group A")
ax.scatter(*b, color="#33a02c", s=30, label="Group B")
ax.legend(frameon=True, facecolor="white", framealpha=0.8,
          edgecolor="lightgrey", labelcolor="dimgrey", 
          loc="upper left", bbox_to_anchor=(1.02, 1))

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
