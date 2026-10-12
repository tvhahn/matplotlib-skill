"""Execute every pattern template against real data and lint the figure.

Each ```python block in skills/matplotlib/patterns/*.md is code the model copies,
so it must run and produce a figure free of overlaps and style drift. Blocks use
generic names ("data.csv", df with category/value columns); the fixtures below
supply those from data/raw/.

    uv run --with pytest --with matplotlib --with seaborn --with pandas --with numpy \
        pytest tests/test_patterns.py -q

Rendered PNGs are written to logs/pattern-renders/ for eyeballing.
"""

import os
import re
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402
import seaborn as sns  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SKILL = Path(os.environ.get("MPL_SKILL_DIR", REPO / "skills" / "matplotlib"))
RAW = REPO / "data" / "raw"
RENDERS = REPO / "logs" / "pattern-renders"
sys.path.insert(0, str(REPO / "skills" / "matplotlib" / "scripts"))
import check_figure  # noqa: E402

BLOCK_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)


def blocks():
    for md in sorted((SKILL / "patterns").glob("*.md")):
        for i, code in enumerate(BLOCK_RE.findall(md.read_text())):
            yield pytest.param(md.stem, i, code, id=f"{md.stem}-{i}")


def setup_data(stem, idx, tmp):
    """Write the files a template reads and return extra globals it expects."""
    g = {}
    if stem.startswith("P1-"):
        d = pd.read_csv(RAW / "public/car_crashes.csv").nlargest(10, "total")
        g["df"] = d.rename(columns={"abbrev": "category", "total": "value"})[
            ["category", "value"]
        ]
    elif stem.startswith("P2-"):
        d = pd.read_csv(RAW / "public/diamonds.csv")
        g["raw"] = d.rename(columns={"clarity": "category", "carat": "value"})
    elif stem.startswith("P3-"):
        shutil.copy(RAW / "precomputed/p3/co2_concentration.csv", tmp / "data.csv")
    elif stem.startswith("P4-"):
        d = pd.read_csv(RAW / "public/diamonds.csv")
        d.rename(columns={"price": "value", "color": "category"}).to_csv(
            tmp / "data.csv", index=False
        )
    elif stem.startswith("P5-"):
        shutil.copy(RAW / "precomputed/p5/healthexp.csv", tmp / "data.csv")
    elif stem.startswith("P6-"):
        shutil.copy(RAW / "precomputed/p6/penguins.npz", tmp / "data.npz")
    elif stem.startswith("P7-") and idx == 0:
        shutil.copy(RAW / "precomputed/p7/diamonds.csv", tmp / "data.csv")
    elif stem.startswith("P7-"):
        rng = np.random.default_rng(0)
        g.update(
            time_axis=np.linspace(0, 30, 120),
            freq_axis=np.linspace(0, 5000, 80),
            bins=np.arange(20),
            data=rng.gamma(2, 1, (80, 120)),
            binned_data=rng.gamma(2, 1, (20, 120)),
        )
    elif stem.startswith("P8-"):
        d = pd.read_csv(RAW / "public/chickweight.csv")
        d["diet"] = "Diet " + d["diet"].astype(str)
        d.rename(columns={"diet": "group", "time": "x", "weight": "y"}).to_csv(
            tmp / "data.csv", index=False
        )
    elif stem.startswith("P9-"):
        (tmp / "data/raw/precomputed/p9").mkdir(parents=True)
        shutil.copy(
            RAW / "precomputed/p9/penguins.npz",
            tmp / "data/raw/precomputed/p9/dataset.npz",
        )
    elif stem.startswith("P10-") and idx == 0:  # slope: continents 1952 vs 2007
        d = pd.read_csv(RAW / "public/gapminder.csv")
        d = d[d["year"].isin([1952, 2007])]
        d.rename(columns={"continent": "item", "year": "period", "lifeExp": "value"})[
            ["item", "period", "value"]
        ].to_csv(tmp / "data.csv", index=False)
    elif stem.startswith("P10-"):  # dumbbell: health spending 1970 vs 2020
        d = pd.read_csv(RAW / "public/healthexp.csv")
        d.rename(columns={"Country": "item", "Year": "period", "Spending_USD": "value"})[
            ["item", "period", "value"]
        ].to_csv(tmp / "data.csv", index=False)
    elif stem.startswith("P11-") and idx == 0:  # 100% bars: Titanic class x fate
        d = pd.read_csv(RAW / "public/titanic.csv")
        d["alive"] = d["alive"].map({"yes": "Survived", "no": "Died"})
        d.rename(columns={"class": "group", "alive": "component"})[
            ["group", "component"]
        ].to_csv(tmp / "data.csv", index=False)
    elif stem.startswith("P11-"):  # stacked area: Iowa generation by source
        d = pd.read_csv(RAW / "public/iowa_electricity.csv")
        d["year"] = pd.to_datetime(d["year"]).dt.year
        d.rename(
            columns={"year": "x", "source": "component", "net_generation": "value"}
        ).to_csv(tmp / "data.csv", index=False)
    elif stem.startswith("P12-") and idx == 0:  # ECDF: taxi distance by payment
        d = pd.read_csv(RAW / "public/taxis.csv")
        d["payment"] = d["payment"].str.capitalize()
        d.rename(columns={"payment": "group", "distance": "value"})[
            ["group", "value"]
        ].to_csv(tmp / "data.csv", index=False)
    elif stem.startswith("P12-"):  # ridgeline: Seattle max temperature by month
        d = pd.read_csv(RAW / "public/seattle_weather.csv", parse_dates=["date"])
        d = d.sort_values("date")
        d["group"] = d["date"].dt.strftime("%b")  # file order = calendar order
        d.rename(columns={"temp_max": "value"})[["group", "value"]].to_csv(
            tmp / "data.csv", index=False
        )
    elif stem.startswith("P13-") and idx == 0:  # training curves
        shutil.copy(RAW / "precomputed/ml/training_breast_cancer.csv", tmp / "data.csv")
    elif stem.startswith("P13-"):  # confusion matrix
        shutil.copy(RAW / "precomputed/ml/predictions_wine.csv", tmp / "data.csv")
    elif stem == "other-charts":
        if idx == 0:
            d = pd.read_csv(RAW / "public/stocks.csv")
            d["date"] = pd.to_datetime(d["date"], format="%b %d %Y")
            d.rename(columns={"symbol": "series", "price": "value"}).to_csv(
                tmp / "data.csv", index=False
            )
        elif idx == 1:
            d = pd.read_csv(RAW / "public/penguins.csv")
            d.rename(
                columns={
                    "flipper_length_mm": "x",
                    "body_mass_g": "y",
                    "species": "group",
                }
            ).to_csv(tmp / "data.csv", index=False)
        elif idx == 2:
            d = pd.read_csv(RAW / "public/diamonds.csv")
            d.rename(columns={"price": "value"}).to_csv(tmp / "data.csv", index=False)
        else:
            d = pd.read_csv(RAW / "public/titanic.csv")
            d["class"] = d["class"].str.title()
            d["sex"] = d["sex"].str.title()
            d.rename(
                columns={"class": "group", "sex": "subgroup", "survived": "value"}
            ).to_csv(tmp / "data.csv", index=False)
    return g


