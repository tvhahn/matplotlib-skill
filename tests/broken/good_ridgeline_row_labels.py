# expect: clean
"""Ridgeline: each row's fill sits on its own baseline, one median label per row."""

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402

sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
rng = np.random.default_rng(1)
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]
fig, ax = plt.subplots(figsize=(9, 7), dpi=150)
x = np.linspace(-5, 35, 200)
halo = [pe.withStroke(linewidth=3, foreground="white")]
for i, m in enumerate(months):
    base = len(months) - 1 - i
    mu = 8 + 2.5 * i
    y = np.exp(-0.5 * ((x - mu) / 3) ** 2) * 1.6
    ax.fill_between(x, base, base + y, color="#72a5b4", edgecolor="white", zorder=20 - i)
    t = ax.text(mu, base + 0.15, f"{mu:.0f}", ha="center", va="bottom", fontsize=9,
                color="dimgrey", zorder=30)
    t.set_path_effects(halo)
ax.set_yticks(range(len(months)), months[::-1])
ax.set_xlabel("Max temperature (°C)", color="dimgrey")
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey", weight="semibold")
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
sns.despine(left=True, bottom=True)
