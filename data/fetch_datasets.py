# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas>=2.1",
#     "seaborn>=0.13",
#     "scikit-learn>=1.3",
# ]
# ///
"""Download curated public reference datasets into data/raw/public/.

Run once to populate the public datasets directory. The resulting CSVs are
committed to the repo — this script serves as provenance documentation.

Usage:
    uv run data/fetch_datasets.py
"""

import io
import urllib.request
from pathlib import Path

import pandas as pd

PUBLIC_DIR = Path(__file__).parent / "raw" / "public"


def fetch_csv_from_url(url: str) -> pd.DataFrame:
    """Download a CSV from a URL and return as DataFrame."""
    print(f"  Fetching {url}")
    with urllib.request.urlopen(url) as response:
        return pd.read_csv(io.BytesIO(response.read()))


def fetch_penguins():
    """Palmer Penguins — 344 rows — CC-0 license."""
    url = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv"
    df = fetch_csv_from_url(url)
    df.to_csv(PUBLIC_DIR / "penguins.csv", index=False)
    print(f"  -> penguins.csv ({len(df)} rows)")


def fetch_gapminder():
    """Gapminder excerpt — ~1,704 rows — CC0 (public domain)."""
    # Use plotly's curated gapminder dataset
    url = "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
    df = fetch_csv_from_url(url)
    # Keep only the standard gapminder columns and a manageable subset
    expected_cols = ["country", "continent", "year", "lifeExp", "pop", "gdpPercap"]
    if all(c in df.columns for c in expected_cols):
        df = df[expected_cols]
    df.to_csv(PUBLIC_DIR / "gapminder.csv", index=False)
    print(f"  -> gapminder.csv ({len(df)} rows)")


def fetch_tips():
    """Restaurant tips — 244 rows — BSD license (seaborn bundled)."""
    import seaborn as sns

    df = sns.load_dataset("tips")
    df.to_csv(PUBLIC_DIR / "tips.csv", index=False)
    print(f"  -> tips.csv ({len(df)} rows)")


def fetch_global_temp():
    """GISTEMP global temperature anomalies — public domain."""
    # NASA GISTEMP v4 — global annual mean
    url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
    print(f"  Fetching {url}")
    with urllib.request.urlopen(url) as response:
        content = response.read().decode("utf-8")
    # Skip the header line that starts with "Land-Ocean..."
    lines = content.strip().split("\n")
    # Find the row with column headers (Year, Jan, Feb, ...)
    header_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("Year"):
            header_idx = i
            break
    clean = "\n".join(lines[header_idx:])
    df = pd.read_csv(io.StringIO(clean))
    # Reshape to long format: Year, Month, Anomaly
    month_cols = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    available_months = [m for m in month_cols if m in df.columns]
    df_long = df.melt(
        id_vars=["Year"],
        value_vars=available_months,
        var_name="Month",
        value_name="Anomaly",
    )
    # Drop rows where Anomaly is not a valid number
    df_long["Anomaly"] = pd.to_numeric(df_long["Anomaly"], errors="coerce")
    df_long = df_long.dropna(subset=["Anomaly"])
    df_long = df_long.sort_values(["Year", "Month"]).reset_index(drop=True)
    df_long.to_csv(PUBLIC_DIR / "global_temp.csv", index=False)
    print(f"  -> global_temp.csv ({len(df_long)} rows)")


def fetch_car_crashes():
    """US bad drivers — 51 rows — CC-BY 4.0 (FiveThirtyEight via seaborn)."""
    import seaborn as sns

    df = sns.load_dataset("car_crashes")
    df.to_csv(PUBLIC_DIR / "car_crashes.csv", index=False)
    print(f"  -> car_crashes.csv ({len(df)} rows)")


def fetch_breast_cancer():
    """UCI Wisconsin breast cancer — 569 rows — CC BY 4.0."""
    from sklearn.datasets import load_breast_cancer

    data = load_breast_cancer()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df["target"] = data.target
    df["target_name"] = [data.target_names[t] for t in data.target]
    df.to_csv(PUBLIC_DIR / "breast_cancer.csv", index=False)
    print(f"  -> breast_cancer.csv ({len(df)} rows)")


def fetch_healthexp():
    """Health expenditure by country — seaborn bundled — CC-BY."""
    import seaborn as sns

    df = sns.load_dataset("healthexp")
    df.to_csv(PUBLIC_DIR / "healthexp.csv", index=False)
    print(f"  -> healthexp.csv ({len(df)} rows)")


def fetch_iowa_electricity():
    """Iowa electricity generation — vega-datasets — public domain."""
    url = "https://raw.githubusercontent.com/vega/vega-datasets/main/data/iowa-electricity.csv"
    df = fetch_csv_from_url(url)
    df.to_csv(PUBLIC_DIR / "iowa_electricity.csv", index=False)
    print(f"  -> iowa_electricity.csv ({len(df)} rows)")


def fetch_iris():
    """Fisher's Iris — 150 rows — CC0 (public domain via scikit-learn)."""
    from sklearn.datasets import load_iris

    data = load_iris()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df["target"] = data.target
    df["target_name"] = [data.target_names[t] for t in data.target]
    df.to_csv(PUBLIC_DIR / "iris.csv", index=False)
    print(f"  -> iris.csv ({len(df)} rows)")


