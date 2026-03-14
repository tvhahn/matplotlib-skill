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

### public/mpg.csv

- **Source:** seaborn built-in dataset (UCI Auto MPG)
- **License:** BSD
- **Domain:** Automotive
- **Rows:** 392
- **Description:** Auto fuel efficiency with engine specs and country of origin
- **Patterns:** P1 (horizontal bar), P2 (violin), P5 (lollipop), P6 (vertical bar), P7 (heatmap)

### public/flights.csv

- **Source:** seaborn built-in dataset (Box & Jenkins, 1970)
- **License:** BSD
- **Domain:** Aviation
- **Rows:** 144
- **Description:** Monthly airline passenger counts from 1949 to 1960
- **Patterns:** P3 (time series), P7 (heatmap — month x year), P8 (multi-panel)

### public/titanic.csv

- **Source:** seaborn built-in dataset (Titanic passenger records)
- **License:** BSD
- **Domain:** Historical
- **Rows:** 891
- **Description:** Titanic passenger survival data with class, age, fare, and demographics
- **Patterns:** P1 (horizontal bar), P2 (violin), P4 (PR/ROC), P6 (vertical bar)

### public/geyser.csv

- **Source:** seaborn built-in dataset (Old Faithful)
- **License:** BSD
- **Domain:** Geology
- **Rows:** 272
- **Description:** Old Faithful geyser eruption durations and waiting times
- **Patterns:** P2 (violin), P4 (PR/ROC), P9 (decision boundary)

### public/diamonds.csv

- **Source:** seaborn built-in dataset (ggplot2 diamonds, subsetted to ~2,000 rows)
- **License:** BSD
- **Domain:** Gemology
- **Rows:** ~2,000
- **Description:** Diamond prices with cut, color, clarity, and physical measurements
- **Patterns:** P1 (horizontal bar), P2 (violin), P5 (lollipop), P6 (vertical bar), P7 (heatmap)

### public/dowjones.csv

- **Source:** seaborn built-in dataset
- **License:** BSD
- **Domain:** Finance
- **Rows:** 649
- **Description:** Dow Jones Industrial Average closing prices
- **Patterns:** P3 (time series)

### public/glue.csv

- **Source:** seaborn built-in dataset (GLUE benchmark)
- **License:** BSD
- **Domain:** ML/NLP
- **Rows:** 64
- **Description:** GLUE benchmark scores for NLP models across tasks
- **Patterns:** P1 (horizontal bar), P5 (lollipop)

### public/fmri.csv

- **Source:** seaborn built-in dataset
- **License:** BSD
- **Domain:** Neuroscience
- **Rows:** 1,064
- **Description:** fMRI brain signal measurements by region and event type
- **Patterns:** P3 (time series), P8 (multi-panel)

### public/planets.csv

- **Source:** seaborn built-in dataset (NASA Exoplanet Archive)
- **License:** BSD
- **Domain:** Astronomy
- **Rows:** 1,035
- **Description:** Confirmed exoplanet discoveries by method, year, and orbital parameters
- **Patterns:** P1 (horizontal bar), P3 (time series)

### public/taxis.csv

- **Source:** seaborn built-in dataset (NYC TLC, subsetted to 1,000 rows)
- **License:** BSD
- **Domain:** Urban transport
- **Rows:** 1,000
- **Description:** NYC taxi ride fares, distances, tips, and pickup/dropoff details
- **Patterns:** P1 (horizontal bar), P2 (violin), P6 (vertical bar), P7 (heatmap)

### public/wine.csv

- **Source:** UCI ML Repository (Wine dataset) via scikit-learn
- **License:** CC-BY 4.0
- **Domain:** Chemistry
- **Rows:** 178
- **Description:** Chemical analysis of wines from 3 Italian cultivars (13 features)
- **Patterns:** P7 (heatmap — correlation), P9 (decision boundary)

### public/diabetes.csv

- **Source:** scikit-learn (Efron et al., 2004)
- **License:** CC-BY 4.0
- **Domain:** Medical
- **Rows:** 442
- **Description:** Diabetes disease progression with 10 clinical measurements
- **Patterns:** P7 (heatmap — correlation)

### public/seattle_weather.csv

- **Source:** Vega Datasets (NOAA)
- **License:** BSD-3
- **Domain:** Climate
- **Rows:** 1,461
- **Description:** Seattle daily weather: precipitation, temperature, wind, conditions (2012-2015)
- **Patterns:** P2 (violin), P3 (time series)

### public/stocks.csv

