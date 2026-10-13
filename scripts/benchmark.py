# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""Docker-free, multi-model benchmark for the matplotlib skill.

Runs each prompt in an isolated clean-room directory with headless
``claude -p``. The clean room contains only the skill under test, a symlink
to ``data/``, and a two-line CLAUDE.md. A fresh CLAUDE_CONFIG_DIR and
``CLAUDE_CODE_DISABLE_BUNDLED_SKILLS=1`` keep user-level and bundled skills
(e.g. a generic ``dataviz`` skill) from competing with the skill under test.

For every run it records cost, turns, wall time, which skill files were read,
the generated scripts and figures, and the output of ``check_figure.py``.

Usage:
    uv run scripts/benchmark.py --label baseline --skill-dir skills/matplotlib
    uv run scripts/benchmark.py --label v2 --models claude-sonnet-5-5 --only p1-titanic
    uv run scripts/benchmark.py --label noskill --no-skill
    uv run scripts/benchmark.py --summarize logs/bench/baseline
    uv run scripts/benchmark.py --recheck logs/bench/baseline  # re-score
    uv run scripts/benchmark.py --label v3 --runs 3            # 3 runs per cell

Results go to logs/bench/<label>/<model>/<prompt-id>/r<k>/. Score them with
scripts/judge.py (absolute and blind pairwise, both A/B orders).

