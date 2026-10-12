# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""Headless vision judges for scripts/benchmark.py results.

Each judgement runs ``claude -p`` in its own room that holds only the chart
PNG(s), the task (prompt + ground-truth checks) and the rubric. The judge may
only Read; it never sees the chart code, the skill, the model or the version.

Absolute scores (rubric dimensions + overall 1–10):
    uv run scripts/judge.py absolute logs/bench/v3 --judges claude-opus-5-5

Blind pairwise, every pair judged in BOTH A/B orders; a pair whose two orders
disagree counts as a tie:
    uv run scripts/judge.py pairwise logs/bench/v2base logs/bench/v3

With two or more --judges, the summary reports how often the judges agree.
Results go to <results-dir>/judgements/ (absolute) or
logs/bench/pairwise-<a>-vs-<b>/ (pairwise).
"""

import argparse
import json
import random
import re
import shutil
import statistics
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from benchmark import child_env  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
RUBRIC = REPO / "scripts" / "judge_rubric.md"
ROOM_ROOT = Path("/tmp/matplotlib-skill-judge")
DIMS = ["correct", "fit", "legible", "insight", "polish"]

ABSOLUTE_PROMPT = """You are a demanding data-visualisation editor judging one chart.
Read rubric.md, then task.json (the request and ground-truth checks), then every
PNG in this directory ({pngs}). Judge only what you see in the PNG(s).

Reply with ONLY one JSON object, no prose, no code fence:
{{"correct": 0-3, "fit": 0-3, "legible": 0-3, "insight": 0-3, "polish": 0-3,
 "overall": 1-10, "defects": ["<15 words each"], "note": "one sentence"}}"""

PAIRWISE_PROMPT = """You are a demanding data-visualisation editor comparing two charts
made for the same request. Read rubric.md (see "Pairwise mode"), then task.json,
then chart A ({a}) and chart B ({b}). Which chart would you publish? Judge the
chart, not the effort; correctness first, then fit, legibility, insight, polish.

