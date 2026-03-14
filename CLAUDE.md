# matplotlib-chart-skill

## Project Purpose

This repo is the **source of truth** for Tim's `matplotlib-chart` Claude Code skill AND a gallery documenting its evolution for a blog article about iteratively building a Claude Code skill.

The skill generates publication-quality matplotlib/seaborn charts matching Tim's personal aesthetic (whitegrid, DejaVu Sans, cubehelix/ColorBrewer palettes, despined, annotation-rich).

## Blog Article Narrative

This repo doubles as the evidence base for a blog article about iteratively building a Claude Code skill. The gallery (`docs/gallery/`) IS the article's visual narrative — each entry corresponds to a chapter in the story.

### Narrative Arc

| Phase | Gallery Entries | Blog Chapter |
|-------|----------------|--------------|
| **Origin** | `00-original-inspiration` | "Starting from real research code" — how 4 projects became 9 chart patterns |
| **Baseline** | `01-original` | "Capturing the starting point" — why you need a before picture |
| **Visual iteration** | `02-current` through `06-subplot-outlines` | "Iterating on aesthetics" — API modernization, consistency audits, verification checklists |
| **Infrastructure pivot** | `07-datasets-and-evaluation`, `08-clean-room-testing` | "From eyeballing to automation" — devcontainer, datasets, Docker clean-room testing |
| **Autonomous iteration** | `09+` (future) | "Letting the agent drive" — `/iterate-skill` in practice |

### Design Principles for Gallery Entries

- Each entry must stand alone — a reader should understand the change from the README alone
- Include PNGs as evidence, not decoration — every image should demonstrate a specific improvement or capability
- Process changes are as important as visual changes — document them with the same rigor
- "Lessons Learned" sections are the most valuable part for the blog — write them for a reader building their own skill

### Key files

```
.claude/skills/matplotlib-chart/
  SKILL.md              # Persona, 5-phase workflow, code generation rules
  style-reference.md    # Full style spec (palettes, sizing, save conventions)
  chart-patterns.md     # 9 self-contained code patterns by chart type

data/
  datasets.yaml         # Manifest of all datasets (source project + public)
  SOURCES.md            # Attribution and licensing for all datasets
  fetch_datasets.py     # Download script for public reference datasets
  raw/                  # All datasets (committed to repo)
    arxiv/              # arxiv-code-search (4,665 rows)
    beautiful-plots/    # Beautiful-Plots (birth %, classifier AUC)
    ml-tool-wear/       # Tool wear labels (167 rows)
    weibull/            # Weibull RUL experiments + HDF5 spectrograms
    public/             # Curated public datasets (29 CSVs)

docs/gallery/           # Before/after captures at each iteration
  TEMPLATE.md           # Template for new gallery entries
  00-original-inspiration/  # ... through 06-subplot-outlines/

scratch/
  figures/                # Working output directory (gitignored PNGs)

logs/clean-room/            # Archived clean-room runs (gitignored)

scripts/
  chart-test-container.sh # Primary verification — Claude Code generates charts in Docker clean room
  evaluate_skill.py       # Static analysis — checks chart-patterns.md for style compliance
  test_chart_patterns.py  # Optional syntax check — directly runs chart-patterns.md code blocks
```

## Skill Discovery

Claude Code discovers the skill through two mechanisms:

- **Devcontainer / any clone:** Claude Code finds `.claude/skills/matplotlib-chart/SKILL.md` directly from the repo -- no symlinks needed.
- **Host (global availability):** A two-hop symlink chain makes the skill available outside this repo:

```
~/.claude/skills/matplotlib-chart
  -> ~/dotfiles/claude/skills/matplotlib-chart/
    -> ~/Documents/matplotlib-chart-skill/.claude/skills/matplotlib-chart  (this repo)
```

Edits to skill files in this repo propagate instantly to `~/.claude/skills/` -- no copy or sync step needed. Do not create or modify skill files directly in dotfiles or `~/.claude/skills/`.

