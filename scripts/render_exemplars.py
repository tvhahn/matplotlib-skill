# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "matplotlib",
#     "seaborn",
#     "numpy",
#     "pandas",
# ]
# ///
"""Render the skill's exemplar PNGs from its own pattern templates.

Each exemplar runs a pattern's ```python block on a real dataset, swaps the
template's placeholder title/labels for real ones, lints it with
check_figure.py, and writes a small PNG to skills/matplotlib/exemplars/.
Exemplars therefore always match the current templates: re-run this after
changing a pattern.

    uv run scripts/render_exemplars.py            # all
    uv run scripts/render_exemplars.py P1 P8      # by prefix

Two exemplars per pattern on different data, so the model sees what stays
fixed (the Signature) and what adapts to the data.
"""

import re
import shutil
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "matplotlib"
RAW = REPO / "data" / "raw"
OUT = SKILL / "exemplars"
sys.path.insert(0, str(SKILL / "scripts"))
import check_figure  # noqa: E402

BLOCK_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)
DPI = 80  # small on purpose: the model reads these, every pixel costs tokens


def csv(df, tmp, name="data.csv"):
    df.to_csv(tmp / name, index=False)


def pub(name):
    return pd.read_csv(RAW / "public" / name)


# --------------------------------------------------------------------------- data setups
# Exemplar data must never overlap a benchmark prompt's data (tests enforce it:
# an exemplar on the prompt's own data is a worked answer, and models copy it).
# Each setup returns extra globals for the template (most read ./data.csv).


def p1_crashes(tmp):
    d = pub("car_crashes.csv").nlargest(10, "total")
    return {"df": d.rename(columns={"abbrev": "category", "total": "value"})[["category", "value"]]}


def p1_planets(tmp):
    d = pub("planets.csv")["method"].value_counts().head(8).rename_axis("category")
    return {"df": d.reset_index(name="value")}


def p2_mtcars(tmp):
    return {"raw": pub("mtcars.csv").rename(columns={"cyl": "category", "mpg": "value"})}


def p2_iris(tmp):
    return {"raw": pub("iris.csv").rename(
        columns={"target_name": "category", "petal length (cm)": "value"})}


def precomp(folder, name, ext="csv", dest="data"):
    def f(tmp):
        shutil.copy(RAW / f"precomputed/{folder}/{name}.{ext}", tmp / f"{dest}.{ext}")
        return {}
    return f


def p4_weibull(tmp):
    d = pd.read_csv(RAW / "weibull/femto_results_filtered.csv")
    d["category"] = np.where(d["loss_func"].str.contains("weibull"), "Weibull-informed loss",
                             "Traditional loss")
    csv(d.rename(columns={"epoch_stopped_on": "value"})[["category", "value"]], tmp)
    return {}


def p4_iris(tmp):
    csv(pub("iris.csv").rename(columns={"target_name": "category",
                                        "sepal width (cm)": "value"}), tmp)
    return {}


def p5_classifiers(tmp):
    d = pd.read_csv(RAW / "beautiful-plots/best_results.csv")
    d["name"] = d["clf_name"].str.replace("_classifier", "").str.replace("_", " ").str.title()
    csv(d.rename(columns={"auc_min": "min", "auc_max": "max", "auc_avg": "avg"})[
        ["name", "min", "max", "avg"]], tmp)
    return {}


def p5_flights(tmp):
    d = pub("flights.csv").groupby("year")["passengers"].agg(["min", "max", "mean"])
    d = d.rename(columns={"mean": "avg"}).reset_index().rename(columns={"year": "name"})
    d["name"] = d["name"].astype(str)
    csv(d, tmp)
    return {}


def p8_fmri(tmp):
    d = pub("fmri.csv")
    d["group"] = d["region"].str.title() + ", " + d["event"]
    csv(d.rename(columns={"timepoint": "x", "signal": "y"}), tmp)
    return {}


def p8_flights(tmp):
    d = pub("flights.csv")
    d = d[d["year"].isin([1949, 1952, 1955, 1958, 1960])]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    d["x"] = d["month"].map({m: i + 1 for i, m in enumerate(months)})
    csv(d.rename(columns={"year": "group", "passengers": "y"})[["group", "x", "y"]], tmp)
    return {}






def p9(name):
    def f(tmp):
        (tmp / "data/raw/precomputed/p9").mkdir(parents=True)
        shutil.copy(RAW / f"precomputed/p9/{name}.npz", tmp / "data/raw/precomputed/p9/dataset.npz")
        return {}
    return f


