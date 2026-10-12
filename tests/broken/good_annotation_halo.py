# expect: clean
"""Label over a dense point cloud, with a white halo."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

import matplotlib.patheffects as pe  # noqa: E402

pts = rng.normal(0, 1, (2, 400))
ax.scatter(*pts, color="#4575b4", s=12)
t = ax.text(0, 0, "Dense centre", ha="center", va="center", fontsize=11,
            color="dimgrey")
t.set_path_effects([pe.withStroke(linewidth=3, foreground="white")])

ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
for a in fig.get_axes():
    a.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