Reply with ONLY one JSON object, no prose, no code fence:
{{"winner": "A" | "B" | "tie", "margin": "slight" | "clear" | "large",
 "why": "one sentence"}}"""


def run_metas(results_dir):
    return sorted(
        p for p in Path(results_dir).rglob("meta.json") if "workspace" not in p.parts
    )


def run_key(meta_path, results_dir):
    return "/".join(meta_path.parent.relative_to(results_dir).parts)


def ask(room, prompt, model, timeout=600):
    """Run one headless judgement; return the parsed JSON object (or an error)."""
    cfg = room.parent / (room.name + "-cfg")
    cfg.mkdir(parents=True, exist_ok=True)
    cmd = [
        "claude", "-p", prompt, "--model", model, "--max-turns", "12",
        "--output-format", "json", "--setting-sources", "project",
        "--allowedTools", "Read", "Glob",
    ]
    try:
        proc = subprocess.run(
            cmd, cwd=room, env=child_env(cfg), capture_output=True, text=True,
            timeout=timeout,
        )
        out = json.loads(proc.stdout)
        text = out.get("result") or ""
        cost = out.get("total_cost_usd") or 0
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        return {"error": repr(e)[:300]}
    finally:
        shutil.rmtree(cfg, ignore_errors=True)
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {"error": "no JSON in reply", "raw": text[-500:]}
    try:
        res = json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"error": "bad JSON", "raw": text[-500:]}
    res["cost_usd"] = cost
    return res


def task_json(meta):
    return json.dumps({"request": meta["prompt"], "checks": meta.get("checks", [])}, indent=2)


def copy_pngs(src_dir, room, prefix):
    names = []
    for k, png in enumerate(sorted(src_dir.glob("*.png"))):
        name = f"{prefix}{'' if k == 0 else k + 1}.png"
        shutil.copy(png, room / name)
        names.append(name)
    return names


# --------------------------------------------------------------------------- absolute


def judge_absolute(results_dir, judges, parallel):
    results_dir = Path(results_dir).resolve()
    out_dir = results_dir / "judgements"
    out_dir.mkdir(exist_ok=True)
    jobs = [(m, j) for m in run_metas(results_dir) for j in judges]

    def one(job):
        meta_path, judge = job
        key = run_key(meta_path, results_dir)
        meta = json.loads(meta_path.read_text())
        room = ROOM_ROOT / "abs" / results_dir.name / judge / key.replace("/", "__")
        shutil.rmtree(room, ignore_errors=True)
        room.mkdir(parents=True)
        shutil.copy(RUBRIC, room / "rubric.md")
        (room / "task.json").write_text(task_json(meta))
        pngs = copy_pngs(meta_path.parent, room, "chart")
        if not pngs:
            res = {d: 0 for d in DIMS} | {"overall": 0, "defects": ["no chart"]}
        else:
            res = ask(room, ABSOLUTE_PROMPT.format(pngs=", ".join(pngs)), judge)
        shutil.rmtree(room, ignore_errors=True)
        res.update(run=key, judge=judge, model=meta["model"], case=meta["id"],
                   kind=meta.get("kind"))
        return res

    with ThreadPoolExecutor(max_workers=parallel) as pool:
        rows = list(pool.map(one, jobs))
    for judge in judges:
        mine = [r for r in rows if r["judge"] == judge]
        (out_dir / f"absolute-{judge}.json").write_text(json.dumps(mine, indent=2))
    summarize_absolute(rows, judges)
    return rows


def summarize_absolute(rows, judges):
    ok = [r for r in rows if "overall" in r]
    errs = len(rows) - len(ok)
    print(f"\n{len(ok)} judgements ({errs} errors)")
    for judge in judges:
        mine = [r for r in ok if r["judge"] == judge]
        print(f"\njudge {judge}")
        by = {}
        for r in mine:
            by.setdefault(r["model"], []).append(r)
        for model, rs in sorted(by.items()):
            dims = "  ".join(f"{d}={statistics.mean(r[d] for r in rs):.2f}" for d in DIMS)
            print(f"  {model:<20} n={len(rs):<3} overall={statistics.mean(r['overall'] for r in rs):.2f}  {dims}")
        kinds = {}
        for r in mine:
            kinds.setdefault(r.get("kind"), []).append(r["overall"])
        print("  by kind: " + ", ".join(
            f"{k}={statistics.mean(v):.2f} (n={len(v)})" for k, v in sorted(kinds.items(), key=str)))
    if len(judges) > 1:
        for a, b in combinations(judges, 2):
            xa = {r["run"]: r["overall"] for r in ok if r["judge"] == a}
            xb = {r["run"]: r["overall"] for r in ok if r["judge"] == b}
            common = sorted(set(xa) & set(xb))
            if len(common) > 2:
                r = statistics.correlation([xa[k] for k in common], [xb[k] for k in common])
                mad = statistics.mean(abs(xa[k] - xb[k]) for k in common)
                print(f"\nagreement {a} vs {b}: pearson r={r:.2f}, mean |Δ|={mad:.2f} (n={len(common)})")


# --------------------------------------------------------------------------- pairwise


def judge_pairwise(dir_a, dir_b, judges, parallel, seed=0):
    dir_a, dir_b = Path(dir_a).resolve(), Path(dir_b).resolve()
    out_dir = dir_b.parent / f"pairwise-{dir_a.name}-vs-{dir_b.name}"
    out_dir.mkdir(exist_ok=True)
    a_runs = {run_key(m, dir_a): m for m in run_metas(dir_a)}
    b_runs = {run_key(m, dir_b): m for m in run_metas(dir_b)}
    keys = sorted(set(a_runs) & set(b_runs))
    rng = random.Random(seed)
    jobs = []
    for key in keys:
        first = rng.choice([0, 1])  # which version is shown as A in order 0
        for order in (0, 1):
            a_is_dir_a = (first + order) % 2 == 0
            for judge in judges:
                jobs.append((key, order, a_is_dir_a, judge))

    def one(job):
        key, order, a_is_dir_a, judge = job
        src_a = a_runs[key] if a_is_dir_a else b_runs[key]
        src_b = b_runs[key] if a_is_dir_a else a_runs[key]
        meta = json.loads(a_runs[key].read_text())
        room = ROOM_ROOT / "pair" / out_dir.name / judge / f"{key.replace('/', '__')}-o{order}"
        shutil.rmtree(room, ignore_errors=True)
        room.mkdir(parents=True)
        shutil.copy(RUBRIC, room / "rubric.md")
        (room / "task.json").write_text(task_json(meta))
        pa = copy_pngs(src_a.parent, room, "A")
        pb = copy_pngs(src_b.parent, room, "B")
        if not pa or not pb:
            winner = "tie" if not pa and not pb else ("B" if not pa else "A")
            res = {"winner": winner, "margin": "large", "why": "missing chart"}
        else:
            res = ask(room, PAIRWISE_PROMPT.format(a=", ".join(pa), b=", ".join(pb)), judge)
        shutil.rmtree(room, ignore_errors=True)
        w = res.get("winner")
        version = {"A": dir_a.name if a_is_dir_a else dir_b.name,
                   "B": dir_b.name if a_is_dir_a else dir_a.name}.get(w, "tie")
        res.update(run=key, order=order, judge=judge, model=meta["model"],
                   case=meta["id"], kind=meta.get("kind"), winner_version=version)
        return res

    with ThreadPoolExecutor(max_workers=parallel) as pool:
        rows = list(pool.map(one, jobs))
    (out_dir / "pairwise.json").write_text(json.dumps(rows, indent=2))
    summarize_pairwise(rows, dir_a.name, dir_b.name, judges, out_dir)
    return rows


def resolve_orders(rows):
    """Collapse the two orders of each (run, judge) into one verdict."""
    by = {}
    for r in rows:
        by.setdefault((r["run"], r["judge"]), []).append(r)
    final = {}
    for (run, judge), rs in by.items():
        votes = {r["winner_version"] for r in rs if "error" not in r}
        verdict = votes.pop() if len(votes) == 1 else "tie"
        final[(run, judge)] = {"verdict": verdict, "model": rs[0]["model"],
                               "case": rs[0]["case"], "kind": rs[0]["kind"],
                               "consistent": len({r['winner_version'] for r in rs}) == 1}
    return final


def summarize_pairwise(rows, name_a, name_b, judges, out_dir):
    final = resolve_orders(rows)
    lines = [f"pairwise {name_a} vs {name_b} (both orders; disagreement → tie)"]
    for judge in judges:
        mine = {k: v for k, v in final.items() if k[1] == judge}
        cons = sum(v["consistent"] for v in mine.values()) / max(len(mine), 1)
        lines.append(f"\njudge {judge}  (order-consistency {cons:.0%})")
        groups = {}
        for (run, _), v in mine.items():
            for g in (v["model"], "ALL", f"kind:{v['kind']}"):
                groups.setdefault(g, []).append(v["verdict"])
        for g, vs in sorted(groups.items()):
            wa, wb, t = vs.count(name_a), vs.count(name_b), vs.count("tie")
            decided = wa + wb
            rate = wb / decided if decided else 0
            lines.append(f"  {g:<22} {name_b} {wb:>3} | {name_a} {wa:>3} | tie {t:>3}"
                         f"   {name_b} win-rate (excl. ties) {rate:.0%}, of all {wb / len(vs):.0%}")
    if len(judges) > 1:
        for a, b in combinations(judges, 2):
            runs = {k[0] for k in final}
            same = [final[(r, a)]["verdict"] == final[(r, b)]["verdict"]
                    for r in runs if (r, a) in final and (r, b) in final]
            if same:
                lines.append(f"\njudge agreement {a} vs {b}: {sum(same) / len(same):.0%} (n={len(same)})")
    text = "\n".join(lines)
    print(text)
    (out_dir / "summary.txt").write_text(text + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    a = sub.add_parser("absolute")
    a.add_argument("results_dir")
    p = sub.add_parser("pairwise")
    p.add_argument("dir_a")
    p.add_argument("dir_b")
    for s in (a, p):
        s.add_argument("--judges", default="claude-opus-5-5",
                       help="comma-separated judge models")
        s.add_argument("--parallel", type=int, default=8)
    args = ap.parse_args()
    judges = args.judges.split(",")
    if args.mode == "absolute":
        judge_absolute(args.results_dir, judges, args.parallel)
    else:
        judge_pairwise(args.dir_a, args.dir_b, judges, args.parallel)


if __name__ == "__main__":
    main()
