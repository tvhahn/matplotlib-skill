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
  00-original-inspiration/ # Source material from 4 inspiring projects
  01-original/             # Baseline from original commit
  02-current/              # After API modernization + visual polish
  03-dpi-optimization/     # Verification DPI fix
  04-consistency-audit/    # Pattern consistency fixes
  05-verification-checklist/ # Phase 5 checklist rewrite
  06-subplot-outlines/     # Subplot borders + RUL test data

scratch/                   # Test scripts and working output
  test_chart_patterns.py   # Generates all 8 testable patterns
  figures/                 # Working output directory
```

## Skill Installation

The skill lives in `.claude/skills/matplotlib-chart/`, where Claude Code discovers it automatically in any clone or devcontainer. On the host, a symlink from `~/dotfiles/claude/skills/matplotlib-chart/` keeps it globally available.

## Datasets

The skill ships with 19 datasets (10 from Tim's projects, 9 public references) in `data/raw/`. See [`data/SOURCES.md`](data/SOURCES.md) for full attribution and pattern mappings.

**Source Project Datasets**

| Project | License | Description |
|---|---|---|
| [weibull-knowledge-informed-ml](https://github.com/tvhhn/weibull-knowledge-informed-ml) | MIT | Bearing RUL predictions, Weibull loss functions, spectrograms (8 CSVs + 38 HDF5) |
| [arxiv-code-search](https://github.com/tvhhn/arxiv-code-search) | MIT | Paper labels with code-availability flags (4,665 rows) |
| [Beautiful-Plots](https://github.com/tvhhn/Beautiful-Plots) | MIT | Classifier AUC comparisons, US birth patterns (2 CSVs) |
| [ml-tool-wear](https://github.com/tvhhn/ml-tool-wear) | MIT | Tool wear cases with class labels (167 rows) |

**Public Reference Datasets**

| Dataset | License | Source | Description |
|---|---|---|---|
| penguins.csv | CC-0 | [Palmer Penguins](https://github.com/allisonhorst/palmerpenguins) | Body measurements of 3 penguin species (344 rows) |
| gapminder.csv | CC-BY 4.0 | [Gapminder](https://www.gapminder.org/data/) | Life expectancy, GDP, population by country/year (3,313 rows) |
| tips.csv | BSD | [seaborn-data](https://github.com/mwaskom/seaborn-data) | Restaurant tips with meal context (244 rows) |
| global_temp.csv | Public domain | [NASA GISTEMP](https://data.giss.nasa.gov/gistemp/) | Monthly surface temperature anomalies (1,753 rows) |
| car_crashes.csv | CC-BY 4.0 | [FiveThirtyEight](https://github.com/fivethirtyeight/data/tree/master/bad-drivers) | US state bad driver statistics (51 rows) |
| breast_cancer.csv | CC-BY 4.0 | [UCI ML Repository](https://archive.ics.uci.edu/dataset/17) | Breast mass FNA diagnostic features (569 rows) |
| healthexp.csv | CC-BY | [OECD](https://data.oecd.org/healthres/health-spending.htm) | Health expenditure per capita by country/year (274 rows) |
| iowa_electricity.csv | Public domain | [US EIA](https://www.eia.gov/) | Iowa electricity generation by source (51 rows) |
| iris.csv | CC-BY 4.0 | [UCI ML Repository](https://archive.ics.uci.edu/dataset/53) | Fisher's iris flower measurements (150 rows) |

## Gallery

Each `docs/gallery/NN-name/` folder captures the skill's output at a specific iteration point, following the template in `docs/gallery/TEMPLATE.md`. This serves as material for a blog article about iteratively building a Claude Code skill.
