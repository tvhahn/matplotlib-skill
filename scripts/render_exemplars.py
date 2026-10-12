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
# Each returns extra globals for the template (most templates read ./data.csv).


def p1_crashes(tmp):
    d = pub("car_crashes.csv").nlargest(10, "total")
    return {"df": d.rename(columns={"abbrev": "category", "total": "value"})[["category", "value"]]}


def p1_happiness(tmp):
    d = pub("world_happiness.csv").groupby("Region", as_index=False)["Happiness Score"].mean()
    return {"df": d.rename(columns={"Region": "category", "Happiness Score": "value"})}


def p2_mpg(tmp):
    return {"raw": pub("mpg.csv").rename(columns={"cylinders": "category", "horsepower": "value"})}


def p2_penguins(tmp):
    return {"raw": pub("penguins.csv").rename(columns={"island": "category", "body_mass_g": "value"})}


def p3(name):
    def f(tmp):
        shutil.copy(RAW / f"precomputed/p3/{name}.csv", tmp / "data.csv")
        return {}
    return f


def p4_penguins(tmp):
    csv(pub("penguins.csv").rename(columns={"species": "category", "body_mass_g": "value"}), tmp)
    return {}


def p4_gapminder(tmp):
    d = pub("gapminder.csv")
    d = d[(d["year"] == 2007) & (d["continent"] != "FSU")]
    csv(d.rename(columns={"continent": "category", "lifeExp": "value"}), tmp)
    return {}


def p5(name):
    def f(tmp):
        shutil.copy(RAW / f"precomputed/p5/{name}.csv", tmp / "data.csv")
        return {}
    return f


def p6(name):
    def f(tmp):
        shutil.copy(RAW / f"precomputed/p6/{name}.npz", tmp / "data.npz")
        return {}
    return f


def p7(name):
    def f(tmp):
        shutil.copy(RAW / f"precomputed/p7/{name}.csv", tmp / "data.csv")
        return {}
    return f


def p8_chicks(tmp):
    d = pub("chickweight.csv")
    d["diet"] = "Diet " + d["diet"].astype(str)
    csv(d.rename(columns={"diet": "group", "time": "x", "weight": "y"}), tmp)
    return {}


def p8_gapminder(tmp):
    d = pub("gapminder.csv")
    d = d[d["year"] % 5 == 2]  # 1952, 1957, … 2007: every country reported
    d = d[d["continent"] != "FSU"]
    csv(d.rename(columns={"continent": "group", "year": "x", "lifeExp": "y"}), tmp)
    return {}


def p9(name):
    def f(tmp):
        (tmp / "data/raw/precomputed/p9").mkdir(parents=True)
        shutil.copy(RAW / f"precomputed/p9/{name}.npz", tmp / "data/raw/precomputed/p9/dataset.npz")
        return {}
    return f


def oc_stocks(tmp):
    d = pub("stocks.csv")
    d["date"] = pd.to_datetime(d["date"], format="%b %d %Y")
    csv(d.rename(columns={"symbol": "series", "price": "value"}), tmp)
    return {}


def oc_penguins(tmp):
    csv(pub("penguins.csv").rename(
        columns={"flipper_length_mm": "x", "body_mass_g": "y", "species": "group"}), tmp)
    return {}


def oc_taxis(tmp):
    csv(pub("taxis.csv").rename(columns={"fare": "value"}), tmp)
    return {}


def oc_titanic(tmp):
    d = pub("titanic.csv")
    d["class"] = d["class"].str.title()
    d["sex"] = d["sex"].str.title()
    csv(d.rename(columns={"class": "group", "sex": "subgroup", "survived": "value"}), tmp)
    return {}


def p10_gapminder(tmp):
    d = pub("gapminder.csv")
    d = d[d["year"].isin([1952, 2007])]
    csv(d.rename(columns={"continent": "item", "year": "period", "lifeExp": "value"})[
        ["item", "period", "value"]], tmp)
    return {}


def p10_healthexp(tmp):
    d = pub("healthexp.csv")
    csv(d.rename(columns={"Country": "item", "Year": "period", "Spending_USD": "value"})[
        ["item", "period", "value"]], tmp)
    return {}