## Gallery Workflow

Each `docs/gallery/NN-name/` folder captures the skill's output at a specific iteration point. To create a new gallery entry:

1. Make skill changes in `.claude/skills/matplotlib-chart/`
2. Run `scripts/chart-test-container.sh --quick` (or full run without `--quick`) to generate charts in a clean room
3. Create `docs/gallery/NN-name/` folder (next sequential number)
4. Copy relevant PNGs from `logs/clean-room/latest/` into the gallery folder
5. Write `README.md` following `docs/gallery/TEMPLATE.md`
6. Commit

## Existing Gallery Entries

| Entry | Description |
|---|---|
| `00-original-inspiration` | Source material from 4 projects that inspired the skill's 9 chart patterns |
| `01-original` | Baseline from the original commit -- captures all quirks before improvements |
| `02-current` | API modernization (`sns.set()` -> `sns.set_theme()`, pandas iloc fixes) + visual polish (dimgrey annotations, framed legends, `sns.despine()`) |
| `03-dpi-optimization` | Added verification render at 150 DPI during iterative development; final output stays 300 DPI |
| `04-consistency-audit` | Fixed 5 patterns with inconsistent `sns.set_theme()` calls or wrong `dpi=` values |
| `05-verification-checklist` | Rewrote Phase 5 verification from vague prose to a 7-item numbered checklist |
| `06-subplot-outlines` | Added `ax.patch` subplot borders to pattern 8; replaced sine test data with synthetic RUL predictions |
| `07-datasets-and-evaluation` | Infrastructure pivot: devcontainer, public datasets, evaluate_skill.py, /iterate-skill command, DPI 300→150 |
| `08-clean-room-testing` | Docker clean-room verification: Claude Code generates charts from one-line prompts in isolated container |
| `14-tick-marks-and-evaluator` | Fixed evaluator despine check for superset args; added tick_params to P1-P3; dimgrey legend text to P3 |
| `15-violin-lollipop-polish` | Added tick_params to P4-P6; fixed P4 grid alpha; added title placeholders to P5/P6 |
| `16-pr-roc-and-multipanel-consistency` | P9 spelling/label/title fixes; tick_params + dimgrey legend text for P6/P8/P9 |
| `17-labelcolor-cleanup` | Replaced legend `get_texts()` loops with inline `labelcolor="dimgrey"` in P3, P5, P9 |
| `18-labelcolor-complete` | Completed `labelcolor` migration for P6, P8; updated style-reference.md legend convention |
| `19-title-consistency` | Normalized title `loc="left"` and `pad` across P1, P2, P4 for consistency |
| `20-spectrogram-prroc-title-padding` | Added `pad=7` to P7/P9 titles; added `grid(False)` to P7 subplots |
| `21-title-fontsize-p3-p8` | Added explicit `fontsize=12` to P3 and P8 titles (bold-prefix convention) |
| `22-dimgrey-tick-labels` | Added `labelcolor="dimgrey"` tick_params convention to style-reference, P1, P4 |
| `23-dimgrey-tick-labels-p2-p3-p5` | Added `labelcolor="dimgrey"` to tick_params in P2, P3, P5; consolidated P5 split calls |
| `24-dimgrey-tick-labels-p6-p7-p8` | Added `labelcolor="dimgrey"` to tick_params in P6, P7 (both subplots), P8 |
| `25-dimgrey-tick-labels-p9-pad-consistency` | Completed `labelcolor="dimgrey"` rollout to P9; normalized P2 title pad to 7 |
| `26-full-suite-coverage` | P6/P7/P8 pattern rewrites for clean-room testability; all 9 prompts verified |
| `27-p2-variation-analysis` | Parallel clean-room comparison (3x3 runs) to find and fix P2 under-specification |
| `28-p3-variation-analysis` | P3 rewrite from ML-prediction specialist to general time series; 3-round convergence |
| `29-p7-variation-analysis` | P7 correlation heatmap: rocket to RdBu_r diverging palette; 2-round convergence |
| `29-dataset-variety` | Added 20 public datasets; per-pattern prompt pools with random selection in clean-room testing |
| `30-p5-variation-analysis` | P5 lollipop: concrete sizes replacing `"x-large"`, legend loc fix, 10-item Rules section; 3-round convergence |
| `31-p6-variation-analysis` | P6 vertical bar: palette slice order, annotation format (no unit suffix), x-axis label rules; 2-round convergence |
| `32-p8-variation-analysis` | P8 multi-panel: rewrite from RUL prediction to line+scatter trend template; single color, shared y-axis, 8 rules; 2-round convergence |
| `33-p9-variation-analysis` | P9 decision boundary: DIVERGING_COLORBLIND mandate, prob dots not contourf, two outside legends, 7 rules; 2-round convergence |
| `34-p1-variation-analysis` | P1 horizontal bar: added 10-item Rules section (Blues_d mandate, sns.barplot not ax.barh, no annotation prefixes/suffixes, set_xticks([]), fontsize=14); 3-round convergence 4/10 to 9/10 |
| `35-p4-variation-analysis` | P4 PR/ROC: removed sharex/sharey, added 12-item Rules section (k-fold mandate, panel order, no fill_between/suptitle/ax.patch, axis label styling); 2-round convergence |
| `36-p4-variation-analysis` | P4 PR/ROC: added 4 rules (Average label prefix, no axhline, no axis limits, k-fold mandatory default), explicit alpha=0.5; 3-round convergence |
| `37-p8-variation-analysis` | P8 multi-panel: 12 numbered rules (pal[5] mandate, no fill_between/SEM/area, exact wspace/hspace, 2x2 figsize, no per-event colors); 3-round convergence |

