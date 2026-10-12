"""Regression tests for skills/matplotlib/scripts/check_figure.py.

tests/broken/*.py are small chart scripts that each break one rule; their first
line names the issue code that must be reported (`# expect: <code>`), and an
optional second line lists codes that may co-occur (`# also: a, b`).
tests/broken/good_*.py use the house style legitimately and must be clean
(no ERROR, WARN or STYLE).

    uv run --no-project --with pytest --with matplotlib --with seaborn \
        --with pandas --with numpy pytest tests/test_checker.py -q
"""

import json
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import pytest  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
CHECKER = REPO / "skills" / "matplotlib" / "scripts" / "check_figure.py"
BROKEN = Path(__file__).resolve().parent / "broken"
sys.path.insert(0, str(CHECKER.parent))
import check_figure  # noqa: E402

FAILING = ("ERROR", "WARN", "STYLE")
SCRIPTS = sorted(BROKEN.glob("*.py"))
BAD = [s for s in SCRIPTS if not s.name.startswith("good_")]
GOOD = [s for s in SCRIPTS if s.name.startswith("good_")]


def _meta(path):
    lines = path.read_text().splitlines()
    assert lines[0].startswith("# expect:"), f"{path.name}: needs '# expect: <code>'"
    expect = lines[0].split(":", 1)[1].strip()
    also = set()
    if len(lines) > 1 and lines[1].startswith("# also:"):
        also = {c.strip() for c in lines[1].split(":", 1)[1].split(",") if c.strip()}
    return expect, also


def _run(script, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # scripts that save write ./figures/ here
    res = check_figure.check_script(script)
    assert res["run_error"] is None, res["run_error"]
    assert res["figures"], "script produced no figure"
    return res


def test_corpus_size():
    assert len(BAD) >= 20 and len(GOOD) >= 5


@pytest.mark.parametrize("script", BAD, ids=lambda p: p.stem)
def test_broken_script_is_caught(script, tmp_path, monkeypatch):
    expect, also = _meta(script)
    res = _run(script, tmp_path, monkeypatch)
    issues = res["issues"]
    hits = [i for i in issues if i["code"] == expect or expect in i["message"]]
    summary = "\n".join(f"{i['severity']} [{i['code']}] {i['message']}" for i in issues)
    assert hits, f"expected '{expect}', got:\n{summary}"
    # each script breaks exactly one rule: nothing else may fail
    extra = {i["code"] for i in issues if i["severity"] in FAILING} - {expect} - also
    assert not extra, f"unexpected {sorted(extra)}:\n{summary}"


@pytest.mark.parametrize("script", GOOD, ids=lambda p: p.stem)
def test_good_script_is_clean(script, tmp_path, monkeypatch):
    res = _run(script, tmp_path, monkeypatch)
    bad = [i for i in res["issues"] if i["severity"] in FAILING]
    msg = "\n".join(f"{i['severity']} [{i['code']}] {i['message']}" for i in bad)
    assert not bad, msg


def test_every_issue_has_a_code(tmp_path, monkeypatch):
    for script in BAD[:5]:
        res = _run(script, tmp_path, monkeypatch)
        assert all(i.get("code") and i.get("severity") for i in res["issues"])


def test_cvd_reference_distances():
    d = check_figure._cvd_distances
    # house pair: equal luminance by design, but far apart for every viewer
    assert min(d((0.843, 0.188, 0.153), (0.271, 0.459, 0.706)).values()) > 15
    red, grey = "#d73027", "#555555"
    from matplotlib.colors import to_rgb

    assert d(to_rgb(red), to_rgb(grey))["protanopia"] == pytest.approx(7.7, abs=0.2)


@pytest.mark.parametrize(
    "text,flag",
    [
        ("Prices range from $6 to $230", True),
        ("Revenue $1.2M vs $0.8M", True),
        (r"Prices range from \$6 to \$230", False),
        (r"$R^2$ = 0.93", False),
        (r"$\bf{(a)}$  Panel", False),
        (r"$2 \times 10^3$ samples", False),
        (r"$x_{max}$ and $y_{min}$", False),
        (r"$\alpha = 0.5$", False),
        ("Costs $5", False),
    ],
)
def test_currency_mathtext_detection(text, flag):
    assert (check_figure._currency_math(text) is not None) is flag


def test_cli_strict_and_json_schema(tmp_path):
    script = BROKEN / "twinx.py"  # WARN only

    def run(*flags):
        return subprocess.run(
            [sys.executable, str(CHECKER), *flags, str(script)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=120,
        )

    assert run().returncode == 0
    assert run("--strict").returncode == 1
    out = run("--json")
    data = json.loads(out.stdout)
    for key in ("script", "run_error", "figures", "issues", "errors"):  # v1 schema
        assert key in data
    for key in ("warnings", "strict", "exit_code"):  # additions
        assert key in data
    fig = data["figures"][0]
    for key in ("size_in", "n_axes", "issues", "saved_as", "formats", "dpi"):
        assert key in fig
    for key in ("saved_pdf", "saved_png", "in_figures_dir"):
        assert key in fig
    assert any(i["code"] == "dual-axis" for i in data["issues"])
