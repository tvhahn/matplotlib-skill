# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Process metrics for scripts/benchmark.py results (no Claude calls).

    uv run scripts/bench_report.py logs/bench/v2base logs/bench/v3

Per results dir and model: runs, charts produced, turn-cap hits, timeouts, mean
cost and time, routing accuracy (did the run read the pattern file the prompt
calls for), exemplar uptake, independent-review rate (an Agent/Task call whose
description mentions review/critic), and checker findings on the final scripts
(non-INFO, by severity).
"""

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

# The pattern file a correct run reads first, by prompt id (prefix match on the
# file stem; a tuple lists acceptable alternatives).
EXPECTED = {
    "p1-titanic": "P1-", "p2-mpg": "P2-", "p3-globaltemp": "P3-", "p4-penguins": "P4-",
    "p5-glue": "P5-", "p6-wine": "P6-", "p7-mpg": "P7-", "p8-chickweight": "P8-",
    "p9-titanic": "P9-", "x-stocks-line": "other-charts", "x-gapminder-scatter": "other-charts",
    "x-taxis-hist": "other-charts", "x-titanic-grouped": "other-charts",
    "m-publication-tips": ("P2-", "other-charts"), "m-quick-seattle": ("other-charts", "P3-"),
    "m-function-happiness": ("P1-", "P2-"),
    "n-slope-gapminder": "P10-", "n-dumbbell-healthexp": "P10-", "n-mix-iowa": "P11-",
    "n-ecdf-taxis": "P12-", "n-ridgeline-seattle": ("P12-", "P4-"),
    "n-training-cancer": "P13-", "n-confusion-wine": "P13-",
}


def metas(d):
    return [json.loads(p.read_text()) for p in sorted(Path(d).rglob("meta.json"))
            if "workspace" not in p.parts]


def tool_calls(m, d):
    """(name, input) for every tool call in the run's transcript (full commands)."""
    t = Path(d) / m["model"] / m["id"] / f"r{m.get('run', 1)}" / "transcript.jsonl"
    if not t.exists():
        t = Path(d) / m["model"] / m["id"] / "transcript.jsonl"
    calls = []
    for line in t.read_text().splitlines() if t.exists() else []:
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            for b in ev.get("message", {}).get("content", []) or []:
                if b.get("type") == "tool_use":
                    calls.append((b.get("name"), b.get("input") or {}))
    return calls


def patterns_read(calls):
    out = []
    for name, inp in calls:
        text = str(inp.get("file_path", "")) if name == "Read" else (
            str(inp.get("command", "")) if name == "Bash" else "")
        for seg in text.split("patterns/")[1:]:
            out.append(seg.split()[0] if seg.split() else seg)
    return out


def routed(m, calls):
    exp = EXPECTED.get(m["id"])
    if exp is None:
        return None
    exp = exp if isinstance(exp, tuple) else (exp,)
    return any(p.startswith(e) for p in patterns_read(calls) for e in exp)


def exemplars_opened(calls):
    return any(n == "Read" and "/exemplars/" in str(i.get("file_path", "")) for n, i in calls)


def reviewed(calls):
    return any(n in ("Agent", "Task") and any(
        w in (str(i.get("description", "")) + str(i.get("prompt", ""))[:400]).lower()
        for w in ("review", "critic", "critique")) for n, i in calls)


def checker_counts(m):
    c = Counter()
    for rep in (m.get("checker") or {}).values():
        if isinstance(rep, dict):
            for i in rep.get("issues", []):
                if i.get("severity") != "INFO":
                    c[i["severity"]] += 1
    return c


def report(d):
    rows = metas(d)
    calls = {id(m): tool_calls(m, d) for m in rows}
    print(f"\n## {Path(d).name}  ({len(rows)} runs)\n")
    print("| model | runs | chart | turn cap | timeout | $/run | s/run | routed | exemplars read | reviewed | ERROR | WARN | STYLE |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    groups = {}
    for m in rows:
        groups.setdefault(m["model"], []).append(m)
    groups["ALL"] = rows
    for model, ms in groups.items():
        n = len(ms)
        chart = sum(any(f.endswith(".png") for f in m["figures"]) for m in ms)
        cap = sum((m.get("turns") or 0) >= 40 for m in ms)
        to = sum(bool(m.get("timed_out")) for m in ms)
        cost = statistics.mean((m.get("cost_usd") or 0) for m in ms)
        secs = statistics.mean(m["duration_s"] for m in ms)
        r = [routed(m, calls[id(m)]) for m in ms if routed(m, calls[id(m)]) is not None]
        ex = sum(exemplars_opened(calls[id(m)]) for m in ms)
        rv = sum(reviewed(calls[id(m)]) for m in ms)
        cc = Counter()
        for m in ms:
            cc += checker_counts(m)
        print(f"| {model} | {n} | {chart} | {cap} | {to} | {cost:.3f} | {secs:.0f} | "
              f"{sum(r)}/{len(r)} | {ex}/{n} | {rv}/{n} | {cc['ERROR']} | {cc['WARN']} | {cc['STYLE']} |")
    misrouted = Counter(m["id"] for m in rows if routed(m, calls[id(m)]) is False)
    if misrouted:
        print("\nMisrouted (prompt: runs): " + ", ".join(f"{k}: {v}" for k, v in misrouted.most_common()))
    codes = Counter()
    for m in rows:
        for rep in (m.get("checker") or {}).values():
            if isinstance(rep, dict):
                for i in rep.get("issues", []):
                    if i.get("severity") != "INFO":
                        codes[i.get("code")] += 1
    if codes:
        print("Checker findings by code: " + ", ".join(f"{k} {v}" for k, v in codes.most_common()))


if __name__ == "__main__":
    for d in sys.argv[1:]:
        report(d)
