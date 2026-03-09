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
