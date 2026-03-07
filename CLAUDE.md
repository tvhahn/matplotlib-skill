# matplotlib-chart-skill

## Project

This repo holds the source of truth for Tim's `matplotlib-chart` Claude Code skill, plus a gallery documenting its evolution for a blog article.

## Conventions

- Skill files live in `skills/matplotlib-chart/` and are symlinked into `~/dotfiles/claude/skills/matplotlib-chart/`
- Gallery entries follow the template in `docs/gallery/TEMPLATE.md`
- Test charts are generated via `uv run scratch/test_chart_patterns.py`
- Output PNGs go to `scratch/figures/`

## Style rules

All charts follow the aesthetic defined in `skills/matplotlib-chart/style-reference.md`. Key rules:
- `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")`
- All spines removed via `sns.despine(left=True, bottom=True)`
- Legends: `frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey"`
- Annotations: `color="dimgrey"`
- Publication: 300 DPI PDF+PNG; Exploratory: 150 DPI PNG-only
- Verification renders during development use 150 DPI