# --- New datasets (Step 1) ---


def fetch_mpg():
    """Auto MPG — ~392 rows — BSD (seaborn bundled)."""
    import seaborn as sns

    df = sns.load_dataset("mpg").dropna()
    df.to_csv(PUBLIC_DIR / "mpg.csv", index=False)
    print(f"  -> mpg.csv ({len(df)} rows)")


def fetch_flights():
    """Airline passengers — 144 rows — BSD (seaborn bundled)."""
    import seaborn as sns

    df = sns.load_dataset("flights")
    df.to_csv(PUBLIC_DIR / "flights.csv", index=False)
    print(f"  -> flights.csv ({len(df)} rows)")


def fetch_titanic():
    """Titanic passengers — 891 rows — BSD (seaborn bundled)."""
    import seaborn as sns

    df = sns.load_dataset("titanic")
    df.to_csv(PUBLIC_DIR / "titanic.csv", index=False)
    print(f"  -> titanic.csv ({len(df)} rows)")


def fetch_geyser():
    """Old Faithful geyser — 272 rows — BSD (seaborn bundled)."""
    import seaborn as sns

    df = sns.load_dataset("geyser")
    df.to_csv(PUBLIC_DIR / "geyser.csv", index=False)
    print(f"  -> geyser.csv ({len(df)} rows)")


def fetch_diamonds():
    """Diamonds — ~2,000 rows (subsetted) — BSD (seaborn bundled)."""
    import seaborn as sns

    df = sns.load_dataset("diamonds")
    df = df.groupby("cut", group_keys=False).apply(
        lambda x: x.sample(min(len(x), 400), random_state=42)
    )
    df.to_csv(PUBLIC_DIR / "diamonds.csv", index=False)
    print(f"  -> diamonds.csv ({len(df)} rows)")


def fetch_dowjones():
    """Dow Jones index — 649 rows — BSD (seaborn bundled)."""
    import seaborn as sns

    df = sns.load_dataset("dowjones")
    df.to_csv(PUBLIC_DIR / "dowjones.csv", index=False)
    print(f"  -> dowjones.csv ({len(df)} rows)")


def fetch_glue():
    """GLUE benchmark scores — 64 rows — BSD (seaborn bundled)."""
    import seaborn as sns

    df = sns.load_dataset("glue")
    df.to_csv(PUBLIC_DIR / "glue.csv", index=False)
    print(f"  -> glue.csv ({len(df)} rows)")


def fetch_fmri():
    """fMRI brain signals — 1,064 rows — BSD (seaborn bundled)."""
    import seaborn as sns

    df = sns.load_dataset("fmri")
    df.to_csv(PUBLIC_DIR / "fmri.csv", index=False)
    print(f"  -> fmri.csv ({len(df)} rows)")


def fetch_planets():
    """Exoplanets — 1,035 rows — BSD (seaborn bundled)."""
    import seaborn as sns

    df = sns.load_dataset("planets")
    df.to_csv(PUBLIC_DIR / "planets.csv", index=False)
    print(f"  -> planets.csv ({len(df)} rows)")


def fetch_taxis():
    """NYC taxi rides — ~1,000 rows (subsetted) — BSD (seaborn bundled)."""
    import seaborn as sns

    df = sns.load_dataset("taxis").dropna().sample(1000, random_state=42)
    df.to_csv(PUBLIC_DIR / "taxis.csv", index=False)
    print(f"  -> taxis.csv ({len(df)} rows)")


def fetch_wine():
    """UCI Wine — 178 rows — CC-BY-4.0 (scikit-learn)."""
    from sklearn.datasets import load_wine

    data = load_wine()
    df = pd.DataFrame(data.data, columns=data.feature_names)
    df["target"] = data.target
    df["target_name"] = [data.target_names[t] for t in data.target]
    df.to_csv(PUBLIC_DIR / "wine.csv", index=False)
    print(f"  -> wine.csv ({len(df)} rows)")


def fetch_diabetes():
    """Diabetes progression — 442 rows — CC-BY-4.0 (scikit-learn)."""
    from sklearn.datasets import load_diabetes

    df = load_diabetes(as_frame=True).frame
    df.to_csv(PUBLIC_DIR / "diabetes.csv", index=False)
    print(f"  -> diabetes.csv ({len(df)} rows)")


def fetch_seattle_weather():
    """Seattle daily weather — 1,461 rows — BSD-3 (Vega Datasets)."""
    url = "https://cdn.jsdelivr.net/npm/vega-datasets@2/data/seattle-weather.csv"
    df = fetch_csv_from_url(url)
    df.to_csv(PUBLIC_DIR / "seattle_weather.csv", index=False)
    print(f"  -> seattle_weather.csv ({len(df)} rows)")


