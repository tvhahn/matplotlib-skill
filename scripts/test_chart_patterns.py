# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "matplotlib>=3.9",
#     "seaborn>=0.13",
#     "numpy>=1.26",
#     "pandas>=2.1",
#     "scikit-learn>=1.3",
# ]
# ///
"""Test all 8 matplotlib-chart skill patterns (pattern 6 skipped) with data.

Supports two modes:
  - Synthetic (default): dummy data, same as original test harness
  - Real data (--real-data): loads curated datasets from data/raw/

Usage:
    uv run scripts/test_chart_patterns.py              # synthetic data
    uv run scripts/test_chart_patterns.py --real-data   # real datasets
"""

import argparse
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

def _find_repo_root():
    """Find the repo root by looking for data/ directory."""
    script_dir = Path(__file__).resolve().parent
    # scripts/ or scratch/ -> parent is repo root
    if (script_dir.parent / "data").is_dir():
        return script_dir.parent
    # Workspace root (clean room) -> data/ is a sibling
    if (script_dir / "data").is_dir():
        return script_dir
    return script_dir.parent


REPO_ROOT = _find_repo_root()
DATA_DIR = REPO_ROOT / "data"
OUT = REPO_ROOT / "scratch" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Pattern 1 — Horizontal Bar
# ---------------------------------------------------------------------------

def pattern_1_horizontal_bar(real_data=False):
    """Horizontal bar chart — ranked categories."""
    if real_data:
        # Use car_crashes — top 15 states by total collisions per billion miles
        df = pd.read_csv(DATA_DIR / "raw/public/car_crashes.csv")
        df = df.nlargest(12, "total")[["abbrev", "total"]].sort_values("total")
        df.columns = ["category", "percent"]
        title = "Collisions per Billion Miles (Top 12 States)"
        suffix = "car_crashes"
        fmt = "{:.1f}"
    else:
        rng = np.random.default_rng(42)
        df = pd.DataFrame({
            "category": [f"Model {chr(65+i)}" for i in range(8)],
            "percent": rng.uniform(30, 95, 8),
        }).sort_values("percent")
        title = "Accuracy by Model"
        suffix = "synthetic"
        fmt = "{:.1f}%"

    sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
    fig, ax = plt.subplots(figsize=(4, 7), dpi=300)
    sns.barplot(x="percent", y="category", hue="category", data=df, palette="Blues_d", legend=False, ax=ax)

    for p in ax.patches:
        space = 1.5
        _x = p.get_x() + p.get_width() + space
        _y = p.get_y() + p.get_height() / 2
        value = p.get_width()
        ax.text(_x, _y, fmt.format(value), ha="left", va="center",
                weight="semibold", size=10, color="dimgrey")

    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.grid(alpha=0.7, linewidth=1, axis="x")
    ax.set_xticks([0])
    ax.set_xticklabels([], alpha=0)
    ax.set_title(title, fontsize=14, loc="center")
    sns.despine(left=True, bottom=True)
    fig.savefig(OUT / f"01_horizontal_bar_{suffix}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] 1. Horizontal Bar ({suffix})")


# ---------------------------------------------------------------------------
# Pattern 2 — Vertical Bar
# ---------------------------------------------------------------------------

def pattern_2_vertical_bar(real_data=False):
    """Vertical bar chart — category values."""
    if real_data:
        # Use iowa_electricity — latest year, generation by source
        df = pd.read_csv(DATA_DIR / "raw/public/iowa_electricity.csv")
        latest_year = df["year"].max()
        df = df[df["year"] == latest_year][["source", "net_generation"]]
        df.columns = ["category", "value"]
        df["value"] = df["value"] / 1000  # Convert to thousands
        title = f"Iowa Electricity Generation ({latest_year[:4]}, GWh)"
        suffix = "iowa_electricity"
    else:
        rng = np.random.default_rng(42)
        df = pd.DataFrame({
            "category": [f"Feature {i+1}" for i in range(6)],
            "value": rng.uniform(0.1, 0.9, 6),
        })
        title = r"$\bf{(a)}$" + " Correlation Values"
        suffix = "synthetic"

    sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    sns.barplot(x="category", y="value", hue="category", data=df, palette="rocket", legend=False, ax=ax)

    for i, p in enumerate(ax.patches):
        space = abs(df["value"].max()) * 0.1
        value = p.get_height()
        _y = p.get_y() + p.get_height() + space
        _x = p.get_x() + p.get_width() / 2
        ax.text(_x, _y, f"{value:.1f}", ha="center", va="center",
                weight="semibold", size=12, color="dimgrey")

    sns.despine(left=True, bottom=True)
    ax.grid(alpha=0.7, linewidth=1, axis="y")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(title, loc="left", fontsize=15, pad=20)
    fig.savefig(OUT / f"02_vertical_bar_{suffix}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] 2. Vertical Bar ({suffix})")