def p11_titanic(tmp):
    d = pub("titanic.csv")
    d["alive"] = d["alive"].map({"yes": "Survived", "no": "Died"})
    csv(d.rename(columns={"class": "group", "alive": "component"})[["group", "component"]], tmp)
    return {}


def p11_iowa(tmp):
    d = pub("iowa_electricity.csv")
    d["year"] = pd.to_datetime(d["year"]).dt.year
    csv(d.rename(columns={"year": "x", "source": "component", "net_generation": "value"}), tmp)
    return {}


def p12_taxis(tmp):
    d = pub("taxis.csv")
    d["payment"] = d["payment"].str.capitalize()
    csv(d.rename(columns={"payment": "group", "distance": "value"})[["group", "value"]], tmp)
    return {}


def p12_seattle(tmp):
    d = pd.read_csv(RAW / "public/seattle_weather.csv", parse_dates=["date"]).sort_values("date")
    d["group"] = d["date"].dt.strftime("%b")
    csv(d.rename(columns={"temp_max": "value"})[["group", "value"]], tmp)
    return {}


def p13(name):
    def f(tmp):
        shutil.copy(RAW / f"precomputed/ml/{name}.csv", tmp / "data.csv")
        return {}
    return f


# --------------------------------------------------------------------------- catalogue
# (output name, pattern file stem, block index, setup, [(placeholder, replacement), ...])

