# matplotlib-chart-skill

## Project Purpose

This repo is the **source of truth** for Tim's `matplotlib-chart` Claude Code skill AND a gallery documenting its evolution for a blog article about iteratively building a Claude Code skill.

The skill generates publication-quality matplotlib/seaborn charts matching Tim's personal aesthetic (whitegrid, DejaVu Sans, cubehelix/ColorBrewer palettes, despined, annotation-rich).

### Key files

```
skills/matplotlib-chart/
  SKILL.md              # Persona, 5-phase workflow, code generation rules
  style-reference.md    # Full style spec (palettes, sizing, save conventions)
  chart-patterns.md     # 9 self-contained code patterns by chart type

docs/gallery/           # Before/after captures at each iteration
  TEMPLATE.md           # Template for new gallery entries
  00-original/          # ... through 04-verification-checklist/

scratch/
  test_chart_patterns.py  # Standalone test harness -- exercises chart-patterns.md code with dummy data (pattern 6 skipped)
  figures/                # Working output directory (gitignored PNGs)
```

## Symlink Setup

Claude Code discovers the skill through a **two-hop symlink chain**:

```
~/.claude/skills/matplotlib-chart
  -> ~/dotfiles/claude/skills/matplotlib-chart/
    -> ~/Documents/matplotlib-chart-skill/skills/matplotlib-chart  (this repo)
```

Edits to skill files in this repo propagate instantly to `~/.claude/skills/` -- no copy or sync step needed. Do not create or modify skill files directly in dotfiles or `~/.claude/skills/`.

This repo has no `.claude/` directory because the skill is loaded globally via the chain above. The repo-level `CLAUDE.md` provides project instructions only when working inside this repo.

## Gallery Workflow

Each `docs/gallery/NN-name/` folder captures the skill's output at a specific iteration point. To create a new gallery entry:

1. Make skill changes in `skills/matplotlib-chart/`
2. Update `scratch/test_chart_patterns.py` if chart patterns changed
3. Run `uv run scratch/test_chart_patterns.py` to regenerate test charts (this runs the code patterns directly with dummy data -- it does not invoke the skill's LLM workflow)
4. Create `docs/gallery/NN-name/` folder (next sequential number)
5. Copy relevant PNGs from `scratch/figures/` into the gallery folder
6. Write `README.md` following `docs/gallery/TEMPLATE.md`
7. Commit

## Existing Gallery Entries

| Entry | Description |
|---|---|
| `00-original` | Baseline from the original commit -- captures all quirks before improvements |
| `01-current` | API modernization (`sns.set()` -> `sns.set_theme()`, pandas iloc fixes) + visual polish (dimgrey annotations, framed legends, `sns.despine()`) |
| `02-dpi-optimization` | Added verification render at 150 DPI during iterative development; final output stays 300 DPI |
| `03-consistency-audit` | Fixed 5 patterns with inconsistent `sns.set_theme()` calls or wrong `dpi=` values |
| `04-verification-checklist` | Rewrote Phase 5 verification from vague prose to a 7-item numbered checklist |

## Style Rules

All charts follow the aesthetic defined in `skills/matplotlib-chart/style-reference.md`:

- `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")` -- identical in every pattern
- `sns.despine(left=True, bottom=True)` -- all spines removed
- Legends: `frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey"`
- Annotations: `color="dimgrey"`
- Publication output: 300 DPI, PDF+PNG dual save
- Exploratory output: 150 DPI, PNG-only
- Verification renders during development: 150 DPI

## Verification

Quick consistency checks:

```bash
# All sns.set_theme calls should be identical
grep 'sns.set_theme' skills/matplotlib-chart/chart-patterns.md

# All patterns should use dpi=300
grep 'dpi=' skills/matplotlib-chart/chart-patterns.md
```

## Future Work

Deferred patterns not yet in `chart-patterns.md`:
- Scatter plot (standalone, not decision-boundary)
- Grouped bar chart
- `fill_between` area chart
