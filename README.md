# matplotlib-chart Skill

A Claude Code skill that generates publication-quality matplotlib/seaborn charts matching Tim's personal aesthetic.

## Structure

```
.claude/skills/matplotlib-chart/  # Source of truth for skill files
  SKILL.md                 # Persona, workflow, code generation rules
  style-reference.md       # Full style spec (palettes, sizing, conventions)
  chart-patterns.md        # 9 code patterns by chart type

docs/gallery/              # Before/after captures at each iteration
  TEMPLATE.md              # Blog capture template
  00-original/             # Baseline from original commit
  01-current/              # After API modernization + visual polish
  02-dpi-optimization/     # Verification DPI fix
  03-consistency-audit/    # Pattern consistency fixes
  04-verification-checklist/ # Phase 5 checklist rewrite

scratch/                   # Test scripts and working output
  test_chart_patterns.py   # Generates all 8 testable patterns
  figures/                 # Working output directory
```

## Skill Installation

The skill lives in `.claude/skills/matplotlib-chart/`, where Claude Code discovers it automatically in any clone or devcontainer. On the host, a symlink from `~/dotfiles/claude/skills/matplotlib-chart/` keeps it globally available.

## Gallery

Each `docs/gallery/NN-name/` folder captures the skill's output at a specific iteration point, following the template in `docs/gallery/TEMPLATE.md`. This serves as material for a blog article about iteratively building a Claude Code skill.
