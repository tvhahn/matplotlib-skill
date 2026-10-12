# expect: low-contrast-text
"""Direct label in a pale series colour (#fdbf6f) has under 3:1 contrast."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

x = np.linspace(0, 10, 50)
ax.plot(x, np.sin(x), color="#fdbf6f", linewidth=2.5)
ax.annotate("Warning band", xy=(x[-1], np.sin(x[-1])), xytext=(6, 0),
            textcoords="offset points", va="center", fontsize=10, color="#fdbf6f")

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
