# expect: clean
"""Ranked horizontal bars with the category axis inverted."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

cats = ["Alpha", "Bravo", "Charlie", "Delta"]
vals = [95, 85, 80, 70]
bars = ax.barh(cats, vals, color="#446485")
ax.invert_yaxis()
ax.bar_label(bars, padding=3, color="dimgrey", weight="semibold")
ax.axvline(0, color="lightgrey", linewidth=0.8, zorder=0)
ax.grid(False)

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