- **Source:** Vega Datasets (Yahoo Finance)
- **License:** BSD-3
- **Domain:** Finance
- **Rows:** ~560
- **Description:** Monthly stock prices for 5 tech companies (AAPL, AMZN, GOOG, IBM, MSFT)
- **Patterns:** P3 (time series), P8 (multi-panel)

### public/disasters.csv

- **Source:** Vega Datasets (Our World in Data)
- **License:** BSD-3
- **Domain:** Humanitarian
- **Rows:** ~800
- **Description:** Global disaster deaths by type (drought, earthquake, flood, etc.) and year
- **Patterns:** P1 (horizontal bar), P6 (vertical bar)

### public/co2_concentration.csv

- **Source:** Vega Datasets (Scripps CO2 Program)
- **License:** BSD-3
- **Domain:** Climate
- **Rows:** ~740
- **Description:** Atmospheric CO2 concentration at Mauna Loa (monthly measurements)
- **Patterns:** P3 (time series)

### public/mtcars.csv

- **Source:** R datasets (Motor Trend, 1974)
- **License:** Public domain
- **Domain:** Automotive
- **Rows:** 32
- **Description:** Motor Trend 1974 car road test data (mpg, cylinders, displacement, hp, weight, etc.)
- **Patterns:** P1 (horizontal bar), P7 (heatmap — correlation)

### public/chickweight.csv

- **Source:** R datasets (Crowder & Hand, 1990)
- **License:** Public domain
- **Domain:** Nutrition
- **Rows:** 578
- **Description:** Chick body weight growth over 21 days across 4 protein diets
- **Patterns:** P2 (violin), P3 (time series), P8 (multi-panel)

### public/world_happiness.csv

- **Source:** World Happiness Report (via PhilippeCodes/World-Happiness-Report-Data-Analysis)
- **License:** Public domain
- **Domain:** Economics
- **Rows:** ~153
- **Description:** Country happiness scores with GDP, family, health, freedom, generosity, corruption factors
- **Patterns:** P1 (horizontal bar), P5 (lollipop), P7 (heatmap), P8 (multi-panel)

### public/country_stats.csv

- **Source:** Gapminder 2007 via Plotly datasets
- **License:** CC0
- **Domain:** Geography
- **Rows:** ~142
- **Description:** Single-year (2007) country-level life expectancy, population, and GDP per capita
- **Patterns:** P1 (horizontal bar), P5 (lollipop), P7 (heatmap)

## Pre-computed Datasets

Generated by `scripts/generate_precomputed.py` from source/public datasets above. These contain pre-aggregated or pre-modeled data so chart patterns focus on visualization only — no sklearn imports, no groupby/rolling/corr computation.

### precomputed/p3/ — Time Series (CSV: year, value, rolling)

Derived from P3 source datasets via annual groupby + 10-year rolling mean.
Files: `global_temp.csv`, `flights.csv`, `birth_percentage.csv`, `dowjones.csv`, `co2_concentration.csv`, `stocks.csv`, `planets.csv`

### precomputed/p5/ — Lollipop (CSV: name, min, max, avg)

Derived from P5 source datasets via groupby + min/mean/max aggregation, sorted by avg.
Files: `healthexp.csv`, `mpg.csv`, `diamonds.csv`, `best_results.csv`, `world_happiness.csv`, `country_stats.csv`, `glue.csv`

### precomputed/p6/ — Decision Boundary (NPZ: mesh_x0, mesh_x1, yy_hat, yy_prob, X, y, class_names)

Derived from P6 source datasets via KNeighborsClassifier(k=15) fit + mesh grid predictions.
Files: `iris.npz`, `wine.npz`, `breast_cancer.npz`, `geyser.npz`, `penguins.npz`

### precomputed/p7/ — Heatmap (CSV: correlation matrix or pivot table)

Derived from P7 source datasets via `.corr()` on numeric columns or `.pivot_table()`.
Files: `penguins.csv`, `mpg.csv`, `diamonds.csv`, `wine.csv`, `birth_percentage.csv`, `tips.csv`, `flights.csv`, `diabetes.csv`, `mtcars.csv`, `taxis.csv`

### precomputed/p9/ — PR/ROC Curves (NPZ: precision/recall/tpr/fpr arrays + averages + baseline)

Derived from P9 source datasets via 5-fold StratifiedKFold with LogisticRegression.
Files: `breast_cancer.npz`, `penguins.npz`, `titanic.npz`, `geyser.npz`, `wine.npz`
