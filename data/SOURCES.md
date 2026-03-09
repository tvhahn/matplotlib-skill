# Dataset Sources & Attribution

All datasets in `data/raw/` with their provenance, licensing, and usage notes.

## Source Project Datasets

These datasets come from the 4 research projects that inspired the skill's chart patterns (see `docs/gallery/00-original-inspiration/`).

### arxiv/labels.csv

- **Source:** [arxiv-code-search](https://github.com/tvhahn/arxiv-code-search) (Tim's research tool)
- **License:** Author (Tim)
- **Rows:** 4,665
- **Description:** Paper labels with code availability flags for ML classification
- **Patterns:** P1 (horizontal bar — publisher percentages), P9 (PR/ROC — binary labels)

### beautiful-plots/best_results.csv

- **Source:** [Beautiful-Plots](https://github.com/tvhahn/Beautiful-Plots)
- **License:** Author (Tim)
- **Rows:** 6
- **Description:** Classifier AUC comparison results (min/avg/max per classifier)
- **Patterns:** P5 (lollipop/dumbbell)

### beautiful-plots/birth_percentage.csv

- **Source:** [Beautiful-Plots](https://github.com/tvhahn/Beautiful-Plots)
- **License:** Author (Tim)
- **Rows:** 468
- **Description:** Birth percentage above average by month and year
- **Patterns:** P3 (time series), P7 (heatmap — year x month grid)

### ml-tool-wear/labels_with_tool_class.csv

- **Source:** [ml-tool-wear](https://github.com/tvhahn/ml-tool-wear)
- **License:** Author (Tim)
- **Rows:** 167
- **Description:** Tool wear cases with class labels for anomaly detection
- **Patterns:** P2 (vertical bar — class distribution)

### weibull/*.csv

- **Source:** [weibull-knowledge-informed-ml](https://github.com/tvhahn/weibull-knowledge-informed-ml) (Tim's PhD research)
- **License:** Author (Tim)
- **Files & patterns:**
  - `femto_count_results.csv` (12 rows) — P1 (horizontal bar — loss function percentages)
  - `ims_count_results.csv` (9 rows) — P1 variant
  - `femto_correlation_results.csv` (15 rows) — P2 (vertical bar — correlation values)
  - `ims_correlation_results.csv` (15 rows) — P2 variant
  - `femto_early_stop_summary_stats.csv` (9 rows) — P4 (violin/strip — epoch distributions)
  - `ims_early_stop_summary_stats.csv` (9 rows) — P4 variant
  - `femto_results_filtered.csv` (582 rows) — P3 (time series — RUL), P8 (multi-panel)
  - `ims_results_filtered.csv` (775 rows) — P3/P8 variant

### weibull/processed/*.hdf5

- **Source:** Same as above
- **License:** Author (Tim)
- **Files:** 38 HDF5 files (~7.4 MB total)
- **Description:** Train/val/test splits for spectrogram data
- **Patterns:** P7 (heatmap/spectrogram)

## Public Reference Datasets

Curated small datasets with permissive licenses, downloaded via `data/fetch_datasets.py`.

### public/penguins.csv

- **Source:** [Palmer Penguins](https://github.com/allisonhorst/palmerpenguins) by Allison Horst, Alison Hill, Kristen Gorman
- **License:** CC-0 (public domain)
- **Domain:** Ecology
- **Rows:** 344
- **Description:** Body measurements of 3 penguin species from Palmer Station, Antarctica
- **Patterns:** P4 (violin/strip — body mass by species), P6 (scatter/decision boundary — bill dimensions), P9 (PR/ROC — species classification)

### public/gapminder.csv

- **Source:** [Gapminder](https://www.gapminder.org/) via Plotly datasets
- **License:** CC-BY 4.0
- **Domain:** Global development
- **Rows:** ~1,700
- **Description:** Life expectancy, population, and GDP per capita by country and year
- **Patterns:** P1 (horizontal bar — GDP by country), P8 (multi-panel — per-continent trends)

### public/tips.csv

- **Source:** [Seaborn](https://github.com/mwaskom/seaborn-data) (Bryant & Smith, 1995)
- **License:** BSD
- **Domain:** Social science
- **Rows:** 244
- **Description:** Restaurant tip amounts with meal context (day, time, party size)
- **Patterns:** P4 (violin/strip — tip by day), P7 (heatmap — correlation matrix)

### public/global_temp.csv

- **Source:** [NASA GISTEMP v4](https://data.giss.nasa.gov/gistemp/)
- **License:** PDDL (public domain)
- **Domain:** Climate science
- **Rows:** ~1,700
- **Description:** Global surface temperature anomalies (monthly, relative to 1951-1980 baseline)
- **Patterns:** P3 (time series — temperature trend), P7 (heatmap — year x month)

### public/car_crashes.csv

- **Source:** [FiveThirtyEight](https://github.com/fivethirtyeight/data/tree/master/bad-drivers) via seaborn
- **License:** CC-BY 4.0
- **Domain:** Transportation safety
- **Rows:** 51
- **Description:** US state-level bad driver statistics (collisions, speeding, alcohol, insurance)
- **Patterns:** P1 (horizontal bar — collision rates), P2 (vertical bar — causes)

### public/breast_cancer.csv

- **Source:** [UCI ML Repository](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic) (Wisconsin Diagnostic)
- **License:** CC BY 4.0
- **Domain:** Medical diagnostics
- **Rows:** 569
- **Description:** Cell nucleus features from digitized breast mass FNA images
- **Patterns:** P6 (scatter/decision boundary — feature pairs), P9 (PR/ROC — binary diagnosis)

### public/healthexp.csv

- **Source:** [OECD](https://data.oecd.org/healthres/health-spending.htm) via seaborn
- **License:** CC-BY
- **Domain:** Health economics
- **Rows:** ~231
- **Description:** Health expenditure per capita by country and year
- **Patterns:** P5 (lollipop — 1970 vs 2020 comparison), P8 (multi-panel — per-country trends)

### public/iowa_electricity.csv

- **Source:** [US EIA](https://www.eia.gov/) via vega-datasets
- **License:** Public domain (US government)
- **Domain:** Energy
- **Rows:** ~51
- **Description:** Iowa electricity generation by source type
- **Patterns:** P2 (vertical bar — generation by source)

### public/iris.csv

- **Source:** [UCI ML Repository](https://archive.ics.uci.edu/dataset/53/iris) (Fisher, 1936) via scikit-learn
- **License:** CC-BY 4.0
- **Domain:** Ecology
- **Rows:** 150
- **Description:** Sepal and petal measurements for 3 iris species
- **Patterns:** P6 (decision boundary — petal length vs petal width)