# ---------------------------------------------------------------------------
# Pattern 3 — Time Series
# ---------------------------------------------------------------------------

def pattern_3_time_series(real_data=False):
    """Time series + predictions."""
    if real_data:
        # Use global_temp — annual average anomalies
        df = pd.read_csv(DATA_DIR / "raw/public/global_temp.csv")
        # Compute annual average
        annual = df.groupby("Year")["Anomaly"].mean().reset_index()
        annual = annual.sort_values("Year")
        years = annual["Year"].values
        anomaly = annual["Anomaly"].values

        sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        ax.grid(False)

        ax.scatter(years, anomaly, alpha=0.4, c="grey", edgecolors="none", s=8,
                   label="Annual Mean")

        # 10-year rolling average
        window_size = 10
        rolling_avg = np.convolve(anomaly, np.ones(window_size), "valid") / window_size
        ax.plot(years[window_size - 1:], rolling_avg,
                color="#d73027", alpha=1, label=f"{window_size}-Year Rolling Avg", linewidth=2)

        # Linear trend
        z = np.polyfit(years, anomaly, 1)
        trend = np.polyval(z, years)
        ax.plot(years, trend, color="#4575b4", linewidth=1, linestyle="--",
                label="Linear Trend", alpha=0.8)

        # Metric annotation
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        ax.text(
            (x_max - x_min) * 0.03 + x_min,
            y_max - (y_max - y_min) * 0.05,
            f"Trend: {z[0]:.4f} \u00b0C/year\nTotal: {z[0] * (years[-1] - years[0]):.2f} \u00b0C",
            fontsize=9, fontweight="normal",
            verticalalignment="top", horizontalalignment="left",
            bbox={"facecolor": "gray", "alpha": 0.0, "pad": 6},
        )

        ax.set_xlabel("Year")
        ax.set_ylabel("Temperature Anomaly (\u00b0C)")
        ax.legend(loc="lower right", fontsize=10, frameon=True, facecolor="white",
                  framealpha=0.8, edgecolor="lightgrey")
        ax.set_title(r"$\bf{(a)}$" + " GISTEMP Global Temperature Anomaly",
                      loc="left", pad=7)
        suffix = "global_temp"
    else:
        rng = np.random.default_rng(42)
        n = 200
        t = np.linspace(0, 4 * np.pi, n)
        y_true_sorted = np.sin(t) + 0.5 * t / t.max()
        y_pred_sorted = y_true_sorted + rng.normal(0, 0.15, n)

        sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        ax.grid(False)

        ax.plot(y_true_sorted, label="True Values", alpha=1, color="#4575b4", linewidth=1, zorder=0)
        ax.scatter(np.arange(len(y_pred_sorted)), y_pred_sorted, label="Predicted",
                   alpha=0.4, c="grey", edgecolors="none", s=2)

        window_size = 12
        rolling_avg = np.convolve(y_pred_sorted, np.ones(window_size), "valid") / window_size
        ax.plot(np.arange(len(y_pred_sorted))[window_size - 1:], rolling_avg,
                color="#d73027", alpha=1, label="Rolling Avg", linewidth=1.5)

        rmse = 0.15
        r2 = 0.92
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        ax.text(
            (x_max - x_min) * 0.03 + x_min,
            y_max - (y_max - y_min) * 0.05,
            f"RMSE = {rmse:.3f}\n$R^2$ = {r2:.3f}",
            fontsize=9, fontweight="normal",
            verticalalignment="top", horizontalalignment="left",
            bbox={"facecolor": "gray", "alpha": 0.0, "pad": 6},
        )

        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.legend(loc="lower right", fontsize=10, frameon=True, facecolor="white",
                  framealpha=0.8, edgecolor="lightgrey")
        ax.set_title(r"$\bf{(a)}$" + " Prediction Results", loc="left", pad=7)
        suffix = "synthetic"

    fig.savefig(OUT / f"03_time_series_{suffix}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] 3. Time Series ({suffix})")


