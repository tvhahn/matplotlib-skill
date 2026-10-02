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
    if stem.startswith("P1"):
        d = pd.read_csv(RAW / "public/car_crashes.csv").nlargest(10, "total")
        g["df"] = d.rename(columns={"abbrev": "category", "total": "value"})[
            ["category", "value"]
        ]
    elif stem.startswith("P2"):
        d = pd.read_csv(RAW / "public/diamonds.csv")
        g["raw"] = d.rename(columns={"clarity": "category", "carat": "value"})
    elif stem.startswith("P3"):
        shutil.copy(RAW / "precomputed/p3/co2_concentration.csv", tmp / "data.csv")
    elif stem.startswith("P4"):
        d = pd.read_csv(RAW / "public/diamonds.csv")
        d.rename(columns={"price": "value", "color": "category"}).to_csv(
            tmp / "data.csv", index=False
        )
    elif stem.startswith("P5"):
        shutil.copy(RAW / "precomputed/p5/healthexp.csv", tmp / "data.csv")
    elif stem.startswith("P6"):
        shutil.copy(RAW / "precomputed/p6/penguins.npz", tmp / "data.npz")
    elif stem.startswith("P7") and idx == 0:
        shutil.copy(RAW / "precomputed/p7/diamonds.csv", tmp / "data.csv")
    elif stem.startswith("P7"):
        rng = np.random.default_rng(0)
        g.update(
            time_axis=np.linspace(0, 30, 120),
            freq_axis=np.linspace(0, 5000, 80),
            bins=np.arange(20),
            data=rng.gamma(2, 1, (80, 120)),
            binned_data=rng.gamma(2, 1, (20, 120)),
        )
    elif stem.startswith("P8"):
        d = pd.read_csv(RAW / "public/fmri.csv")
        s = d.groupby("timepoint")["signal"].mean()
        g.update(
            all_values=s.values,
            x_data=s.index.values,
            y_data=s.values,
            x_last=s.index[-1],
            y_last=s.values[-1],
        )
        d.rename(columns={"region": "group", "timepoint": "x", "signal": "y"}).to_csv(
            tmp / "data.csv", index=False
        )
    elif stem.startswith("P9"):
        (tmp / "data/raw/precomputed/p9").mkdir(parents=True)
        shutil.copy(
            RAW / "precomputed/p9/penguins.npz",
            tmp / "data/raw/precomputed/p9/dataset.npz",
        )
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
            d = pd.read_csv(RAW / "public/tips.csv")
            d.rename(
                columns={"day": "group", "smoker": "subgroup", "tip": "value"}
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
