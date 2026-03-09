# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""Automated evaluation of the matplotlib-chart skill for style compliance.

Checks chart-patterns.md against the style rules defined in CLAUDE.md and
style-reference.md. Can be run standalone or called from the iterate-skill
workflow.

Usage:
    uv run scripts/evaluate_skill.py
    uv run scripts/evaluate_skill.py --check-renders  # also verify PNGs exist
    uv run scripts/evaluate_skill.py --json            # machine-readable output
"""

import argparse
import json
import re
import sys
from pathlib import Path


def _find_repo_root():
    """Find the repo root by looking for .claude/skills/ directory."""
    script_dir = Path(__file__).resolve().parent
    # scripts/ or scratch/ -> parent is repo root
    if (script_dir.parent / ".claude" / "skills").is_dir():
        return script_dir.parent
    # Workspace root (clean room)
    if (script_dir / ".claude" / "skills").is_dir():
        return script_dir
    return script_dir.parent


REPO_ROOT = _find_repo_root()
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "matplotlib-chart"
CHART_PATTERNS = SKILL_DIR / "chart-patterns.md"
FIGURES_DIR = REPO_ROOT / "scratch" / "figures"

EXPECTED_THEME = 'sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")'
EXPECTED_DESPINE = "sns.despine(left=True, bottom=True)"
DEPRECATED_CALLS = ["sns.set()", "plt.hold()", "sns.set_style(", "sns.set_context("]
LEGEND_MARKERS = ["frameon=True", 'facecolor="white"']
ANNOTATION_COLOR = "dimgrey"

_CODE_BLOCK_RE = re.compile(r"```python\n(.*?)```", re.DOTALL)


def extract_pattern_blocks(content: str) -> dict[str, str]:
    """Split chart-patterns.md into numbered pattern blocks."""
    blocks = {}
    pattern = re.compile(r"^## (\d+)\.\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(content))

    for i, match in enumerate(matches):
        num = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        blocks[num] = content[start:end]

    return blocks


def _extract_code(block: str) -> str:
    """Extract all Python code blocks from a markdown block."""
    return "\n".join(_CODE_BLOCK_RE.findall(block))


def check_theme_calls(blocks: dict[str, str]) -> list[dict]:
    """Check that every pattern has the correct sns.set_theme() call."""
    results = []
    for num, block in blocks.items():
        code = _extract_code(block)
        has_theme = "sns.set_theme(" in code
        correct_theme = EXPECTED_THEME in code

        if not has_theme:
            results.append(
                {"pattern": num, "check": "sns.set_theme", "status": "MISSING",
                 "detail": "No sns.set_theme() call found in code block"}
            )
        elif not correct_theme:
            theme_match = re.search(r"sns\.set_theme\([^)]+\)", code)
            actual = theme_match.group(0) if theme_match else "unknown"
            results.append(
                {"pattern": num, "check": "sns.set_theme", "status": "WRONG",
                 "detail": f"Found: {actual}"}
            )
        else:
            results.append(
                {"pattern": num, "check": "sns.set_theme", "status": "OK", "detail": ""}
            )
    return results


def check_despine(blocks: dict[str, str]) -> list[dict]:
    """Check that every pattern has sns.despine(left=True, bottom=True)."""
    results = []
    for num, block in blocks.items():
        code = _extract_code(block)
        has_despine = "sns.despine(" in code
        correct_despine = EXPECTED_DESPINE in code

        if not has_despine:
            results.append(
                {"pattern": num, "check": "sns.despine", "status": "MISSING",
                 "detail": "No sns.despine() call found"}
            )
        elif not correct_despine:
            despine_match = re.search(r"sns\.despine\([^)]+\)", code)
            actual = despine_match.group(0) if despine_match else "unknown"
            results.append(
                {"pattern": num, "check": "sns.despine", "status": "WRONG",
                 "detail": f"Found: {actual}"}
            )
        else:
            results.append(
                {"pattern": num, "check": "sns.despine", "status": "OK", "detail": ""}
            )
    return results


def check_dpi(blocks: dict[str, str]) -> list[dict]:
    """Check that all patterns specify dpi=150 (default output)."""
    results = []
    for num, block in blocks.items():
        code = _extract_code(block)
        dpi_matches = re.findall(r"dpi=(\d+)", code)
        if not dpi_matches:
            results.append(
                {"pattern": num, "check": "dpi", "status": "MISSING",
                 "detail": "No dpi= parameter found"}
            )
        elif all(d == "150" for d in dpi_matches):
            results.append(
                {"pattern": num, "check": "dpi", "status": "OK", "detail": ""}
            )
        else:
            wrong = [d for d in dpi_matches if d != "150"]
            results.append(
                {"pattern": num, "check": "dpi", "status": "WRONG",
                 "detail": f"Found dpi={', '.join(wrong)} (should be 150)"}
            )
    return results


def check_deprecated(content: str) -> list[dict]:
    """Check for deprecated API calls across all patterns."""
    results = []
    for call in DEPRECATED_CALLS:
        if call in content:
            for i, line in enumerate(content.split("\n"), 1):
                if call in line:
                    results.append(
                        {"pattern": "all", "check": "deprecated", "status": "FAIL",
                         "detail": f"Line {i}: {call}"}
                    )
    if not results:
        results.append(
            {"pattern": "all", "check": "deprecated", "status": "OK",
             "detail": "No deprecated API calls found"}
        )
    return results


def check_legend_styling(blocks: dict[str, str]) -> list[dict]:
    """Check that legends use frameon=True, facecolor='white' where present."""
    results = []
    for num, block in blocks.items():
        code = _extract_code(block)
        if "legend(" not in code:
            continue

        missing = [m for m in LEGEND_MARKERS if m not in code]
        if not missing:
            results.append(
                {"pattern": num, "check": "legend_style", "status": "OK", "detail": ""}
            )
        else:
            results.append(
                {"pattern": num, "check": "legend_style", "status": "MISSING",
                 "detail": f"Missing: {', '.join(missing)}"}
            )
    return results


def check_annotation_color(blocks: dict[str, str]) -> list[dict]:
    """Check that annotation text uses color='dimgrey'."""
    results = []
    for num, block in blocks.items():
        code = _extract_code(block)
        if "ax.text(" not in code and ".text(" not in code:
            continue

        if ANNOTATION_COLOR in code:
            results.append(
                {"pattern": num, "check": "annotation_color", "status": "OK",
                 "detail": ""}
            )
        else:
            results.append(
                {"pattern": num, "check": "annotation_color", "status": "MISSING",
                 "detail": f'Text annotations without color="{ANNOTATION_COLOR}"'}
            )
    return results


def check_renders(figures_dir: Path) -> list[dict]:
    """Check that expected PNG files exist and have non-zero size.

    Matches both bare names (01_horizontal_bar.png) and suffixed variants
    (01_horizontal_bar_synthetic.png, 01_horizontal_bar_car_crashes.png).
    """
    expected_prefixes = [
        ("01", "horizontal_bar"),
        ("02", "vertical_bar"),
        ("03", "time_series"),
        ("04", "violin_strip"),
        ("05", "lollipop"),
        ("07", "heatmap"),
        ("08", "multi_panel"),
        ("09", "pr_roc"),
    ]
    results = []
    for num, prefix in expected_prefixes:
        matches = sorted(figures_dir.glob(f"{num}_{prefix}*.png"))
        if not matches:
            results.append(
                {"pattern": num, "check": "render", "status": "MISSING",
                 "detail": f"{num}_{prefix}*.png not found"}
            )
        else:
            for fpath in matches:
                st = fpath.stat()
                if st.st_size == 0:
                    results.append(
                        {"pattern": num, "check": "render", "status": "EMPTY",
                         "detail": f"{fpath.name} is 0 bytes"}
                    )
                else:
                    results.append(
                        {"pattern": num, "check": "render", "status": "OK",
                         "detail": f"{fpath.name} ({st.st_size / 1024:.0f} KB)"}
                    )
    return results


def summarize(all_results: list[dict]) -> dict:
    """Produce a summary of all check results."""
    total = len(all_results)
    ok = sum(1 for r in all_results if r["status"] == "OK")
    issues = [r for r in all_results if r["status"] != "OK"]
    return {
        "total_checks": total,
        "passed": ok,
        "failed": total - ok,
        "score": f"{ok}/{total}",
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate matplotlib-chart skill")
    parser.add_argument(
        "--check-renders",
        action="store_true",
        help="Also check that rendered PNGs exist in scratch/figures/",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=FIGURES_DIR,
        help="Directory containing rendered PNGs",
    )
    args = parser.parse_args()

    if not CHART_PATTERNS.exists():
        print(f"ERROR: {CHART_PATTERNS} not found")
        sys.exit(1)

    content = CHART_PATTERNS.read_text()
    blocks = extract_pattern_blocks(content)

    if not blocks:
        print("ERROR: No pattern blocks found in chart-patterns.md")
        sys.exit(1)

    all_results = []
    all_results.extend(check_theme_calls(blocks))
    all_results.extend(check_despine(blocks))
    all_results.extend(check_dpi(blocks))
    all_results.extend(check_deprecated(content))
    all_results.extend(check_legend_styling(blocks))
    all_results.extend(check_annotation_color(blocks))

    if args.check_renders:
        all_results.extend(check_renders(args.figures_dir))

    summary = summarize(all_results)

    if args.json:
        output = {"summary": summary, "results": all_results}
        print(json.dumps(output, indent=2))
    else:
        print("=" * 60)
        print("Matplotlib Chart Skill — Style Compliance Report")
        print("=" * 60)
        print(f"\nPatterns found: {len(blocks)} ({', '.join(sorted(blocks.keys()))})")
        print(f"Score: {summary['score']}")
        print()

        checks = {}
        for r in all_results:
            checks.setdefault(r["check"], []).append(r)

        for check_name, check_results in checks.items():
            ok_count = sum(1 for r in check_results if r["status"] == "OK")
            total = len(check_results)
            status = "PASS" if ok_count == total else "ISSUES"
            print(f"  [{status}] {check_name}: {ok_count}/{total}")
            for r in check_results:
                if r["status"] != "OK":
                    print(f"         P{r['pattern']}: {r['status']} — {r['detail']}")

        print()
        if summary["failed"] == 0:
            print("All checks passed.")
        else:
            print(f"{summary['failed']} issue(s) found.")

    sys.exit(0 if summary["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
