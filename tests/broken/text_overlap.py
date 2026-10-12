# expect: text-overlap
"""Two annotations printed on top of each other."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

x = np.linspace(0, 10, 50)
ax.plot(x, np.sin(x), color="#4575b4", linewidth=2)
ax.text(2, 1.6, "First note", fontsize=11, color="dimgrey")
ax.text(2.3, 1.62, "Second note", fontsize=11, color="dimgrey")
ax.set_ylim(-1.2, 2)

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
