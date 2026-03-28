# matplotlib Skill

A Claude Code skill that generates publication-quality matplotlib/seaborn charts matching Tim's personal aesthetic.

## Structure

```
.claude/skills/matplotlib/  # Source of truth for skill files
  SKILL.md                 # Persona, workflow, code generation rules
  style-reference.md       # Full style spec (palettes, sizing, conventions)
  patterns/                # 9 code patterns by chart type (one file per pattern)

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

The skill lives in `.claude/skills/matplotlib/`, where Claude Code discovers it automatically in any clone or devcontainer. On the host, a symlink from `~/dotfiles/claude/skills/matplotlib/` keeps it globally available.

## Datasets

The skill ships with 39 datasets (10 from Tim's projects, 29 public references) in `data/raw/`. See [`data/SOURCES.md`](data/SOURCES.md) for full attribution and pattern mappings.

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
| mpg.csv | BSD | [seaborn](https://github.com/mwaskom/seaborn-data) | Auto fuel efficiency with engine and origin (392 rows) |
| flights.csv | BSD | [seaborn](https://github.com/mwaskom/seaborn-data) | Monthly airline passengers 1949-1960 (144 rows) |
| titanic.csv | BSD | [seaborn](https://github.com/mwaskom/seaborn-data) | Titanic passenger survival data (891 rows) |
| geyser.csv | BSD | [seaborn](https://github.com/mwaskom/seaborn-data) | Old Faithful eruption durations and waits (272 rows) |
| diamonds.csv | BSD | [seaborn](https://github.com/mwaskom/seaborn-data) | Diamond prices and quality attributes (2,000 rows) |
| dowjones.csv | BSD | [seaborn](https://github.com/mwaskom/seaborn-data) | Dow Jones closing prices (649 rows) |
| glue.csv | BSD | [seaborn](https://github.com/mwaskom/seaborn-data) | GLUE benchmark NLP model scores (64 rows) |
| fmri.csv | BSD | [seaborn](https://github.com/mwaskom/seaborn-data) | fMRI brain signals by region and event (1,064 rows) |
| planets.csv | BSD | [seaborn](https://github.com/mwaskom/seaborn-data) | Exoplanet discoveries by method and year (1,035 rows) |
| taxis.csv | BSD | [seaborn](https://github.com/mwaskom/seaborn-data) | NYC taxi ride fares and trip details (1,000 rows) |
| wine.csv | CC-BY 4.0 | [UCI ML Repository](https://archive.ics.uci.edu/dataset/109) | Chemical analysis of wines from 3 cultivars (178 rows) |
| diabetes.csv | CC-BY 4.0 | [scikit-learn](https://scikit-learn.org/) | Diabetes progression clinical measurements (442 rows) |
| seattle_weather.csv | BSD-3 | [Vega Datasets](https://github.com/vega/vega-datasets) | Seattle daily weather observations (1,461 rows) |
| stocks.csv | BSD-3 | [Vega Datasets](https://github.com/vega/vega-datasets) | Stock prices for 5 tech companies (560 rows) |
| disasters.csv | BSD-3 | [Vega Datasets](https://github.com/vega/vega-datasets) | Global disaster deaths by type and year (803 rows) |
| co2_concentration.csv | BSD-3 | [Vega Datasets](https://github.com/vega/vega-datasets) | Atmospheric CO2 at Mauna Loa (741 rows) |
| mtcars.csv | Public domain | [R Datasets](https://vincentarelbundock.github.io/Rdatasets/) | Motor Trend 1974 car performance (32 rows) |
| chickweight.csv | Public domain | [R Datasets](https://vincentarelbundock.github.io/Rdatasets/) | Chick weight growth by diet (578 rows) |
| world_happiness.csv | Public domain | [World Happiness Report](https://worldhappiness.report/) | Country happiness scores with factors (153 rows) |
| country_stats.csv | CC0 | [Plotly datasets](https://github.com/plotly/datasets) | Gapminder 2007 country development snapshot (142 rows) |

## Gallery

Each `docs/gallery/NN-name/` folder captures the skill's output at a specific iteration point, following the template in `docs/gallery/TEMPLATE.md`. This serves as material for a blog article about iteratively building a Claude Code skill.
