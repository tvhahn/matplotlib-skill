# expect: annotation-spill
# also: text-overlap, annotation-on-data
"""Long annotation runs into the neighbouring panel."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

fig.clf()
ax, ax2 = fig.subplots(1, 2)
x = np.linspace(0, 10, 50)
ax.plot(x, np.sin(x), color="#4575b4", linewidth=2)
ax2.plot(x, np.cos(x), color="#4575b4", linewidth=2)
ax.text(0.9, 0.93, "This explanatory note is far too long for its own panel",
        transform=ax.transAxes, fontsize=10, color="dimgrey")

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