# ---------------------------------------------------------------------------
# Pattern 4 — Violin + Strip
# ---------------------------------------------------------------------------

def pattern_4_violin_strip(real_data=False):
    """Violin + strip plot — distributions by category."""
    if real_data:
        # Use penguins — body mass by species
        df = pd.read_csv(DATA_DIR / "raw/public/penguins.csv")
        df = df.dropna(subset=["body_mass_g", "species"])
        plot_df = df[["species", "body_mass_g"]].copy()
        plot_df.columns = ["category", "value"]
        title = r"$\bf{(a)}$" + " Penguin Body Mass by Species"
        xlabel = "Body Mass (g)"
        suffix = "penguins"
    else:
        rng = np.random.default_rng(42)
        categories = ["Group A", "Group B", "Group C", "Group D"]
        data = []
        for cat in categories:
            values = rng.normal(loc=rng.uniform(2, 8), scale=rng.uniform(0.5, 2), size=50)
            data.extend({"category": cat, "value": v} for v in values)
        plot_df = pd.DataFrame(data)
        title = r"$\bf{(a)}$" + " Distribution Comparison"
        xlabel = "Value"
        suffix = "synthetic"

    sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)

    sns.violinplot(
        x="value", y="category", data=plot_df,
        density_norm="width", inner=None, linewidth=2,
        color="white", saturation=1, cut=0,
        orient="h", zorder=0, width=0.8, ax=ax,
    )
    sns.stripplot(
        x="value", y="category", data=plot_df,
        size=6, jitter=0.2, color="black", linewidth=0.5,
        marker="o", edgecolor=None, alpha=0.1,
        zorder=4, orient="h", ax=ax,
    )

    ax.grid(axis="x", alpha=0.5)
    ax.yaxis.label.set_visible(False)
    ax.tick_params(axis="x", labelsize=12)
    ax.set_xlabel(xlabel, labelpad=10, fontsize=12)
    ax.set_title(title, fontsize=12, loc="left")
    sns.despine(bottom=True, left=True)
    fig.savefig(OUT / f"04_violin_strip_{suffix}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] 4. Violin + Strip ({suffix})")


# ---------------------------------------------------------------------------
# Pattern 5 — Lollipop / Dumbbell
# ---------------------------------------------------------------------------

def pattern_5_lollipop(real_data=False):
    """Lollipop / dumbbell chart — min/avg/max ranges."""
    if real_data:
        # Use healthexp — spending range per country (min/avg/max across years)
        df = pd.read_csv(DATA_DIR / "raw/public/healthexp.csv")
        stats = df.groupby("Country")["Spending_USD"].agg(["min", "mean", "max"]).reset_index()
        stats.columns = ["name", "min", "avg", "max"]
        # Scale to thousands for readability
        for col in ["min", "avg", "max"]:
            stats[col] = stats[col] / 1000
        stats = stats.sort_values("avg")
        title = "Health Expenditure per Capita (USD thousands)"
        suffix = "healthexp"
    else:
        rng = np.random.default_rng(42)
        names = ["Random Forest", "SVM", "XGBoost", "LightGBM", "Neural Net"]
        avgs = rng.uniform(0.75, 0.95, 5)
        mins = avgs - rng.uniform(0.03, 0.08, 5)
        maxs = avgs + rng.uniform(0.03, 0.08, 5)
        stats = pd.DataFrame({"name": names, "avg": avgs, "min": mins, "max": maxs})
        title = None
        suffix = "synthetic"

    pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)
    darkblue = pal[5]
    lightblue = pal[2]

    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    DOT_SIZE = 150

    ax.scatter(x=stats["avg"], y=stats["name"], s=DOT_SIZE, alpha=1,
               label="Average", color=lightblue, edgecolors="white")
    ax.scatter(x=stats["min"], y=stats["name"], s=DOT_SIZE, alpha=1,
               color=darkblue, label="Min/Max", edgecolors="white")
    ax.scatter(x=stats["max"], y=stats["name"], s=DOT_SIZE, alpha=1,
               color=darkblue, edgecolors="white")

    ax.hlines(y=stats["name"], xmin=stats["min"], xmax=stats["max"],
              color="grey", alpha=0.4, lw=4, zorder=0)

    for i in range(stats.shape[0]):
        ax.text(x=stats["avg"].iloc[i], y=i + 0.15, s=f'{stats["avg"].iloc[i]:.2f}',
                ha="center", va="bottom", size="x-large",
                color="dimgrey", weight="medium")

    ax.grid(False)
    sns.despine(left=True, bottom=True)
    ax.tick_params(axis="x", pad=20, labelsize="x-large", labelcolor="dimgrey")

    legend = ax.legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
                       bbox_to_anchor=(0.6, 1.05), ncol=2, fontsize="x-large")
    for text in legend.get_texts():
        text.set_color("dimgrey")

    if title:
        ax.set_title(title, fontsize=14, pad=40)

    fig.savefig(OUT / f"05_lollipop_{suffix}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] 5. Lollipop / Dumbbell ({suffix})")


