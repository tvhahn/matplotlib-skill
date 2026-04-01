# Contributing

Thanks for your interest in improving the matplotlib skill.

## Quick Start

```bash
git clone https://github.com/tvhahn/matplotlib-skill.git
cd matplotlib-skill
uv sync
```

Skill files live in `.claude/skills/matplotlib/`:
- `SKILL.md` -- persona, workflow, code generation rules
- `style-reference.md` -- full style spec (palettes, sizing, conventions)
- `patterns/P1-horizontal-bar.md` through `patterns/P9-pr-roc.md` -- one file per chart type

## Modifying a Pattern

1. Edit the pattern file in `.claude/skills/matplotlib/patterns/`
2. Run a clean-room test: `scripts/chart-test-container.sh --quick`
3. Create a gallery entry in `docs/gallery/NN-name/` following `docs/gallery/TEMPLATE.md`
4. Include before/after PNGs in your PR

## Adding a New Pattern

1. Create `patterns/P{N}-{name}.md` following the structure of existing patterns
2. Add it to the pattern index table in `SKILL.md`
3. Add test prompts to `scripts/chart-test-container.sh`
4. Run a full test: `scripts/chart-test-container.sh`

## Style Invariants

These are immutable and must not change:

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")
sns.despine(left=True, bottom=True)
```

If you believe these should change, open an issue to discuss first.

## Testing

```bash
# Docker clean room (primary verification)
scripts/chart-test-container.sh --quick            # 5 prompts, random from pools
scripts/chart-test-container.sh                    # all 9 prompts, random from pools
scripts/chart-test-container.sh --fixed            # all 9 prompts, original defaults

# Static analysis (fast, no Docker)
uv run scripts/evaluate_skill.py --check-renders
```

## Pull Requests

- One logical change per PR
- Include before/after PNGs for any visual change
- Run `scripts/chart-test-container.sh --quick` before submitting
- Keep commit messages concise and descriptive

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
