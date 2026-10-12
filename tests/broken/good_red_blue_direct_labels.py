# expect: clean
"""House red/blue pair with direct end labels."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

from matplotlib.ticker import MaxNLocator  # noqa: E402

x = np.arange(2000, 2021)
for name, y, c in [("Exports", 50 + 2.0 * (x - 2000), "#d73027"),
                   ("Imports", 40 + 2.6 * (x - 2000), "#4575b4")]:
    ax.plot(x, y, color=c, linewidth=2)
    ax.annotate(name, xy=(x[-1], y[-1]), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=10, color=c, weight="semibold")
ax.set_ylabel("Value ($bn)", fontsize=12, color="dimgrey")
ax.xaxis.set_major_locator(MaxNLocator(integer=True))

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold",
             pad=26)
ax.annotate("Imports overtook exports in 2017", xy=(0, 1), xycoords="axes fraction",
            xytext=(0, 8), textcoords="offset points", fontsize=10.5, color="dimgrey")