def p10_flights(tmp):
    d = pub("flights.csv")
    d = d[d["year"].isin([1949, 1960])]
    csv(d.rename(columns={"month": "item", "year": "period", "passengers": "value"}), tmp)
    return {}


def p10_planets(tmp):
    d = pub("planets.csv")
    d = d[d["year"].between(2000, 2004) | d["year"].between(2010, 2014)]
    d["period"] = np.where(d["year"] < 2005, "2000–04", "2010–14")
    d = d.groupby(["method", "period"]).size().unstack(fill_value=0)  # no discoveries = 0
    d = d.loc[d.sum(axis=1).nlargest(5).index].stack().reset_index(name="value")
    csv(d.rename(columns={"method": "item"}), tmp)
    return {}




def p11_mtcars(tmp):
    d = pub("mtcars.csv")
    d["group"] = d["cyl"].astype(str) + " cylinders"
    d["component"] = d["am"].map({1: "Manual", 0: "Automatic"})
    csv(d[["group", "component"]], tmp)
    return {}


def p11_planets(tmp):
    d = pub("planets.csv")
    d = d[d["year"] >= 1995]
    d["component"] = d["method"].where(d["method"].isin(["Radial Velocity", "Transit"]), "Other")
    d = d.groupby(["year", "component"]).size().reset_index(name="value")
    csv(d.rename(columns={"year": "x"}), tmp)
    return {}


def p12_geyser(tmp):
    d = pub("geyser.csv")
    d["group"] = d["kind"].str.title() + " eruptions"
    csv(d.rename(columns={"waiting": "value"})[["group", "value"]], tmp)
    return {}


def p12_diamonds(tmp):
    d = pub("diamonds.csv").sort_values("color")  # file order D→J = grade order
    d["group"] = "Grade " + d["color"]
    csv(d.rename(columns={"price": "value"})[["group", "value"]], tmp)
    return {}


def oc_flights(tmp):
    d = pub("flights.csv")
    d = d[d["month"].isin(["Jul", "Mar", "Nov"])]
    d["date"] = pd.to_datetime(d["year"].astype(str) + "-01-01")
    csv(d.rename(columns={"month": "series", "passengers": "value"})[["date", "series", "value"]], tmp)
    return {}




def oc_mtcars(tmp):
    d = pub("mtcars.csv")
    d["group"] = d["cyl"].astype(str) + " cylinders"
    csv(d.rename(columns={"wt": "x", "mpg": "y"}), tmp)
    return {}


def oc_geyser(tmp):
    csv(pub("geyser.csv").rename(columns={"waiting": "value"}), tmp)
    return {}


def oc_mtcars_grouped(tmp):
    d = pub("mtcars.csv")
    d["group"] = d["cyl"].astype(str) + " cyl"
    d["subgroup"] = d["am"].map({1: "Manual", 0: "Automatic"})
    csv(d.rename(columns={"mpg": "value"}), tmp)
    return {}


# --------------------------------------------------------------------------- catalogue
# (name, pattern file stem, block index, setup, [(placeholder, replacement)], sources)
# `sources` are the raw datasets the exemplar is drawn from, by file stem.