EXEMPLARS = [
    ("P1-a", "P1-horizontal-bar", 0, p1_crashes, [
        ("Chart Title", "Fatal Collisions per Billion Miles — Top 10 States"),
        ('fmt = "{:.1f}%"', 'fmt = "{:.1f}"')]),
    ("P1-b", "P1-horizontal-bar", 0, p1_happiness, [
        ("Chart Title", "Average Happiness Score by Region"),
        ('fmt = "{:.1f}%"', 'fmt = "{:.2f}"')]),
    ("P2-a", "P2-vertical-bar", 0, p2_mpg, [
        ("Chart Title", "Average Horsepower by Number of Cylinders"),
        ('"Category label"', '"Cylinders"'),
        (" averages {hi", "-cylinder cars average {hi"),
        ("""f'{label(lo["category"])}',""", """f'the {label(lo["category"])}-cylinder',""")]),
    ("P2-b", "P2-vertical-bar", 0, p2_penguins, [
        ("Chart Title", "Average Penguin Body Mass (g) by Island"),
        ('"Category label"', '"Island"')]),
    ("P3-a", "P3-time-series", 0, p3("global_temp"), [
        ("Chart Title", "Global Surface Temperature Anomaly, 1880–2025"),
        ("Y-Axis Label (unit)", "Anomaly vs 1951–1980 (°C)")]),
    ("P3-b", "P3-time-series", 0, p3("co2_concentration"), [
        ("Chart Title", "Atmospheric CO₂ at Mauna Loa"),
        ("Y-Axis Label (unit)", "CO₂ concentration (ppm)")]),
    ("P4-a", "P4-violin-strip", 0, p4_penguins, [
        ("Chart Title", "Penguin Body Mass by Species"),
        ("Value (units)", "Body mass (g)"),
        ("units above", "g above")]),
    ("P4-b", "P4-violin-strip", 0, p4_gapminder, [
        ("Chart Title", "Life Expectancy by Continent, 2007"),
        ("Value (units)", "Life expectancy (years)"),
        ("units above", "years above"),
        ('f"{med:,.0f}"', 'f"{med:,.1f}"')]),
    ("P5-a", "P5-lollipop", 0, p5("glue"), [
        ("Chart Title", "GLUE Score Range Across Tasks by Model"),
        ("Score (units)", "GLUE task score")]),
    ("P5-b", "P5-lollipop", 0, p5("healthexp"), [
        ("Chart Title", "Health Spending per Capita, 1970–2020"),
        ("Score (units)", "Spending per capita (USD, PPP)")]),
    ("P6-a", "P6-decision-boundary", 0, p6("penguins"), [
        ("KNN Decision Boundary — Dataset Name", "KNN Decision Boundary — Penguin Species"),
        ('r"$x_1$"', '"Bill depth (mm)"'), ('r"$x_0$"', '"Bill length (mm)"')]),
    ("P6-b", "P6-decision-boundary", 0, p6("wine"), [
        ("KNN Decision Boundary — Dataset Name", "KNN Decision Boundary — Wine Cultivars"),
        ('r"$x_1$"', '"Malic acid (g/L)"'), ('r"$x_0$"', '"Alcohol (% vol)"')]),
    ("P7-a", "P7-heatmap", 0, p7("mpg"), [("Chart Title", "Correlation Between Car Attributes")]),
    ("P7-b", "P7-heatmap", 0, p7("diamonds"), [("Chart Title", "Correlation Between Diamond Attributes")]),
    ("P8-a", "P8-multi-panel", 0, p8_chicks, [
        ("Main Title", "Chick Weight Over Time by Diet (mean per day)"),
        ("Y Label (units)", "Weight (g)"), ("X Label (units)", "Day")]),
    ("P8-b", "P8-multi-panel", 0, p8_gapminder, [
        ("Main Title", "Life Expectancy by Continent, 1952–2007 (country mean)"),
        ("Y Label (units)", "Life expectancy (years)"), ("X Label (units)", "Year")]),
    ("P9-a", "P9-pr-roc", 0, p9("titanic"), [
        ("Dataset Name (positive = class)", "Titanic Survival (positive = survived)")]),
    ("P9-b", "P9-pr-roc", 0, p9("breast_cancer"), [
        ("Dataset Name (positive = class)", "Breast Cancer (positive = benign)")]),
    ("P10-slope", "P10-slope-dumbbell", 0, p10_gapminder, [
        ("Chart Title", "Life Expectancy by Continent, 1952 vs 2007")]),
    ("P10-dumbbell", "P10-slope-dumbbell", 1, p10_healthexp, [
        ("Chart Title", "Health Spending per Capita (USD), 1970 vs 2020")]),
    ("P11-share-bars", "P11-part-to-whole", 0, p11_titanic, [
        ("Chart Title", "Titanic Passengers Who Survived, by Class")]),
    ("P11-stacked-area", "P11-part-to-whole", 1, p11_iowa, [
        ("Chart Title", "Iowa Electricity Generation by Source, 2001–2017")]),
    ("P12-ecdf", "P12-distribution-ecdf-ridgeline", 0, p12_taxis, [
        ("Chart Title", "NYC Taxi Trip Distance by Payment Type"),
        ("Value (units; axis cut", "Trip distance (miles; axis cut")]),
    ("P12-ridgeline", "P12-distribution-ecdf-ridgeline", 1, p12_seattle, [
        ("Chart Title", "Seattle Daily Maximum Temperature by Month, 2012–2015"),
        ("Value (units)", "Daily maximum temperature (°C)")]),
    ("P13-training", "P13-training-diagnostics", 0, p13("training_breast_cancer"), [
        ("Chart Title", "MLP Training History — Breast Cancer")]),
    ("P13-confusion", "P13-training-diagnostics", 1, p13("predictions_wine"), [
        ("Chart Title", "Logistic Regression Confusion Matrix — Wine Cultivars")]),
    ("other-line", "other-charts", 0, oc_stocks, [
        ("Chart Title", "Monthly Closing Price, 2000–2010"), ("Value (units)", "Price (USD)")]),
    ("other-scatter", "other-charts", 1, oc_penguins, [
        ("Chart Title", "Penguin Flipper Length vs Body Mass"),
        ("X (units)", "Flipper length (mm)"), ("Y (units)", "Body mass (g)")]),
    ("other-histogram", "other-charts", 2, oc_taxis, [
        ("Chart Title", "NYC Taxi Fares"), ("Value (units)", "Fare (USD)")]),
    ("other-grouped", "other-charts", 3, oc_titanic, [
        ("Chart Title", "Titanic Survival Rate by Class and Sex"), ("Value (units)", "Survival rate")]),
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
    for name, stem, idx, setup, subs in EXEMPLARS:
        if wanted and not any(name.startswith(w) for w in wanted):
            continue
        failures += bool(render(name, stem, idx, setup, subs))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