def fetch_stocks():
    """Stock prices — ~560 rows — BSD-3 (Vega Datasets)."""
    url = "https://cdn.jsdelivr.net/npm/vega-datasets@2/data/stocks.csv"
    df = fetch_csv_from_url(url)
    df.to_csv(PUBLIC_DIR / "stocks.csv", index=False)
    print(f"  -> stocks.csv ({len(df)} rows)")


def fetch_disasters():
    """Global disaster deaths — 682 rows — BSD-3 (Vega Datasets)."""
    url = "https://cdn.jsdelivr.net/npm/vega-datasets@2/data/disasters.csv"
    df = fetch_csv_from_url(url)
    df.to_csv(PUBLIC_DIR / "disasters.csv", index=False)
    print(f"  -> disasters.csv ({len(df)} rows)")


def fetch_co2_concentration():
    """Atmospheric CO2 — ~750 rows — BSD-3 (Vega Datasets)."""
    url = "https://cdn.jsdelivr.net/npm/vega-datasets@2/data/co2-concentration.csv"
    df = fetch_csv_from_url(url)
    df.to_csv(PUBLIC_DIR / "co2_concentration.csv", index=False)
    print(f"  -> co2_concentration.csv ({len(df)} rows)")


def fetch_mtcars():
    """Motor Trend cars — 32 rows — Public domain (R datasets)."""
    url = "https://vincentarelbundock.github.io/Rdatasets/csv/datasets/mtcars.csv"
    df = fetch_csv_from_url(url)
    # Drop the R row-index column, keep car name
    if df.columns[0] == "" or df.columns[0] == "rownames":
        df = df.rename(columns={df.columns[0]: "car"})
    elif "Unnamed: 0" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "car"})
    df.to_csv(PUBLIC_DIR / "mtcars.csv", index=False)
    print(f"  -> mtcars.csv ({len(df)} rows)")


def fetch_chickweight():
    """Chick weight growth — 578 rows — Public domain (R datasets)."""
    url = "https://vincentarelbundock.github.io/Rdatasets/csv/datasets/ChickWeight.csv"
    df = fetch_csv_from_url(url)
    # Drop R row index, lowercase column names
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    elif df.columns[0] == "" or df.columns[0] == "rownames":
        df = df.drop(columns=[df.columns[0]])
    df.columns = [c.lower() for c in df.columns]
    df.to_csv(PUBLIC_DIR / "chickweight.csv", index=False)
    print(f"  -> chickweight.csv ({len(df)} rows)")


def fetch_world_happiness():
    """World Happiness Report — ~155 rows — Public domain."""
    url = "https://raw.githubusercontent.com/PhilippeCodes/World-Happiness-Report-Data-Analysis/master/World%20Happiness%20Report.csv"
    df = fetch_csv_from_url(url)
    # Keep key columns, clean names
    keep = ["Country", "Happiness Score", "Economy", "Family", "Health",
            "Freedom", "Generosity", "Corruption", "Region"]
    df = df[[c for c in keep if c in df.columns]]
    df.to_csv(PUBLIC_DIR / "world_happiness.csv", index=False)
    print(f"  -> world_happiness.csv ({len(df)} rows)")


def fetch_country_stats():
    """Gapminder 2007 cross-section — ~142 rows — CC0 (Plotly datasets)."""
    url = "https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv"
    df = fetch_csv_from_url(url)
    df.to_csv(PUBLIC_DIR / "country_stats.csv", index=False)
    print(f"  -> country_stats.csv ({len(df)} rows)")


def main():
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading public reference datasets to {PUBLIC_DIR}/\n")

    fetchers = [
        ("Palmer Penguins", fetch_penguins),
        ("Gapminder", fetch_gapminder),
        ("Tips", fetch_tips),
        ("Global Temperature", fetch_global_temp),
        ("Car Crashes", fetch_car_crashes),
        ("Breast Cancer", fetch_breast_cancer),
        ("Health Expenditure", fetch_healthexp),
        ("Iowa Electricity", fetch_iowa_electricity),
        ("Iris", fetch_iris),
        # New datasets
        ("Auto MPG", fetch_mpg),
        ("Flights", fetch_flights),
        ("Titanic", fetch_titanic),
        ("Old Faithful Geyser", fetch_geyser),
        ("Diamonds", fetch_diamonds),
        ("Dow Jones", fetch_dowjones),
        ("GLUE Benchmark", fetch_glue),
        ("fMRI", fetch_fmri),
        ("Exoplanets", fetch_planets),
        ("NYC Taxis", fetch_taxis),
        ("Wine", fetch_wine),
        ("Diabetes", fetch_diabetes),
        ("Seattle Weather", fetch_seattle_weather),
        ("Stocks", fetch_stocks),
        ("Disasters", fetch_disasters),
        ("CO2 Concentration", fetch_co2_concentration),
        ("Motor Trend Cars", fetch_mtcars),
        ("Chick Weight", fetch_chickweight),
        ("World Happiness", fetch_world_happiness),
        ("Country Stats", fetch_country_stats),
    ]

    succeeded = 0
    failed = []
    for name, func in fetchers:
        try:
            print(f"[{name}]")
            func()
            succeeded += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed.append(name)
        print()

    print(f"Done: {succeeded}/{len(fetchers)} datasets downloaded.")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