## Style Rules

All charts follow the aesthetic defined in `.claude/skills/matplotlib-chart/style-reference.md`:

- `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")` -- identical in every pattern
- `sns.despine(left=True, bottom=True)` -- all spines removed
- Legends: `frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey"`
- Annotations: `color="dimgrey"`
- Standard output: 150 DPI, PDF+PNG dual save
- Publication output (on explicit request): 300 DPI, PDF+PNG dual save
- Exploratory output: 150 DPI, PNG-only

## Verification

```bash
# Primary: Claude Code generates charts from minimal prompts (Docker required)
scripts/chart-test-container.sh                    # all 9 prompts, random from pools
scripts/chart-test-container.sh --quick            # 5 prompts, random from pools
scripts/chart-test-container.sh --fixed            # all 9 prompts, original defaults
scripts/chart-test-container.sh --quick --fixed    # 5 prompts, original defaults
scripts/chart-test-container.sh --full-archive     # keep data/ in workspace archives

# Static analysis (fast, no Docker)
uv run scripts/evaluate_skill.py --check-renders

# Optional: syntax check of chart-patterns.md code blocks
uv run scripts/test_chart_patterns.py
```

Quick consistency checks:

```bash
# All sns.set_theme calls should be identical
grep 'sns.set_theme' .claude/skills/matplotlib-chart/chart-patterns.md

# All patterns should use dpi=150
grep 'dpi=' .claude/skills/matplotlib-chart/chart-patterns.md
```

## Autonomous Iteration

Use `/iterate-skill` to run a single evaluation-improvement-documentation cycle. The command:

1. Evaluates current skill state (static analysis + latest clean-room results)
2. Identifies 1-2 improvements
3. Applies changes, verifies via `scripts/chart-test-container.sh --quick` (Docker clean room)
4. Creates a gallery entry from clean-room results and atomic commit

Use `/variation-analysis PN` to run targeted convergence analysis on a single pattern with **dataset variety**. Each parallel run uses a different prompt from the pool, so convergence is tested across both structural dimensions and different datasets. Configurable rounds (`--rounds N`, default 3, max 5). The command:

1. Selects 3 different prompts from the pattern's pool per round
2. Runs 3 parallel clean rooms with different datasets (Round 1: tags A, B, C)
3. Compares generated code across structural dimensions (excludes data-handling, which naturally differs)
4. Fixes under-specified dimensions in `chart-patterns.md`
5. Validates with subsequent rounds until convergence or round limit
6. Creates a gallery entry with PNGs + convergence tables + "Prompts Used" mapping

Use `/variation-analysis-single PN` for the original single-dataset behavior — all parallel runs use the same prompt. Useful when iterating on a specific dataset (e.g., `--prompt "lollipop chart of happiness score..."`).

Use `/variation-analysis-all [P1,P3,P5] [--rounds N]` to run variation analysis across multiple patterns. Each pattern is handled by a dedicated Agent subagent in its own context window, solving the context accumulation problem. Each subagent runs the full workflow (rounds, fixes, gallery entry, commit) and returns a one-line summary. Use this for batch analysis across all 9 patterns.

Use `/iterate-skill` when the question is "what should I improve?", `/variation-analysis` when the question is "why does this pattern diverge?", and `/variation-analysis-all` to sweep all patterns autonomously.

Guardrails: max rounds configurable per pattern (default 3, max 5), no pattern deletions, style invariants (`sns.set_theme` and `sns.despine`) are immutable.

## Autoresearch

Use `/autoresearch <tag>` to run an autonomous skill improvement loop inspired by Karpathy's autoresearch. The command runs indefinitely (until interrupted or all patterns exceed the threshold), modifying `chart-patterns.md`, evaluating via a composite metric, keeping improvements, and reverting regressions.

**How it works:**
1. Creates branch `autoresearch/<tag>` (or resumes if it exists)
2. Computes baseline composite scores for all 9 patterns (compliance × convergence × visual × refinement)
3. Picks the lowest-scoring pattern and proposes a small, specific change
4. Evaluates via 3 parallel clean rooms + static analysis + visual rubric
5. Keeps improvements (branch advances), reverts regressions (`git reset --hard HEAD~1`)
6. Loops back to step 3

**Key files:**
- `program.md` — human-authored research priorities, read each iteration
- `results.tsv` — append-only experiment log (gitignored), enables resume across sessions
- `.claude/commands/autoresearch.md` — the command itself

**Composite scoring:** Each pattern gets four layer scores:
- **Compliance** (0/1): `evaluate_skill.py --json --pattern N`
- **Convergence** (0–1): 3 parallel clean rooms → structural dimension comparison
- **Visual** (0–1): 10-check graded rubric (0/1/2 per check) × 3 PNGs, with red-flag caps
- **Refinement** (0–1): 5 binary code-quality checks across the 3 generated scripts

**Circuit breakers:** 10 consecutive discards → next pattern; Docker failure → halt; all above threshold → patrol mode; 50+ experiments → warn about context window

**Reviewing results:** `git log autoresearch/<tag>` shows kept improvements. `results.tsv` has the full experiment history including discards.

**Relationship to other commands:**
- `/iterate-skill` — human-triggered single cycle with gallery entries
- `/variation-analysis` — targeted convergence analysis on one pattern
- `/autoresearch` — fully autonomous loop, no gallery entries, git history IS the documentation

## Plan Verification — MANDATORY

**When implementing a plan that includes a "Verification" section, you MUST execute every verification step before considering the work complete.** This is non-negotiable. Do not skip verification because the code "looks right" or because you "just wrote it." Run the commands, check the output, and confirm each expected result. If a verification step fails, fix the issue and re-verify. Unverified work is unfinished work.

## Future Work

Deferred patterns not yet in `chart-patterns.md`:
- Scatter plot (standalone, not decision-boundary)
- Grouped bar chart
- `fill_between` area chart