Child runs get an explicit tool allowlist (ALLOWED_TOOLS) instead of bypassing
permissions: file tools, Skill, Agent (the skill's critic subagent), and Bash
scoped to the commands a chart workflow needs. A command outside the list is
denied and the model adapts.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DEFAULT_MODELS = ["claude-sonnet-5-5", "claude-opus-5-5", "claude-haiku-4-5"]
CHECKER = REPO / "skills" / "matplotlib" / "scripts" / "check_figure.py"
WORK_ROOT = Path("/tmp/matplotlib-skill-bench")

BASH_PREFIXES = [
    "uv", "python", "python3", "ls", "head", "tail", "cat", "wc", "mkdir",
    "file", "pwd", "echo", "find", "grep", "cd", "sort", "cut", "cp", "du",
]
ALLOWED_TOOLS = [
    "Read", "Write", "Edit", "Glob", "Grep", "Skill", "Agent", "Task",
    "TodoWrite", "NotebookEdit",
] + [f"Bash({c}:*)" for c in BASH_PREFIXES]

# Host-integration variables that would leak the parent session's skills,
# artifacts, or messaging channel into the child run.
_LEAKY_PREFIXES = (
    "CLAUDE_CODE_SYNC_SKILLS",
    "CLAUDE_CODE_ARTIFACT",
    "CLAUDE_CODE_REMOTE",
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_CODE_CHILD_SESSION",
    "CLAUDE_CODE_ADDITIONAL_DIRECTORIES",
    "CLAUDE_CODE_MESSAGING",
    "CLAUDE_ADDITIONAL_DIRECTORIES",
    "CLAUDECODE",
)


def child_env(config_dir):
    env = {k: v for k, v in os.environ.items() if not k.startswith(_LEAKY_PREFIXES)}
    env["CLAUDE_CONFIG_DIR"] = str(config_dir)
    env["CLAUDE_CODE_DISABLE_BUNDLED_SKILLS"] = "1"
    env["CLAUDE_CODE_DISABLE_POLICY_SKILLS"] = "1"
    return env


def build_clean_room(room, skill_dir):
    # The room must live OUTSIDE this repo: Claude Code discovers skills in
    # ancestor directories, so a room under the repo would see the repo's own
    # .claude/skills/matplotlib. Data is copied, not symlinked, for the same
    # reason (a symlink lets `ls data/..` walk back into the repo).
    if room.exists():
        shutil.rmtree(room)
    (room / ".claude" / "skills").mkdir(parents=True)
    if skill_dir is not None:
        shutil.copytree(
            skill_dir, room / ".claude" / "skills" / "matplotlib", symlinks=False
        )
    shutil.copytree(REPO / "data" / "raw", room / "data" / "raw")
    (room / "CLAUDE.md").write_text(
        "# matplotlib-skill\n\n"
        "Datasets are in `data/raw/`. Save charts to `./figures/`.\n"
    )
    cfg = room.parent / "claude-config"
    cfg.mkdir(exist_ok=True)
    (cfg / ".claude.json").write_text('{"hasCompletedOnboarding": true}')
    return cfg


def parse_transcript(lines):
    """Pull the result record and skill-file reads out of stream-json output."""
    result, reads, skills_invoked, tools = {}, [], [], {}
    for line in lines:
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "result":
            result = ev
        if ev.get("type") != "assistant":
            continue
        for block in ev.get("message", {}).get("content", []) or []:
            if block.get("type") != "tool_use":
                continue
            name = block.get("name", "")
            tools[name] = tools.get(name, 0) + 1
            inp = block.get("input", {}) or {}
            if name == "Skill":
                skills_invoked.append(inp.get("skill") or inp.get("command"))
            if name == "Read" and "skills/matplotlib" in str(inp.get("file_path", "")):
                reads.append(str(inp["file_path"]).split("skills/matplotlib/")[-1])
            if name in ("Agent", "Task"):
                reads.append("agent: " + str(inp.get("description", ""))[:80])
            if name == "Bash" and "skills/matplotlib" in str(inp.get("command", "")):
                reads.append("bash: " + str(inp["command"])[:120])
    return result, reads, skills_invoked, tools


def run_checker(room):
    """Run check_figure.py on each generated chart script, in the clean room."""
    if not CHECKER.exists():
        return None
    room = Path(room).resolve()
    reports = {}
    linked = False
    if not (room / "data").exists():  # archived workspaces drop data/
        (room / "data").symlink_to(REPO / "data")
        linked = True
    scripts = [
        p
        for p in room.rglob("*.py")
        if not {"data", ".claude", ".venv", "venv", "env", "site-packages"}
        & set(p.relative_to(room).parts)
    ]
    for script in sorted(scripts):
        proc = subprocess.run(
            [
                "uv",
                "run",
                "--quiet",
                "--with",
                "matplotlib",
                "--with",
                "seaborn",
                "--with",
                "pandas",
                "--with",
                "numpy",
                "python",
                str(CHECKER),
                "--json",
                str(script),
            ],
            cwd=room,
            capture_output=True,
            text=True,
            timeout=300,
        )
        try:
            reports[script.name] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            reports[script.name] = {"error": (proc.stdout + proc.stderr)[-2000:]}
    if linked:
        (room / "data").unlink()
    return reports


def run_one(case, model, skill_dir, out_root, max_turns, timeout, run_idx=1):
    run_dir = out_root / model / case["id"] / f"r{run_idx}"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    room = WORK_ROOT / out_root.name / model / case["id"] / f"r{run_idx}" / "workspace"
    cfg = build_clean_room(room, skill_dir)
    cmd = [
        "claude",
        "-p",
        case["prompt"],
        "--model",
        model,
        "--max-turns",
        str(max_turns),
        "--output-format",
        "stream-json",
        "--verbose",
        "--setting-sources",
        "project",
        "--allowedTools",
        *ALLOWED_TOOLS,
    ]
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=room,
            env=child_env(cfg),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout, stderr, timed_out = proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired as e:
        stdout = (
            (e.stdout or b"").decode()
            if isinstance(e.stdout, bytes)
            else (e.stdout or "")
        )
        stderr, timed_out = "TIMEOUT", True
    wall = time.time() - t0
    (run_dir / "transcript.jsonl").write_text(stdout)
    if stderr.strip():
        (run_dir / "stderr.txt").write_text(stderr)

    result, reads, skills_invoked, tools = parse_transcript(stdout.splitlines())
    figs = (
        sorted(p.name for p in (room / "figures").glob("*"))
        if (room / "figures").exists()
        else []
    )
    for p in (room / "figures").glob("*.png") if figs else []:
        shutil.copy(p, run_dir / p.name)

    meta = {
        "id": case["id"],
        "kind": case["kind"],
        "pattern": case.get("pattern"),
        "prompt": case["prompt"],
        "checks": case.get("checks", []),
        "model": model,
        "run": run_idx,
        "skill": str(skill_dir) if skill_dir else None,
        "cost_usd": result.get("total_cost_usd"),
        "turns": result.get("num_turns"),
        "duration_s": round(wall, 1),
        "is_error": result.get("is_error", True),
        "timed_out": timed_out,
        "figures": figs,
        "skill_invoked": skills_invoked,
        "skill_files_read": reads,
        "tool_counts": tools,
        "critic_invoked": tools.get("Agent", 0) + tools.get("Task", 0) > 0,
        "exemplars_read": [r for r in reads if r.startswith("exemplars/")],
        "final_message": (result.get("result") or "")[-1500:],
    }
    meta["checker"] = run_checker(room)
    shutil.rmtree(cfg, ignore_errors=True)
    for junk in (room / ".venv", room / "__pycache__", room / "data"):
        shutil.rmtree(junk, ignore_errors=True)
    shutil.move(str(room), run_dir / "workspace")
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def summarize(out_root):
    rows = [json.loads(p.read_text()) for p in sorted(out_root.rglob("meta.json"))
            if "workspace" not in p.parts]
    if not rows:
        print("no results")
        return
    print(
        f"{'model':<20} {'case':<22} {'png':>3} {'turns':>5} {'cost':>7} {'secs':>6}"
        "  skill-files-read / checker"
    )
    for r in rows:
        chk = r.get("checker") or {}
        issues = sum(
            sum(i.get("severity") != "INFO" for i in v.get("issues", []))
            for v in chk.values() if isinstance(v, dict)
        )
        pngs = sum(f.endswith(".png") for f in r["figures"])
        read = ",".join(x for x in r["skill_files_read"] if not x.startswith("bash"))[
            :60
        ]
        print(
            f"{r['model']:<20} {r['id'] + '/r' + str(r.get('run', 1)):<22} {pngs:>3} {r['turns'] or 0:>5} "
            f"{(r['cost_usd'] or 0):>7.3f} {r['duration_s']:>6.0f}"
            f"  [{read}] issues={issues}"
        )
    by_model = {}
    for r in rows:
        m = by_model.setdefault(
            r["model"], {"n": 0, "cost": 0.0, "secs": 0.0, "nopng": 0, "critic": 0}
        )
        m["critic"] += bool(r.get("critic_invoked"))
        m["n"] += 1
        m["cost"] += r["cost_usd"] or 0
        m["secs"] += r["duration_s"]
        m["nopng"] += not any(f.endswith(".png") for f in r["figures"])
    print()
    for model, m in by_model.items():
        print(
            f"{model:<20} runs={m['n']} total_cost=${m['cost']:.2f} "
            f"mean_secs={m['secs'] / m['n']:.0f} no_png={m['nopng']} "
            f"critic_runs={m['critic']}"
        )
    (out_root / "summary.json").write_text(json.dumps(rows, indent=2))


def make_pairs(dir_a, dir_b, seed=0):
    """Copy matching runs' PNGs into pairs/<model>__<case>/{A,B}.png in random order.

    The key mapping A/B back to the source dirs goes to pairs-key.json, which the
    judges must not read.
    """
    import random

    rng = random.Random(seed)
    out = dir_b.parent / f"pairs-{dir_a.name}-vs-{dir_b.name}"
    shutil.rmtree(out, ignore_errors=True)
    key = {}
    for meta in sorted(dir_a.rglob("meta.json")):
        rel = meta.parent.relative_to(dir_a)
        other = dir_b / rel
        if not (other / "meta.json").exists():
            continue
        sides = [meta.parent, other]
        rng.shuffle(sides)
        pair = out / "__".join(rel.parts)
        pair.mkdir(parents=True)
        for label, src in zip("AB", sides):
            pngs = sorted(src.glob("*.png"))
            for k, png in enumerate(pngs):
                shutil.copy(png, pair / f"{label}{'' if k == 0 else k + 1}.png")
            key[pair.name + "/" + label] = (dir_a if src == meta.parent else dir_b).name
        m = json.loads(meta.read_text())
        (pair / "task.json").write_text(
            json.dumps({"prompt": m["prompt"], "checks": m["checks"]}, indent=2)
        )
    (dir_b.parent / f"pairs-key-{dir_a.name}-vs-{dir_b.name}.json").write_text(
        json.dumps(key, indent=2)
    )
    print(f"{len(key) // 2} pairs → {out}")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--label", help="results subdirectory under logs/bench/")
    ap.add_argument("--skill-dir", default=str(REPO / "skills" / "matplotlib"))
    ap.add_argument(
        "--no-skill", action="store_true", help="baseline run without the skill"
    )
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS))
    ap.add_argument(
        "--prompts", default=str(REPO / "scripts" / "benchmark_prompts.yaml")
    )
    ap.add_argument("--only", help="comma-separated prompt ids")
    ap.add_argument("--parallel", type=int, default=6)
    ap.add_argument("--runs", type=int, default=1, help="independent runs per cell")
    ap.add_argument("--max-turns", type=int, default=40)
    ap.add_argument("--timeout", type=int, default=1200, help="seconds per run")
    ap.add_argument(
        "--summarize", help="print summary for an existing results dir and exit"
    )
    ap.add_argument(
        "--recheck", help="re-run check_figure.py on every run in a results dir"
    )
    ap.add_argument(
        "--pair",
        nargs=2,
        metavar=("DIR_A", "DIR_B"),
        help="build blinded A/B pairs of two results dirs for pairwise judging",
    )
    args = ap.parse_args()

    if args.pair:
        make_pairs(Path(args.pair[0]), Path(args.pair[1]))
        return

    if args.summarize:
        summarize(Path(args.summarize))
        return
    if args.recheck:
        metas = sorted(
            p for p in Path(args.recheck).resolve().rglob("meta.json")
            if "workspace" not in p.parts
        )
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            reports = pool.map(lambda p: run_checker(p.parent / "workspace"), metas)
            for path, rep in zip(metas, reports):
                meta = json.loads(path.read_text())
                meta["checker"] = rep
                path.write_text(json.dumps(meta, indent=2))
        summarize(Path(args.recheck))
        return
    if not args.label:
        sys.exit("--label is required")
    if shutil.which("claude") is None:
        sys.exit("claude CLI not found on PATH")

    cases = yaml.safe_load(Path(args.prompts).read_text())
    if args.only:
        wanted = set(args.only.split(","))
        cases = [c for c in cases if c["id"] in wanted]
    skill_dir = None if args.no_skill else Path(args.skill_dir).resolve()
    out_root = REPO / "logs" / "bench" / args.label
    out_root.mkdir(parents=True, exist_ok=True)
    models = args.models.split(",")
    jobs = [(c, m, k) for k in range(1, args.runs + 1) for m in models for c in cases]
    print(f"{len(jobs)} runs → {out_root}", flush=True)

    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futs = {
            pool.submit(
                run_one, c, m, skill_dir, out_root, args.max_turns, args.timeout, k
            ): (c, m, k)
            for c, m, k in jobs
        }
        for fut in as_completed(futs):
            c, m, k = futs[fut]
            try:
                meta = fut.result()
                print(
                    f"done {m} {c['id']} r{k}: {len(meta['figures'])} files, "
                    f"${meta['cost_usd'] or 0:.3f}, {meta['duration_s']:.0f}s",
                    flush=True,
                )
            except Exception as e:  # keep the batch going
                print(f"FAIL {m} {c['id']} r{k}: {e!r}", flush=True)
    summarize(out_root)


if __name__ == "__main__":
    main()
