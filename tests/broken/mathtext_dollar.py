# expect: mathtext-dollar
"""Unescaped currency dollars switch on mathtext."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

ax.plot(np.linspace(6, 230, 20), np.linspace(0, 1, 20), color="#4575b4", linewidth=2)
ax.set_xlabel("Prices range from $6 to $230", fontsize=12, color="dimgrey")

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
