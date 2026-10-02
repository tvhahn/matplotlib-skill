# matplotlib-skill

## Project Purpose

This repo is the **source of truth** for Tim's `matplotlib` Claude Code skill AND a gallery documenting its evolution for a blog article about iteratively building a Claude Code skill.

The skill generates publication-quality matplotlib/seaborn charts matching Tim's personal aesthetic (whitegrid, DejaVu Sans, cubehelix/ColorBrewer palettes, despined, annotation-rich).

## Blog Article

This repo doubles as evidence for a blog article. See `docs/blog/building-a-claude-code-skill.md` for the blog post draft.

### Key Paths

- `skills/matplotlib/` — SKILL.md, style-reference.md, patterns/P1–P9 + other-charts.md, scripts/check_figure.py (canonical; `.claude/skills/matplotlib` is a symlink)
- `data/` — datasets.yaml manifest, raw/ datasets
- `scripts/` — benchmark.py (+ benchmark_prompts.yaml, judge_rubric.md), chart-test-container.sh, evaluate_skill.py
- `tests/test_patterns.py` — executes every pattern template on real data and lints the figure
- `docs/gallery/` — key iteration snapshots (00-original-inspiration, 50-template-improvements-v2, TEMPLATE.md)
- `gallery-archive/` — all 51 iteration entries (local-only, git-excluded via `.git/info/exclude`)

## Skill Discovery

- **In-repo:** Claude Code finds `skills/matplotlib/SKILL.md` (also via symlink at `.claude/skills/matplotlib/SKILL.md`)
- **Global:** Two-hop symlink from `~/.claude/skills/` → `~/dotfiles/` → this repo (edits propagate instantly)
- **Rule:** Never edit skill files in dotfiles or `~/.claude/skills/` directly

## Gallery Workflow

Each `gallery-archive/NN-name/` folder captures the skill's output at a specific iteration point. To create a new gallery entry:

1. Make skill changes in `skills/matplotlib/`
2. Run `scripts/chart-test-container.sh --quick` (or full run without `--quick`) to generate charts in a clean room
3. Create `gallery-archive/NN-name/` folder (next sequential number)
4. Copy relevant PNGs from `logs/clean-room/latest/` into the gallery folder
5. Write `README.md` following `docs/gallery/TEMPLATE.md`
6. No commit needed — `gallery-archive/` is git-excluded

**Note:** `gallery-archive/` is excluded from git via `.git/info/exclude` (local-only, not shared on clone). It contains all 51 development iterations. Only `docs/gallery/00-original-inspiration/` and `docs/gallery/50-template-improvements-v2/` are tracked in git (referenced by blog post and README).

## Style Rules

All charts follow the aesthetic defined in `skills/matplotlib/style-reference.md`:

- `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")` -- identical in every pattern
- `sns.despine(left=True, bottom=True)` -- all spines removed
- Legends: `frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey"`
- Annotations: `color="dimgrey"`
- Standard output: 150 DPI, PDF+PNG dual save
- Publication output (on explicit request): 300 DPI, PDF+PNG dual save
- Exploratory output: 150 DPI, PNG-only

## Verification

```bash
# Primary (no Docker): multi-model benchmark in isolated clean rooms outside the repo
uv run scripts/benchmark.py --label v2                          # 12 prompts × Sonnet/Opus/Haiku
uv run scripts/benchmark.py --label quick --models claude-sonnet-5-5 --only p1-titanic,x-stocks-line
uv run scripts/benchmark.py --label noskill --no-skill --models claude-sonnet-5-5
uv run scripts/benchmark.py --recheck logs/bench/v2             # re-score with current checker
# Then judge PNGs with vision subagents using scripts/judge_rubric.md

# Pattern templates must run clean (fast, no Claude calls)
uv run --no-project --with pytest --with matplotlib --with seaborn --with pandas --with numpy \
    pytest tests/test_patterns.py -q

# Lint any chart script (also what the skill runs in its workflow)
uv run skills/matplotlib/scripts/check_figure.py path/to/chart.py

# Docker clean room (original harness)
scripts/chart-test-container.sh                    # all 9 prompts, random from pools
scripts/chart-test-container.sh --quick            # 5 prompts, random from pools
scripts/chart-test-container.sh --fixed            # all 9 prompts, original defaults
scripts/chart-test-container.sh --quick --fixed    # 5 prompts, original defaults
scripts/chart-test-container.sh --full-archive     # keep data/ in workspace archives

# Static analysis (fast, no Docker)
uv run scripts/evaluate_skill.py --check-renders

```

Quick consistency checks:

```bash
# All sns.set_theme calls should be identical
grep 'sns.set_theme' skills/matplotlib/patterns/*.md

# All patterns should use dpi=150
grep 'dpi=' skills/matplotlib/patterns/*.md
```

## Autonomous Commands

| Command | When to use | Key behavior |
|---------|------------|--------------|
| `/iterate-skill` | "What should I improve?" | Single eval→improve→gallery cycle |
| `/variation-analysis PN` | "Does this pattern pass quality checks?" | 3 parallel clean rooms per round, dataset variety |
| `/variation-analysis-single PN` | Single-dataset quality check | All runs use same prompt |
| `/variation-analysis-all [P1,P3,P5]` | Sweep multiple patterns | Per-pattern subagent isolation |
| `/autoresearch <tag>` | Fully autonomous loop | Branch `autoresearch/<tag>`, keep/revert per experiment |

**Guardrails:** max 5 rounds, no pattern deletions, `sns.set_theme` and `sns.despine` immutable.

**Autoresearch scoring (v2):** compliance (0/1 gate), visual (10-check tiered rubric with worst-of-3 floor), refinement (5-check graded 0–3), adaptiveness (5-check graded 0–3). Composite = compliance × (0.50 × visual + 0.25 × refinement + 0.25 × adaptiveness) × signature_penalty (quadratic). Evaluation delegated to Agent subagents for context efficiency. See `docs/specs/autoresearch-v2/` for full spec and `.claude/commands/autoresearch.md` for implementation.

**Circuit breakers:** 10 consecutive discards → next pattern; Docker failure → halt; pattern above 0.90 → skip (diminishing returns); all above threshold → patrol mode.

## Plan Verification — MANDATORY

**When implementing a plan that includes a "Verification" section, you MUST execute every verification step before considering the work complete.** This is non-negotiable. Do not skip verification because the code "looks right" or because you "just wrote it." Run the commands, check the output, and confirm each expected result. If a verification step fails, fix the issue and re-verify. Unverified work is unfinished work.

## Future Work

`patterns/other-charts.md` covers line, scatter, histogram, and grouped bar with short templates.
Candidates for full patterns if usage warrants: stacked/100% bar, `fill_between` area, slope chart.

Benchmark isolation note: Claude Code discovers skills in ancestor directories, so clean rooms
must live outside this repo (benchmark.py uses /tmp/matplotlib-skill-bench).

## Reference

- @skills/matplotlib/SKILL.md — full skill workflow and persona
- @skills/matplotlib/style-reference.md — complete style specification
- @docs/gallery/TEMPLATE.md — gallery entry template
- @data/datasets.yaml — dataset manifest
- @docs/blog/building-a-claude-code-skill.md — blog post draft