EXEMPLARS = [
    ("P1-a", "P1-horizontal-bar", 0, p1_crashes, [
        ("Chart Title", "Fatal Collisions per Billion Miles — Top 10 States"),
        ('fmt = "{:.1f}%"', 'fmt = "{:.1f}"')], ["car_crashes"]),
    ("P1-b", "P1-horizontal-bar", 0, p1_planets, [
        ("Chart Title", "Exoplanets Discovered by Method, 1989–2014"),
        ('fmt = "{:.1f}%"', 'fmt = "{:,.0f}"')], ["planets"]),
    ("P2-a", "P2-vertical-bar", 0, p2_mtcars, [
        ("Chart Title", "Average Fuel Economy (mpg) by Number of Cylinders"),
        ('"Category label"', '"Cylinders"'),
        (" averages {hi", "-cylinder cars average {hi"),
        ("""f'{label(lo["category"])}',""", """f'the {label(lo["category"])}-cylinder',""")],
     ["mtcars"]),
    ("P2-b", "P2-vertical-bar", 0, p2_iris, [
        ("Chart Title", "Average Petal Length (cm) by Iris Species"),
        ('"Category label"', '"Species"')], ["iris"]),
    ("P3-a", "P3-time-series", 0, precomp("p3", "co2_concentration"), [
        ("Chart Title", "Atmospheric CO₂ at Mauna Loa, 1958–2019"),
        ("Y-Axis Label (unit)", "CO₂ concentration (ppm)")], ["co2_concentration"]),
    ("P3-b", "P3-time-series", 0, precomp("p3", "birth_percentage"), [
        ("Chart Title", "Births Above the Monthly Average, 1981–2019"),
        ("Y-Axis Label (unit)", "Births above average (%)"),
        ('loc="upper left", fontsize=10', 'loc="upper right", fontsize=10')], ["birth_percentage"]),
    ("P4-a", "P4-violin-strip", 0, p4_weibull, [
        ("Chart Title", "Early-Stopping Epoch by Loss Function — FEMTO Bearings"),
        ("Value (units)", "Epoch training stopped on"),
        ("units above", "epochs above")], ["femto_results_filtered"]),
    ("P4-b", "P4-violin-strip", 0, p4_iris, [
        ("Chart Title", "Iris Sepal Width by Species"),
        ("Value (units)", "Sepal width (cm)"),
        ("units above", "cm above"),
        ('f"{med:,.0f}"', 'f"{med:,.1f}"'), ("{gap:,.0f}", "{gap:,.1f}")], ["iris"]),
    ("P5-a", "P5-lollipop", 0, p5_classifiers, [
        ("Chart Title", "Classifier PR-AUC Across Cross-Validation Folds"),
        ("Score (units)", "PR-AUC")], ["best_results"]),
    ("P5-b", "P5-lollipop", 0, p5_flights, [
        ("Chart Title", "Monthly Airline Passengers by Year, 1949–1960"),
        ("Score (units)", "Passengers per month (thousands)")], ["flights"]),
    ("P6-a", "P6-decision-boundary", 0, precomp("p6", "iris", "npz"), [
        ("KNN Decision Boundary — Dataset Name", "KNN Decision Boundary — Iris Species"),
        ('r"$x_1$"', '"Petal width (cm)"'), ('r"$x_0$"', '"Petal length (cm)"')], ["iris"]),
    ("P6-b", "P6-decision-boundary", 0, precomp("p6", "geyser", "npz"), [
        ("KNN Decision Boundary — Dataset Name", "KNN Decision Boundary — Old Faithful Eruptions"),
        ('r"$x_1$"', '"Waiting time (min)"'), ('r"$x_0$"', '"Eruption duration (min)"')],
     ["geyser"]),
    ("P7-a", "P7-heatmap", 0, precomp("p7", "mtcars"), [
        ("Chart Title", "Correlation Between Car Performance Measures")], ["mtcars"]),
    ("P7-b", "P7-heatmap", 0, precomp("p7", "diamonds"), [
        ("Chart Title", "Correlation Between Diamond Attributes")], ["diamonds"]),
    ("P8-a", "P8-multi-panel", 0, p8_fmri, [
        ("Main Title", "fMRI Signal by Region and Event (mean of 14 subjects)"),
        ("Y Label (units)", "Signal (a.u.)"), ("X Label (units)", "Time point"),
        ("    ax.set_ylim(y_lo - y_pad, y_hi + y_pad)",
         "    ax.set_ylim(y_lo - y_pad, y_hi + y_pad)\n"
         "    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))"),
        ("{s.values[-1]:,.0f}", "{s.values[-1]:.3f}"),
        ("{end_values[best]:,.0f}", "{end_values[best]:.3f}"),
        ("{end_values[worst]:,.0f}", "{end_values[worst]:.3f}")], ["fmri"]),
    ("P8-b", "P8-multi-panel", 0, p8_flights, [
        ("Main Title", "Monthly Airline Passengers, Selected Years (thousands)"),
        ("Y Label (units)", "Passengers (thousands)"), ("X Label (units)", "Month (1 = Jan)"),
        ("    ax.set_ylim(y_lo - y_pad, y_hi + y_pad)",
         "    ax.set_ylim(y_lo - y_pad, y_hi + y_pad)\n"
         "    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))")], ["flights"]),
    ("P9-a", "P9-pr-roc", 0, p9("diabetes"), [
        ("Dataset Name (positive = class)",
         "Diabetes Progression (positive = above median)")], ["diabetes"]),
    ("P9-b", "P9-pr-roc", 0, p9("iris"), [
        ("Dataset Name (positive = class)", "Iris, Sepal Features (positive = versicolor)"),
        ('loc="lower left", fontsize=10', 'loc="upper right", fontsize=10')],
     ["iris"]),
    ("P10-slope", "P10-slope-dumbbell", 0, p10_planets, [
        ("Chart Title", "Exoplanet Discoveries by Method, 2000–04 vs 2010–14")],
     ["planets"]),
    ("P10-dumbbell", "P10-slope-dumbbell", 1, p10_flights, [
        ("Chart Title", "Airline Passengers by Month, 1949 vs 1960 (thousands)")], ["flights"]),
    ("P11-share-bars", "P11-part-to-whole", 0, p11_mtcars, [
        ("Chart Title", "Transmission Type by Cylinder Count, 1974 Motor Trend Cars")],
     ["mtcars"]),
    ("P11-stacked-area", "P11-part-to-whole", 1, p11_planets, [
        ("Chart Title", "Exoplanet Discoveries by Method, 1995–2014")], ["planets"]),
    ("P12-ecdf", "P12-distribution-ecdf-ridgeline", 0, p12_geyser, [
        ("Chart Title", "Old Faithful: Waiting Time Before Long and Short Eruptions"),
        ("Value (units; axis cut", "Waiting time (min; axis cut")], ["geyser"]),
    ("P12-ridgeline", "P12-distribution-ecdf-ridgeline", 1, p12_diamonds, [
        ("Chart Title", "Diamond Price by Color Grade (D = colourless)"),
        ("Value (units)", "Price (USD)")], ["diamonds"]),
    ("P13-training", "P13-training-diagnostics", 0, precomp("ml", "training_diabetes"), [
        ("Chart Title", "MLP Training History — Diabetes Progression Above Median")],
     ["diabetes"]),
    ("P13-confusion", "P13-training-diagnostics", 1, precomp("ml", "predictions_iris"), [
        ("Chart Title", "Logistic Regression Confusion Matrix — Iris, Sepal Features")],
     ["iris"]),
    ("other-line", "other-charts", 0, oc_flights, [
        ("Chart Title", "Airline Passengers in July, March and November, 1949–1960"),
        ("Value (units)", "Passengers (thousands)")], ["flights"]),
    ("other-scatter", "other-charts", 1, oc_mtcars, [
        ("Chart Title", "Car Weight vs Fuel Economy, 1974 Motor Trend"),
        ("X (units)", "Weight (1,000 lb)"), ("Y (units)", "Fuel economy (mpg)"),
        ("({top.max():,.0f})", "({top.max():,.1f} mpg)"),
        ('loc="lower right", title=None', 'loc="upper right", title=None')], ["mtcars"]),
    ("other-histogram", "other-charts", 2, oc_geyser, [
        ("Chart Title", "Old Faithful: Waiting Time Between Eruptions"),
        ("Value (units)", "Waiting time (min)")], ["geyser"]),
    ("other-grouped", "other-charts", 3, oc_mtcars_grouped, [
        ("Chart Title", "Average Fuel Economy by Cylinders and Transmission"),
        ("Value (units)", "Fuel economy (mpg)"),
        ('fmt="{:.0%}"', 'fmt="{:.1f}"'),
        ("({gap.iloc[0]:.0%} points)", "({gap.iloc[0]:.1f} mpg)")], ["mtcars"]),
]