@pytest.mark.parametrize("stem,idx,code", list(blocks()))
def test_template_runs_clean(stem, idx, code, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plt.close("all")
    ns = {"plt": plt, "sns": sns, "np": np, "pd": pd, "Path": Path}
    ns.update(setup_data(stem, idx, tmp_path))
    exec(compile(code, f"{stem}[{idx}]", "exec"), ns)

    fig = plt.gcf()
    report = check_figure.inspect(fig)
    RENDERS.mkdir(parents=True, exist_ok=True)
    fig.savefig(RENDERS / f"{stem}-{idx}.png", dpi=110, bbox_inches="tight")
    problems = [
        i["message"] for i in report["issues"] if i["severity"] in ("ERROR", "STYLE")
    ]
    assert not problems, "\n".join(problems)


def test_skill_frontmatter():
    """name/description must parse as YAML and satisfy the Agent Skills limits."""
    import yaml

    text = (SKILL / "SKILL.md").read_text()
    front = yaml.safe_load(text.split("---")[1])
    assert re.fullmatch(r"[a-z0-9-]{1,64}", front["name"])
    desc = front["description"]
    assert 50 < len(desc) <= 1024 and "<" not in desc
    assert "Use when" in desc  # says when to trigger, not just what it does


def test_exemplars_referenced_and_present():
    """Every exemplar a pattern names exists, and every exemplar file is named somewhere."""
    named = set()
    for md in (SKILL / "patterns").glob("*.md"):
        named |= set(re.findall(r"exemplars/([\w.-]+\.png)", md.read_text()))
    on_disk = {p.name for p in (SKILL / "exemplars").glob("*.png")}
    assert named, "no pattern references an exemplar"
    assert not named - on_disk, f"missing exemplar files: {sorted(named - on_disk)}"
    assert not on_disk - named, f"unreferenced exemplar files: {sorted(on_disk - named)}"
    for png in (SKILL / "exemplars").glob("*.png"):
        assert png.stat().st_size < 400_000, f"{png.name} too large for the model to read cheaply"


def test_skill_references_exist():
    """Files SKILL.md points at by ${CLAUDE_SKILL_DIR}/... or patterns/... exist."""
    text = (SKILL / "SKILL.md").read_text()
    paths = set(re.findall(r"\$\{CLAUDE_SKILL_DIR\}/([\w./-]+\.(?:md|py))", text))
    paths |= set(re.findall(r"`(patterns/[\w.-]+\.md)`", text))
    missing = [p for p in sorted(paths) if not (SKILL / p).exists()]
    assert not missing, f"SKILL.md references missing files: {missing}"


def _source_stem(path):
    """data/raw/precomputed/ml/training_wine.csv → 'wine'; public/penguins.csv → 'penguins'."""
    stem = Path(path).stem
    for prefix in ("training_", "predictions_"):
        stem = stem.removeprefix(prefix)
    return stem


def test_exemplar_data_disjoint_from_benchmark():
    """An exemplar drawn from a benchmark prompt's dataset is a worked answer: models copy it.

    The first v3 benchmark run was contaminated this way (an exemplar on the Iowa data was
    reproduced callout-for-callout), so every exemplar declares its sources and none may
    share a source dataset with any prompt in scripts/benchmark_prompts.yaml.
    """
    import yaml

    sys.path.insert(0, str(REPO / "scripts"))
    import render_exemplars

    prompts = yaml.safe_load((REPO / "scripts" / "benchmark_prompts.yaml").read_text())
    bench = {
        _source_stem(p)
        for c in prompts
        for p in re.findall(r"data/raw/[\w./-]+\.\w+", c["prompt"])
    }
    assert bench, "no data paths found in benchmark prompts"
    clashes = {
        name: sorted(set(sources) & bench)
        for name, *_, sources in render_exemplars.EXEMPLARS
        if set(sources) & bench
    }
    assert not clashes, f"exemplars share data with benchmark prompts: {clashes}"
    rendered = {e[0] for e in render_exemplars.EXEMPLARS}
    on_disk = {p.stem for p in (SKILL / "exemplars").glob("*.png")}
    assert rendered == on_disk, f"exemplars on disk vs catalogue differ: {rendered ^ on_disk}"
