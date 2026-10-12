# expect: clean
"""Vertical bars from zero with bar_label values and no grid."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

cats = ["Small", "Medium", "Large", "X-Large"]
bars = ax.bar(cats, [12.5, 30.1, 42.7, 18.3], color=sns.color_palette("rocket", 6)[:4])
ax.bar_label(bars, fmt="%.1f%%", padding=3, color="dimgrey", weight="semibold")
ax.grid(False)
ax.set_yticks([])

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