def render(name, stem, idx, setup, subs):
    code = BLOCK_RE.findall((SKILL / "patterns" / f"{stem}.md").read_text())[idx]
    for old, new in subs:
        if old not in code:
            raise ValueError(f"{name}: placeholder {old!r} not in {stem}[{idx}]")
        code = code.replace(old, new)
    plt.close("all")
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        ns = {"plt": plt, "sns": sns, "np": np, "pd": pd, "Path": Path}
        ns.update(setup(tmp))
        cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp)
            exec(compile(code, f"{name}", "exec"), ns)
        finally:
            os.chdir(cwd)
    fig = plt.gcf()
    report = check_figure.inspect(fig)
    bad = [i for i in report["issues"] if i["severity"] in ("ERROR", "STYLE", "WARN")]
    OUT.mkdir(exist_ok=True)
    out = OUT / f"{name}.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    w, h = (fig.get_size_inches() * DPI).astype(int)
    print(f"{name:<16} {out.stat().st_size / 1024:>5.0f} KB  ~{w}x{h}px  "
          + ("clean" if not bad else "; ".join(f"{i['severity']}: {i['message']}" for i in bad)))
    return bad


def main():
    wanted = sys.argv[1:]
    failures = 0
    for name, stem, idx, setup, subs, _sources in EXEMPLARS:
        if wanted and not any(name.startswith(w) for w in wanted):
            continue
        failures += bool(render(name, stem, idx, setup, subs))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
