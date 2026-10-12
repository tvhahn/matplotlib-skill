# expect: too-many-annotations
"""Five callouts crowd one panel."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

x = np.linspace(0, 10, 50)
ax.plot(x, x, color="#4575b4", linewidth=2)
for k, xi in enumerate([1, 3, 5, 7, 9]):
    ax.annotate(f"Event {chr(65 + k)} happened", xy=(xi, xi), xytext=(-70, 40),
                textcoords="offset points", fontsize=9, color="dimgrey",
                arrowprops=dict(arrowstyle="-", color="dimgrey", lw=0.8))
ax.set_ylim(-1, 14)

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
