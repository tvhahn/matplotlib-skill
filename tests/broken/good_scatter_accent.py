# expect: clean
"""Grey context points with one ACCENT_RED point and label."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

x, y = rng.normal(0, 1, (2, 150))
ax.scatter(x, y, color="#bdbdbd", s=18)
ax.scatter([3.2], [2.9], color="#bd0c0c", s=40)
ax.annotate("Outlier: 3.2 sd", xy=(3.2, 2.9), xytext=(-80, -30),
            textcoords="offset points",
            fontsize=10, color="#bd0c0c",
            arrowprops=dict(arrowstyle="-", color="#bd0c0c", lw=0.8))

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
