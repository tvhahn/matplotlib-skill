# matplotlib -- Claude Code Skill

Publication-quality matplotlib/seaborn charts from a one-line prompt. Colorblind-accessible, despined, annotation-rich figures using DejaVu Sans, cubehelix/ColorBrewer palettes, and whitegrid styling. Opinionated.

<table>
<tr>
<td><img src="docs/gallery/comparisons/p1-skill_1.png" width="100%" /></td>
<td><img src="docs/gallery/01-final-improvement/dowjones.png" width="100%" /></td>
<td><img src="docs/gallery/01-final-improvement/P9-pr-roc.png" width="100%" /></td>
</tr>
</table>

## Usage

```
> make a chart of collision rates by state using the matplotlib skill
```

The skill picks the chart type, applies opinionated templates and palettes, and saves PDF+PNG to `./figures/`.

## Before vs. After

Same data. Same prompt. The skill applies despined axes, cubehelix palettes, value labels, and insight annotations.

<table>
<tr>
<th width="50%">Claude defaults</th>
<th width="50%">With skill</th>
</tr>
<tr>
<td><img src="docs/gallery/comparisons/p1-no-skill_1.png" width="100%" /></td>
<td><img src="docs/gallery/comparisons/p1-skill_1.png" width="100%" /></td>
</tr>
</table>

<details>
<summary>More comparisons</summary>

<table>
<tr>
<th width="50%">Claude defaults</th>
<th width="50%">With skill</th>
</tr>
<tr>
<td><img src="docs/gallery/comparisons/p3-no-skill_1.png" width="100%" /></td>
<td><img src="docs/gallery/comparisons/p3-skill_1.png" width="100%" /></td>
</tr>
<tr>
<td><img src="docs/gallery/comparisons/p4-no-skill_1.png" width="100%" /></td>
<td><img src="docs/gallery/comparisons/p4-skill_1.png" width="100%" /></td>
</tr>
</table>

</details>

## Install

### Clone (auto-discovered by Claude Code)

```bash
git clone https://github.com/tvhahn/matplotlib-skill.git
cd matplotlib-skill
# Claude Code auto-discovers skills/matplotlib/SKILL.md when working in this repo
```

### Global install (available in all projects)

```bash
ln -s /path/to/matplotlib-skill/skills/matplotlib ~/.claude/skills/matplotlib
```

### Per-session (no symlink needed)

```bash
claude --add-dir /path/to/matplotlib-skill
```

### Plugin install

```bash
/plugin marketplace add tvhahn/matplotlib-skill
/plugin install matplotlib
```

## 9 Chart Patterns

<table>
<tr>
<td align="center"><img src="docs/gallery/comparisons/p1-skill_1.png" width="100%" /><br/><b>P1</b> Horizontal Bar</td>
<td align="center"><img src="docs/gallery/01-final-improvement/P2-vertical-bar.png" width="100%" /><br/><b>P2</b> Vertical Bar</td>
<td align="center"><img src="docs/gallery/comparisons/p3-skill_1.png" width="100%" /><br/><b>P3</b> Time Series</td>
</tr>
<tr>
<td align="center"><img src="docs/gallery/01-final-improvement/skill-p4.png" width="100%" /><br/><b>P4</b> Violin + Strip</td>
<td align="center"><img src="docs/gallery/01-final-improvement/P5-lollipop.png" width="100%" /><br/><b>P5</b> Lollipop</td>
<td align="center"><img src="docs/gallery/01-final-improvement/P6-decision-boundary.png" width="100%" /><br/><b>P6</b> Decision Boundary</td>
</tr>
<tr>
<td align="center"><img src="docs/gallery/01-final-improvement/P7-heatmap.png" width="100%" /><br/><b>P7</b> Heatmap</td>
<td align="center"><img src="docs/gallery/01-final-improvement/P8-multi-panel.png" width="100%" /><br/><b>P8</b> Multi-Panel</td>
<td align="center"><img src="docs/gallery/01-final-improvement/P9-pr-roc.png" width="100%" /><br/><b>P9</b> PR/ROC</td>
</tr>
</table>

| Pattern | When to use |
|---------|-------------|
| P1 Horizontal Bar | Ranked percentages, category comparisons |
| P2 Vertical Bar | Comparisons across categories, ranked values |
| P3 Time Series | Time series with rolling average |
| P4 Violin + Strip | Distribution comparisons |
| P5 Lollipop | Min/max/avg ranges, model comparison |
| P6 Decision Boundary | Classification boundaries, probability maps |
| P7 Heatmap | Correlation matrices, spectrograms |
| P8 Multi-Panel | Multi-panel grid layouts (2x2, 3x2, 3x3) |
| P9 PR/ROC | PR/ROC classification evaluation curves |
| Other charts | Line, scatter, histogram, grouped bar (`patterns/other-charts.md`) |

## Design Philosophy

> *Above all else, show the data. Annotate the insight, not just the axis. When in doubt, remove.*

<details>
<summary>Full principles</summary>

1. Above all else, show the data
2. Every element earns its ink
3. Prefer position over color, color over size
4. Grey is a color. White space is a feature.
5. Despine, degrid, then add back only what the reader needs
6. Annotate the insight, not just the axis
7. Encode meaning twice -- never rely on color alone
8. Consistency across panels; variety across charts
9. The reader should never do arithmetic
10. When in doubt, remove

</details>

## How This Skill Was Built

Built through 50 iterations of automated evaluation -- an AI refining its own visual taste. [Read the story on my blog &rarr;](https://www.tvhahn.com/posts/building-a-claude-code-skill/)

## Datasets

Ships with 39 datasets for testing and demos:
- **10 source project datasets** from Tim's research (bearing RUL predictions, arxiv paper labels, classifier comparisons, tool wear)
- **29 public reference datasets** (penguins, gapminder, tips, iris, titanic, and more)

See [`data/datasets.yaml`](data/datasets.yaml) for the full manifest with attribution, licenses, and pattern mappings.

## Verification

Every chart the skill makes is linted by `skills/matplotlib/scripts/check_figure.py`, which runs the script and measures text collisions, legends covering data, labels spilling into other panels, and style drift — things that are easy to miss in a downsized PNG.

```bash
# Multi-model benchmark in isolated clean rooms (no Docker; needs the claude CLI)
uv run scripts/benchmark.py --label mytest --models claude-sonnet-5-5,claude-opus-5-5,claude-haiku-4-5

# Every pattern template runs on real data and passes the checker
uv run --no-project --with pytest --with matplotlib --with seaborn --with pandas --with numpy \
    pytest tests/test_patterns.py -q

# Generate charts in a Docker clean room (Docker required)
scripts/chart-test-container.sh --quick            # 5 prompts, random from pools
scripts/chart-test-container.sh                    # all 9 prompts, random from pools
scripts/chart-test-container.sh --fixed            # all 9 prompts, original defaults

# Static analysis (fast, no Docker)
uv run scripts/evaluate_skill.py --check-renders
```

## Contributing

Contributions are welcome — whether it's improving an existing pattern or adding an entirely new chart type. Some ideas to get started:

- **Improve a pattern:** Refine annotations, spacing, or palette choices in any of the 9 existing patterns
- **Add a new chart type:** Line, scatter, histogram, and grouped bar have short templates in `other-charts.md`; stacked bars, `fill_between` area charts, and slope charts are on the wishlist
- **Add datasets:** New public datasets that pair well with existing or new patterns

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on modifying patterns, adding new ones, and running tests.

## License

[MIT](LICENSE)
