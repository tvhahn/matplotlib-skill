# expect: cvd-collision
"""#d73027 and #555555 lines (dE 7.7 under protanopia), same style, legend only."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

x = np.linspace(0, 10, 50)
ax.plot(x, 0.5 * x, color="#d73027", linewidth=2, label="Plan")
ax.plot(x, 0.5 * x + 3, color="#555555", linewidth=2, label="Actual")
ax.legend(frameon=True, facecolor="white", framealpha=0.8,
          edgecolor="lightgrey", labelcolor="dimgrey", 
          loc="upper left", bbox_to_anchor=(1.02, 1))

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
