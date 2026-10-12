# expect: clean
"""Stacked bars: upper segments start above zero, lowest at zero."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

cats = ["Q1", "Q2", "Q3", "Q4"]
a, b = np.array([10.4, 12.1, 9.3, 14.2]), np.array([5.2, 6.4, 8.1, 4.6])
ax.bar(cats, a, color="#4575b4", label="Online")
ax.bar(cats, b, bottom=a, color="#d73027", label="Store")
ax.legend(frameon=True, facecolor="white", framealpha=0.8,
          edgecolor="lightgrey", labelcolor="dimgrey", 
          loc="upper left", bbox_to_anchor=(1.02, 1))
ax.grid(axis="y", alpha=0.7, linewidth=1)

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