# ---------------------------------------------------------------------------
# Pattern 7 — Heatmap / Spectrogram
# ---------------------------------------------------------------------------

def pattern_7_heatmap(real_data=False):
    """Heatmap / spectrogram — two 2D arrays."""
    if real_data:
        # Use global_temp — year x month heatmap
        df = pd.read_csv(DATA_DIR / "raw/public/global_temp.csv")
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        pivot = df.pivot_table(index="Year", columns="Month", values="Anomaly")
        # Reorder months
        available = [m for m in month_order if m in pivot.columns]
        pivot = pivot[available]
        # Take last 60 years for readability
        pivot = pivot.loc[pivot.index >= pivot.index.max() - 60]

        fig, ax = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

        # Full heatmap
        im0 = ax[0].pcolormesh(
            range(len(available)), pivot.index.values, pivot.values,
            cmap="RdBu_r", shading="auto",
        )
        ax[0].set_xticks(range(len(available)))
        ax[0].set_xticklabels(available, rotation=45, ha="right")
        ax[0].set_ylabel("Year")
        ax[0].tick_params(axis="both", which="both", length=0)
        ax[0].set_title(r"$\bf{(a)}$" + " Monthly Temperature Anomaly (\u00b0C)",
                        loc="left", fontsize=12)
        fig.colorbar(im0, ax=ax[0], shrink=0.8)

        # Decade averages
        pivot_decade = pivot.copy()
        pivot_decade["decade"] = (pivot_decade.index // 10) * 10
        decade_avg = pivot_decade.groupby("decade")[available].mean()

        im1 = ax[1].pcolormesh(
            range(len(available)), decade_avg.index.values, decade_avg.values,
            cmap="RdBu_r", shading="auto",
        )
        ax[1].set_xticks(range(len(available)))
        ax[1].set_xticklabels(available, rotation=45, ha="right")
        ax[1].set_ylabel("Decade")
        ax[1].tick_params(axis="both", which="both", length=0)
        ax[1].set_title(r"$\bf{(b)}$" + " Decade Average", loc="left", fontsize=12)
        fig.colorbar(im1, ax=ax[1], shrink=0.8)

        suffix = "global_temp"
    else:
        rng = np.random.default_rng(42)
        freq_axis = np.linspace(0, 5000, 64)
        time_axis = np.linspace(0, 30, 100)
        data = rng.random((64, 100))
        bins = np.arange(16)
        binned_data = rng.random((16, 100))

        fig, ax = plt.subplots(1, 2, figsize=(11, 4), dpi=300)

        ax[0].pcolormesh(time_axis, freq_axis, data, cmap="inferno",
                         vmax=0.9, shading="auto")
        ax[0].set_ylabel("Frequency (Hz)")
        ax[0].set_xlabel("Runtime (days)")
        ax[0].tick_params(axis="both", which="both", length=0)
        ax[0].set_title(r"$\bf{(a)}$" + " Spectrogram", loc="left", fontsize=12)

        ax[1].pcolormesh(time_axis, bins, binned_data, cmap="inferno",
                         vmax=0.9, shading="auto")
        ax[1].set_xlabel("Runtime (days)")
        ax[1].set_ylabel("Frequency Bin")
        ax[1].tick_params(axis="both", which="both", length=0)
        ax[1].set_title(r"$\bf{(b)}$" + " Binned", loc="left", fontsize=12)
        suffix = "synthetic"

    sns.despine(left=True, bottom=True, right=True)
    fig.savefig(OUT / f"07_heatmap_{suffix}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] 7. Heatmap / Spectrogram ({suffix})")


# ---------------------------------------------------------------------------
# Pattern 8 — Multi-Panel Grid
# ---------------------------------------------------------------------------

def pattern_8_multi_panel(real_data=False):
    """Multi-panel grid (3x3) — per-panel data."""
    if real_data:
        # Use healthexp — one panel per country, spending over time
        df = pd.read_csv(DATA_DIR / "raw/public/healthexp.csv")
        countries = sorted(df["Country"].unique())
        n_panels = min(len(countries), 9)
        countries = countries[:n_panels]
        nrows = int(np.ceil(n_panels / 3))
        ncols = min(n_panels, 3)

        sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
        fig = plt.figure(figsize=(14, 4 * nrows), dpi=300)
        gs = gridspec.GridSpec(nrows, ncols)
        axes_list = [plt.subplot(gs[i // ncols, i % ncols]) for i in range(n_panels)]
        gs.update(wspace=0.25, hspace=0.4)

        labels = [chr(ord('a') + i) for i in range(n_panels)]

        for i, (ax, label, country) in enumerate(zip(axes_list, labels, countries)):
            ax.grid(False)
            ax.patch.set_edgecolor("lightgrey")
            ax.patch.set_linewidth(0.8)

            cdf = df[df["Country"] == country].sort_values("Year")
            ax.plot(cdf["Year"], cdf["Spending_USD"], color="#4575b4", linewidth=1.5)

            if "Life_Expectancy" in cdf.columns:
                ax2 = ax.twinx()
                ax2.plot(cdf["Year"], cdf["Life_Expectancy"], color="#d73027",
                         linewidth=1, alpha=0.6, linestyle="--")
                ax2.set_ylabel("Life Exp.", fontsize=8, color="#d73027")
                ax2.tick_params(axis="y", labelsize=7, colors="#d73027")
                sns.despine(ax=ax2, left=True, bottom=True, right=False)

            ax.set_title(r"$\bf{(" + label + r")}$" + f" {country}", loc="left", pad=7)

            if i == 0:
                ax.set_xlabel("Year")
                ax.set_ylabel("Spending (USD)")
            else:
                ax.set_xlabel("")
                ax.set_ylabel("")

        suffix = "healthexp"
    else:
        rng = np.random.default_rng(42)

        sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
        fig = plt.figure(figsize=(14, 12), dpi=300)
        gs = gridspec.GridSpec(3, 3)
        axes_list = [plt.subplot(gs[i, j]) for i in range(3) for j in range(3)]
        gs.update(wspace=0.15, hspace=0.4)

        labels = [chr(ord('a') + i) for i in range(9)]
        max_hours = [7.8, 2.5, 1.4, 2.4, 2.2, 4.5, 5.0, 3.3, 1.0]
        titles = [
            "Train Results (Bearing1_1)", "Train Results (Bearing2_1)", "Train Results (Bearing3_1)",
            "Val Results (Bearing1_2)", "Val Results (Bearing2_2)", "Val Results (Bearing3_2)",
            "Test Results (Bearing1_3)", "Test Results (Bearing2_3)", "Test Results (Bearing3_3)",
        ]

        for i, (ax, label, title) in enumerate(zip(axes_list, labels, titles)):
            ax.grid(False)
            ax.patch.set_edgecolor("lightgrey")
            ax.patch.set_linewidth(0.8)

            n = 200
            t = np.linspace(0, max_hours[i], n)
            y_true = 100 * t / max_hours[i]
            noise_scale = 5 + 10 * (t / max_hours[i])
            y_pred = y_true + rng.normal(0, noise_scale, n)
            y_pred = np.clip(y_pred, 0, 110)

            ax.plot(t, y_true, color="#4575b4", linewidth=1, zorder=0,
                    label="True Life Percentage" if i == 0 else None)
            ax.scatter(t, y_pred, alpha=0.4, c="grey", edgecolors="none", s=2,
                       label="Predicted Life Percentage" if i == 0 else None, zorder=1)

            window = 12
            rolling = np.convolve(y_pred, np.ones(window), "valid") / window
            ax.plot(t[window - 1:], rolling, color="#d73027", linewidth=0.5,
                    label="2min Rolling Avg" if i == 0 else None, zorder=2)

            rmse = np.sqrt(np.mean((y_pred - y_true) ** 2)) / 100
            r2 = 1 - np.sum((y_pred - y_true) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2)
            x_min, x_max = ax.get_xlim()
            y_min, y_max = ax.get_ylim()
            ax.text(
                (x_max - x_min) * 0.03 + x_min,
                y_max - (y_max - y_min) * 0.05,
                f"RMSE = {rmse:.3f}\n$R^2$ = {r2:.3f}",
                fontsize=9, fontweight="normal",
                verticalalignment="top", horizontalalignment="left",
                bbox={"facecolor": "gray", "alpha": 0.0, "pad": 6},
            )

            ax.set_title(r"$\bf{(" + label + r")}$" + f" {title}", loc="left", pad=7)

            if i == 0:
                ax.set_xlabel("Runtime (hours)")
                ax.set_ylabel("Life Percentage")
                ax.legend(loc="lower right", fontsize=10, frameon=True,
                          facecolor="white", framealpha=0.8, edgecolor="lightgrey")
            else:
                ax.set_yticklabels([])

        suffix = "synthetic"

    sns.despine(left=True, bottom=True)
    fig.savefig(OUT / f"08_multi_panel_{suffix}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] 8. Multi-Panel Grid ({suffix})")


# ---------------------------------------------------------------------------
# Pattern 9 — PR/ROC Curves
# ---------------------------------------------------------------------------

def pattern_9_pr_roc(real_data=False):
    """PR/ROC curves — classification evaluation."""
    if real_data:
        # Use breast_cancer — real binary classification with cross-validation
        from sklearn.datasets import load_breast_cancer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import StratifiedKFold
        from sklearn.metrics import precision_recall_curve, roc_curve

        data = load_breast_cancer()
        X, y = data.data, data.target
        # Invert so malignant=1 (positive class)
        y = 1 - y

        kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        precision_curves, recall_curves = [], []
        tpr_curves, fpr_curves = [], []

        for train_idx, test_idx in kf.split(X, y):
            clf = LogisticRegression(max_iter=5000, random_state=42)
            clf.fit(X[train_idx], y[train_idx])
            y_prob = clf.predict_proba(X[test_idx])[:, 1]

            prec, rec, _ = precision_recall_curve(y[test_idx], y_prob)
            precision_curves.append(prec)
            recall_curves.append(rec)

            fpr, tpr, _ = roc_curve(y[test_idx], y_prob)
            fpr_curves.append(fpr)
            tpr_curves.append(tpr)

        baseline = y.mean()
        title_pr = "Precision-Recall (Breast Cancer)"
        title_roc = "ROC (Breast Cancer)"
        suffix = "breast_cancer"
    else:
        rng = np.random.default_rng(42)
        n_folds = 5

        precision_curves = []
        recall_curves = []
        for _ in range(n_folds):
            recall = np.sort(rng.uniform(0, 1, 50))
            precision = 1 - recall * rng.uniform(0.3, 0.7) + rng.normal(0, 0.05, 50)
            precision = np.clip(precision, 0.1, 1.0)
            precision_curves.append(precision)
            recall_curves.append(recall)

        tpr_curves = []
        fpr_curves = []
        for _ in range(n_folds):
            fpr = np.sort(rng.uniform(0, 1, 50))
            tpr = fpr + rng.uniform(0.1, 0.4) * (1 - fpr) + rng.normal(0, 0.03, 50)
            tpr = np.clip(tpr, 0, 1)
            tpr_curves.append(tpr)
            fpr_curves.append(fpr)

        baseline = 0.3
        title_pr = "Precision-Recall Curve"
        title_roc = "ROC Curve"
        suffix = "synthetic"

    sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True, dpi=300)
    fig.tight_layout(pad=5.0)
    pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)

    # PR curve panel
    for i, (p, r) in enumerate(zip(precision_curves, recall_curves)):
        label = "k-fold model" if i == len(precision_curves) - 1 else None
        axes[0].plot(r, p, color="gray", alpha=0.5, linewidth=1, label=label)

    # Average PR (interpolated for real data which has variable lengths)
    if real_data:
        common_recall = np.linspace(0, 1, 100)
        interp_precisions = []
        for p, r in zip(precision_curves, recall_curves):
            interp_p = np.interp(common_recall, r[::-1], p[::-1])
            interp_precisions.append(interp_p)
        avg_prec = np.mean(interp_precisions, axis=0)
        axes[0].plot(common_recall, avg_prec, label="Average model",
                     color=pal[5], linewidth=2)
    else:
        recall_avg = np.mean(recall_curves, axis=0)
        precision_avg = np.mean(precision_curves, axis=0)
        axes[0].plot(recall_avg, precision_avg, label="Average model",
                     color=pal[5], linewidth=2)

    axes[0].plot([0, 1], [baseline, baseline], linestyle="--",
                 label="No skill model", color="orange", linewidth=2, zorder=0)
    axes[0].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey")
    axes[0].set_title(title_pr)
    axes[0].set_xlabel("Recall")
    axes[0].set_ylabel("Precision")

    # ROC curve panel
    for i, (t, f) in enumerate(zip(tpr_curves, fpr_curves)):
        label = "k-fold models" if i == len(tpr_curves) - 1 else None
        axes[1].plot(f, t, color="grey", alpha=0.5, linewidth=1, label=label)

    if real_data:
        common_fpr = np.linspace(0, 1, 100)
        interp_tprs = []
        for t, f in zip(tpr_curves, fpr_curves):
            interp_t = np.interp(common_fpr, f, t)
            interp_tprs.append(interp_t)
        avg_tpr = np.mean(interp_tprs, axis=0)
        axes[1].plot(common_fpr, avg_tpr, label="Average of k-folds",
                     color=pal[5], linewidth=2)
    else:
        fpr_avg = np.mean(fpr_curves, axis=0)
        tpr_avg = np.mean(tpr_curves, axis=0)
        axes[1].plot(fpr_avg, tpr_avg, label="Average of k-folds",
                     color=pal[5], linewidth=2)

    axes[1].plot([0, 1], [0, 1], linestyle="--",
                 label="No skill", color="orange", linewidth=2, zorder=0)
    axes[1].legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey")
    axes[1].set_title(title_roc)
    axes[1].set_xlabel("False Positive Rate")
    axes[1].set_ylabel("True Positive Rate")

    for ax in axes.flatten():
        ax.yaxis.set_tick_params(labelleft=True, which="major")
        ax.grid(False)

    fig.savefig(OUT / f"09_pr_roc_{suffix}.png", bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] 9. PR/ROC Curves ({suffix})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Test matplotlib-chart skill patterns")
    parser.add_argument("--real-data", action="store_true",
                        help="Use real datasets from data/raw/ instead of synthetic data")
    args = parser.parse_args()

    mode = "real" if args.real_data else "synthetic"
    print(f"Testing 8 chart patterns (pattern 6 skipped) with {mode} data...\n")

    pattern_1_horizontal_bar(real_data=args.real_data)
    pattern_2_vertical_bar(real_data=args.real_data)
    pattern_3_time_series(real_data=args.real_data)
    pattern_4_violin_strip(real_data=args.real_data)
    pattern_5_lollipop(real_data=args.real_data)
    pattern_7_heatmap(real_data=args.real_data)
    pattern_8_multi_panel(real_data=args.real_data)
    pattern_9_pr_roc(real_data=args.real_data)

    print(f"\nAll figures saved to {OUT.resolve()}")


if __name__ == "__main__":
    main()
