# expect: area-not-at-zero
"""fill_between down to 0, but the y axis starts at 90."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

x = np.linspace(0, 10, 60)
y = 100 + 10 * np.sin(x)
ax.fill_between(x, y, color="#4575b4", alpha=0.5)
ax.plot(x, y, color="#4575b4", linewidth=2)
ax.set_ylim(85, 115)

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
