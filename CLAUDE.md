# matplotlib-chart-skill

## Project Purpose

This repo is the **source of truth** for Tim's `matplotlib-chart` Claude Code skill AND a gallery documenting its evolution for a blog article about iteratively building a Claude Code skill.

The skill generates publication-quality matplotlib/seaborn charts matching Tim's personal aesthetic (whitegrid, DejaVu Sans, cubehelix/ColorBrewer palettes, despined, annotation-rich).

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
    public/             # Curated public datasets (8 CSVs, ~300KB)

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

## Style Rules

All charts follow the aesthetic defined in `.claude/skills/matplotlib-chart/style-reference.md`:

- `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")` -- identical in every pattern
- `sns.despine(left=True, bottom=True)` -- all spines removed
- Legends: `frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey"`
- Annotations: `color="dimgrey"`
- Publication output: 300 DPI, PDF+PNG dual save
- Exploratory output: 150 DPI, PNG-only
- Verification renders during development: 150 DPI

## Verification

```bash
# Primary: Claude Code generates charts from minimal prompts (Docker required)
scripts/chart-test-container.sh
scripts/chart-test-container.sh --quick            # 3 prompts instead of 5
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

# All patterns should use dpi=300
grep 'dpi=' .claude/skills/matplotlib-chart/chart-patterns.md
```

## Autonomous Iteration

Use `/iterate-skill` to run a single evaluation-improvement-documentation cycle. The command:

1. Evaluates current skill state (static analysis + latest clean-room results)
2. Identifies 1-2 improvements
3. Applies changes, verifies via `scripts/chart-test-container.sh --quick` (Docker clean room)
4. Creates a gallery entry from clean-room results and atomic commit

Guardrails: max 3 iterations without human feedback, no pattern deletions, style invariants (`sns.set_theme` and `sns.despine`) are immutable.

## Plan Verification — MANDATORY

**When implementing a plan that includes a "Verification" section, you MUST execute every verification step before considering the work complete.** This is non-negotiable. Do not skip verification because the code "looks right" or because you "just wrote it." Run the commands, check the output, and confirm each expected result. If a verification step fails, fix the issue and re-verify. Unverified work is unfinished work.

## Future Work

Deferred patterns not yet in `chart-patterns.md`:
- Scatter plot (standalone, not decision-boundary)
- Grouped bar chart
- `fill_between` area chart
