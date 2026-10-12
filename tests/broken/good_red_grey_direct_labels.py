# expect: clean
"""#d73027 vs #555555 (protan dE 7.7) is fine once each line is labelled."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

x = np.linspace(0, 10, 50)
for name, y, c in [("Plan", 0.5 * x, "#d73027"), ("Actual", 0.5 * x + 3, "#555555")]:
    ax.plot(x, y, color=c, linewidth=2)
    ax.annotate(name, xy=(x[-1], y[-1]), xytext=(6, 0), textcoords="offset points",
                va="center", fontsize=10, color=c, weight="semibold")

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
