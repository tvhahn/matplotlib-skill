#!/usr/bin/env python3
"""Generate pre-computed datasets for chart patterns.

Each chart pattern that currently embeds computation (aggregation, ML models,
correlation matrices) gets pre-computed outputs so the pattern files contain
only visualization code.

Output: data/raw/precomputed/{p3,p5,p6,p7,p9,ml}/<dataset>.{csv,npz}
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve, roc_curve
from sklearn.preprocessing import LabelEncoder

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "raw" / "precomputed"


# ---------------------------------------------------------------------------
# P3: Time Series — aggregate to annual with rolling mean
# Output CSV: year, value, rolling
# ---------------------------------------------------------------------------

P3_CONFIGS = {
    "global_temp": {
        "file": "public/global_temp.csv",
        "time_col": "Year",
        "value_col": "Anomaly",
        "agg": "annual_mean",  # groupby year → mean
        "rolling_window": 10,
    },
    "flights": {
        "file": "public/flights.csv",
        "time_col": "year",
        "value_col": "passengers",
        "agg": "annual_mean",
        "rolling_window": 10,
    },
    "birth_percentage": {
        "file": "beautiful-plots/birth_percentage.csv",
        "time_col": "dob_yy",
        "value_col": "percent_above_avg",
        "agg": "annual_mean",
        "rolling_window": 10,
    },
    "dowjones": {
        "file": "public/dowjones.csv",
        "time_col": "Date",
        "value_col": "Price",
        "agg": "annual_mean_from_date",  # parse date → extract year → groupby
        "rolling_window": 10,
    },
    "co2_concentration": {
        "file": "public/co2_concentration.csv",
        "time_col": "Date",
        "value_col": "CO2",
        "agg": "annual_mean_from_date",
        "rolling_window": 10,
    },
    "stocks": {
        "file": "public/stocks.csv",
        "time_col": "date",
        "value_col": "price",
        "agg": "annual_mean_from_date",
        "rolling_window": 10,
        "filter": {"symbol": "AAPL"},
    },
    "planets": {
        "file": "public/planets.csv",
        "time_col": "year",
        "value_col": None,  # count per year
        "agg": "annual_count",
        "rolling_window": 10,
    },
}


def generate_p3():
    """Generate pre-computed time series datasets."""
    outdir = OUT / "p3"
    outdir.mkdir(parents=True, exist_ok=True)

    for name, cfg in P3_CONFIGS.items():
        df = pd.read_csv(RAW / cfg["file"])

        # Apply filters
        if "filter" in cfg:
            for col, val in cfg["filter"].items():
                df = df[df[col] == val]

        if cfg["agg"] == "annual_mean":
            df_annual = (
                df.groupby(cfg["time_col"])[cfg["value_col"]]
                .mean()
                .reset_index()
            )
            df_annual.columns = ["year", "value"]
        elif cfg["agg"] == "annual_mean_from_date":
            df[cfg["time_col"]] = pd.to_datetime(df[cfg["time_col"]])
            df["_year"] = df[cfg["time_col"]].dt.year
            df_annual = (
                df.groupby("_year")[cfg["value_col"]].mean().reset_index()
            )
            df_annual.columns = ["year", "value"]
        elif cfg["agg"] == "annual_count":
            df_annual = (
                df.groupby(cfg["time_col"]).size().reset_index(name="value")
            )
            df_annual.columns = ["year", "value"]

        # Filter partial periods (≥6 obs in original data)
        if cfg["agg"] in ("annual_mean", "annual_mean_from_date"):
            if cfg["value_col"] is not None:
                counts = df.groupby(
                    df[cfg["time_col"]].dt.year
                    if cfg["agg"] == "annual_mean_from_date"
                    else cfg["time_col"]
                ).size()
                valid_years = counts[counts >= 6].index
                df_annual = df_annual[df_annual["year"].isin(valid_years)]

        # Rolling mean
        window = cfg["rolling_window"]
        df_annual = df_annual.sort_values("year").reset_index(drop=True)
        df_annual["rolling"] = (
            df_annual["value"].rolling(window, center=True).mean()
        )

        df_annual.to_csv(outdir / f"{name}.csv", index=False)
        print(f"  P3/{name}: {len(df_annual)} rows")


# ---------------------------------------------------------------------------
# P5: Lollipop — groupby → min/mean/max, sorted by avg
# Output CSV: name, min, max, avg
# ---------------------------------------------------------------------------

P5_CONFIGS = {
    "healthexp": {
        "file": "public/healthexp.csv",
        "group_col": "Country",
        "value_col": "Spending_USD",
    },
    "mpg": {
        "file": "public/mpg.csv",
        "group_col": "origin",
        "value_col": "mpg",
    },
    "diamonds": {
        "file": "public/diamonds.csv",
        "group_col": "color",
        "value_col": "price",
    },
    "best_results": {
        "file": "beautiful-plots/best_results.csv",
        "precomputed": True,  # already has clf_name, auc_min, auc_avg, auc_max
        "name_col": "clf_name",
        "min_col": "auc_min",
        "max_col": "auc_max",
        "avg_col": "auc_avg",
    },
    "world_happiness": {
        "file": "public/world_happiness.csv",
        "group_col": "Region",
        "value_col": "Happiness Score",
    },
    "country_stats": {
        "file": "public/country_stats.csv",
        "group_col": "continent",
        "value_col": "lifeExp",
    },
    "glue": {
        "file": "public/glue.csv",
        "group_col": "Model",
        "value_col": "Score",
    },
}


def generate_p5():
    """Generate pre-computed lollipop datasets."""
    outdir = OUT / "p5"
    outdir.mkdir(parents=True, exist_ok=True)

    for name, cfg in P5_CONFIGS.items():
        df = pd.read_csv(RAW / cfg["file"])

        if cfg.get("precomputed"):
            result = pd.DataFrame(
                {
                    "name": df[cfg["name_col"]],
                    "min": df[cfg["min_col"]],
                    "max": df[cfg["max_col"]],
                    "avg": df[cfg["avg_col"]],
                }
            )
        else:
            agg = df.groupby(cfg["group_col"])[cfg["value_col"]].agg(
                ["min", "mean", "max"]
            )
            result = pd.DataFrame(
                {
                    "name": agg.index,
                    "min": agg["min"].values,
                    "max": agg["max"].values,
                    "avg": agg["mean"].values,
                }
            )

        result = result.sort_values("avg", ascending=True).reset_index(
            drop=True
        )
        result.to_csv(outdir / f"{name}.csv", index=False)
        print(f"  P5/{name}: {len(result)} rows")


# ---------------------------------------------------------------------------
# P6: Decision Boundary — KNN fit + mesh grid + predict/predict_proba
# Output NPZ: mesh_x0, mesh_x1, yy_hat, yy_prob, X, y, class_names
# ---------------------------------------------------------------------------

P6_CONFIGS = {
    "iris": {
        "file": "public/iris.csv",
        "features": ["petal length (cm)", "petal width (cm)"],
        "target": "target",
        "class_names_col": "target_name",
    },
    "wine": {
        "file": "public/wine.csv",
        "features": ["alcohol", "malic_acid"],
        "target": "target",
        "class_names_col": "target_name",
    },
    "breast_cancer": {
        "file": "public/breast_cancer.csv",
        "features": ["mean radius", "mean texture"],
        "target": "target",
        "class_names_col": "target_name",
    },
    "geyser": {
        "file": "public/geyser.csv",
        "features": ["duration", "waiting"],
        "target": "kind",
        "class_names_col": None,  # encode from unique values
    },
    "penguins": {
        "file": "public/penguins.csv",
        "features": ["bill_length_mm", "bill_depth_mm"],
        "target": "species",
        "class_names_col": None,
    },
}


def generate_p6():
    """Generate pre-computed decision boundary datasets."""
    outdir = OUT / "p6"
    outdir.mkdir(parents=True, exist_ok=True)

    for name, cfg in P6_CONFIGS.items():
        df = pd.read_csv(RAW / cfg["file"]).dropna(
            subset=cfg["features"] + [cfg["target"]]
        )

        X = df[cfg["features"]].values

        if cfg["class_names_col"]:
            y = df[cfg["target"]].values.astype(int)
            class_names = df[cfg["class_names_col"]].unique().tolist()
            # Ensure order matches integer labels
            class_names = [
                df[df[cfg["target"]] == i][cfg["class_names_col"]].iloc[0]
                for i in sorted(df[cfg["target"]].unique())
            ]
        else:
            le = LabelEncoder()
            y = le.fit_transform(df[cfg["target"]])
            class_names = le.classes_.tolist()

        # Fit classifier
        clf = KNeighborsClassifier(n_neighbors=15)
        clf.fit(X, y)

        # Mesh grid — fixed point count for consistent dot density
        n_grid = 50  # ~2,500 total mesh points, matches original inspiration
        x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
        y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
        xx0, xx1 = np.meshgrid(
            np.linspace(x_min, x_max, n_grid),
            np.linspace(y_min, y_max, n_grid)
        )
        mesh_points = np.c_[xx0.ravel(), xx1.ravel()]
        yy_hat = clf.predict(mesh_points)
        yy_prob = clf.predict_proba(mesh_points).max(axis=1)

        np.savez_compressed(
            outdir / f"{name}.npz",
            mesh_x0=xx0,
            mesh_x1=xx1,
            yy_hat=yy_hat.reshape(xx0.shape),
            yy_prob=yy_prob.reshape(xx0.shape),
            X=X,
            y=y,
            class_names=np.array(class_names),
            feature_names=np.array(cfg["features"]),
        )
        print(
            f"  P6/{name}: mesh {xx0.shape}, {len(X)} points, "
            f"{len(class_names)} classes"
        )


# ---------------------------------------------------------------------------
# P7: Heatmap — correlation matrix or pivot table
# Output CSV: correlation matrix with column names as index
# ---------------------------------------------------------------------------

P7_CONFIGS = {
    "penguins": {
        "file": "public/penguins.csv",
        "type": "corr",
    },
    "mpg": {
        "file": "public/mpg.csv",
        "type": "corr",
        "cols": [
            "mpg",
            "displacement",
            "horsepower",
            "weight",
            "acceleration",
        ],
    },
    "diamonds": {
        "file": "public/diamonds.csv",
        "type": "corr",
        "cols": ["carat", "depth", "table", "price", "x", "y", "z"],
    },
    "wine": {
        "file": "public/wine.csv",
        "type": "corr",
        "exclude": ["target", "target_name"],
    },
    "birth_percentage": {
        "file": "beautiful-plots/birth_percentage.csv",
        "type": "pivot",
        "index": "dob_yy",
        "columns": "birth_month",
        "values": "percent_above_avg",
    },
    "tips": {
        "file": "public/tips.csv",
        "type": "corr",
        "cols": ["total_bill", "tip", "size"],
    },
    "flights": {
        "file": "public/flights.csv",
        "type": "pivot",
        "index": "year",
        "columns": "month",
        "values": "passengers",
    },
    "diabetes": {
        "file": "public/diabetes.csv",
        "type": "corr",
        "exclude": ["target"],
    },
    "mtcars": {
        "file": "public/mtcars.csv",
        "type": "corr",
        "exclude": ["car"],
    },
    "taxis": {
        "file": "public/taxis.csv",
        "type": "corr",
        "cols": ["distance", "fare", "tip", "tolls", "total"],
    },
}


def generate_p7():
    """Generate pre-computed heatmap datasets."""
    outdir = OUT / "p7"
    outdir.mkdir(parents=True, exist_ok=True)

    for name, cfg in P7_CONFIGS.items():
        df = pd.read_csv(RAW / cfg["file"])

        if cfg["type"] == "corr":
            if "cols" in cfg:
                num_df = df[cfg["cols"]]
            elif "exclude" in cfg:
                num_df = df.select_dtypes("number").drop(
                    columns=[
                        c
                        for c in cfg["exclude"]
                        if c in df.select_dtypes("number").columns
                    ]
                )
            else:
                # Auto-select numeric, exclude year/id/index
                num_df = df.select_dtypes("number")
                drop = [
                    c
                    for c in num_df.columns
                    if c.lower() in ("year", "id", "index")
                ]
                num_df = num_df.drop(columns=drop)

            corr = num_df.corr()
            corr.to_csv(outdir / f"{name}.csv")
            print(f"  P7/{name}: {corr.shape[0]}x{corr.shape[1]} corr matrix")

        elif cfg["type"] == "pivot":
            pivot = df.pivot_table(
                index=cfg["index"],
                columns=cfg["columns"],
                values=cfg["values"],
                aggfunc="mean",
            )
            pivot.to_csv(outdir / f"{name}.csv")
            print(f"  P7/{name}: {pivot.shape[0]}x{pivot.shape[1]} pivot")


# ---------------------------------------------------------------------------
# P9: PR/ROC — k-fold CV, precision/recall/ROC curves
# Output NPZ: precision_array, recall_array, tpr_array, fpr_array,
#              precision_avg, recall_avg, tpr_avg, fpr_avg, baseline
# ---------------------------------------------------------------------------

P9_CONFIGS = {
    "breast_cancer": {
        "file": "public/breast_cancer.csv",
        "features": None,  # all numeric except target
        "target": "target",
        "exclude_cols": ["target_name"],
    },
    "penguins": {
        "file": "public/penguins.csv",
        "features": ["bill_length_mm", "bill_depth_mm"],
        "target": "species",
        "positive_class": "Adelie",  # binary: Adelie vs others
    },
    "titanic": {
        "file": "public/titanic.csv",
        "features": ["pclass", "age", "fare"],
        "target": "survived",
    },
    "geyser": {
        "file": "public/geyser.csv",
        "features": ["duration", "waiting"],
        "target": "kind",
    },
    "diabetes": {
        "file": "public/diabetes.csv",
        "features": None,  # all numeric except target
        "target": "target",
        "binarize_median": True,  # progression above the median vs below
    },
    "iris": {
        "file": "public/iris.csv",
        "features": ["sepal length (cm)", "sepal width (cm)"],
        "target": "target",
        "positive_class": 1,  # versicolor vs others: the hard class
        "exclude_cols": ["target_name"],
    },
    "wine": {
        "file": "public/wine.csv",
        "features": None,  # all numeric except target
        "target": "target",
        "positive_class": 0,  # class 0 vs others
        "exclude_cols": ["target_name"],
    },
}


def generate_p9():
    """Generate pre-computed PR/ROC curve datasets."""
    outdir = OUT / "p9"
    outdir.mkdir(parents=True, exist_ok=True)

    for name, cfg in P9_CONFIGS.items():
        df = pd.read_csv(RAW / cfg["file"]).dropna()

        # Prepare features
        if cfg["features"]:
            X = df[cfg["features"]].values
        else:
            exclude = [cfg["target"]] + cfg.get("exclude_cols", [])
            num_cols = [
                c
                for c in df.select_dtypes("number").columns
                if c not in exclude
            ]
            X = df[num_cols].values

        # Prepare binary target
        target_series = df[cfg["target"]]
        if cfg.get("binarize_median"):
            y = (target_series > target_series.median()).astype(int).values
        elif "positive_class" in cfg:
            y = (target_series == cfg["positive_class"]).astype(int).values
        elif not pd.api.types.is_numeric_dtype(target_series):
            # Encode string target as binary (first class vs rest)
            le = LabelEncoder()
            y_multi = le.fit_transform(target_series)
            y = (y_multi == 0).astype(int)
        else:
            y = target_series.values.astype(int)

        # Ensure binary
        unique_y = np.unique(y)
        if len(unique_y) > 2:
            # Take class 1 vs rest
            y = (y == 1).astype(int)

        baseline = y.mean()  # prevalence for PR baseline

        # K-fold CV
        skf = StratifiedKFold(
            n_splits=5, shuffle=True, random_state=42
        )
        clf = LogisticRegression(max_iter=10000, random_state=42)

        precision_curves = []
        recall_curves = []
        tpr_curves = []
        fpr_curves = []

        mean_recall = np.linspace(0, 1, 100)
        mean_fpr = np.linspace(0, 1, 100)

        for train_idx, val_idx in skf.split(X, y):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            clf.fit(X_train, y_train)
            y_scores = clf.predict_proba(X_val)[:, 1]

            # PR curve
            precision, recall, _ = precision_recall_curve(y_val, y_scores)
            # Interpolate to common recall grid (reversed for monotonicity)
            interp_precision = np.interp(
                mean_recall, recall[::-1], precision[::-1]
            )
            precision_curves.append(interp_precision)
            recall_curves.append(mean_recall.copy())

            # ROC curve
            fpr_fold, tpr_fold, _ = roc_curve(y_val, y_scores)
            interp_tpr = np.interp(mean_fpr, fpr_fold, tpr_fold)
            interp_tpr[0] = 0.0
            tpr_curves.append(interp_tpr)
            fpr_curves.append(mean_fpr.copy())

        # Average curves
        precision_avg = np.mean(precision_curves, axis=0)
        recall_avg = mean_recall
        tpr_avg = np.mean(tpr_curves, axis=0)
        fpr_avg = mean_fpr

        np.savez_compressed(
            outdir / f"{name}.npz",
            precision_array=np.array(precision_curves),
            recall_array=np.array(recall_curves),
            tpr_array=np.array(tpr_curves),
            fpr_array=np.array(fpr_curves),
            precision_avg=precision_avg,
            recall_avg=recall_avg,
            tpr_avg=tpr_avg,
            fpr_avg=fpr_avg,
            baseline=np.array([baseline]),
        )
        print(
            f"  P9/{name}: {len(precision_curves)} folds, "
            f"baseline={baseline:.3f}"
        )



# ---------------------------------------------------------------------------
# ML diagnostics: training curves and out-of-fold predictions
# Output CSVs:
#   training_<name>.csv    epoch, train_loss, val_loss, train_acc, val_acc
#   predictions_<name>.csv y_true, y_pred   (5-fold out-of-fold predictions)
# ---------------------------------------------------------------------------

ML_TRAINING = {
    "breast_cancer": {"file": "public/breast_cancer.csv", "target": "target", "epochs": 80, "lr": 3e-4},
    "wine": {"file": "public/wine.csv", "target": "target", "epochs": 120, "lr": 3e-3},
    # Disease progression above the median → binary; small, noisy, overfits visibly
    "diabetes": {"file": "public/diabetes.csv", "target": "target", "epochs": 150,
                 "lr": 2e-4, "binarize_median": True},
}

ML_PREDICTIONS = {
    "penguins": {
        "file": "public/penguins.csv",
        "target": "species",
        "features": ["bill_length_mm", "flipper_length_mm"],
    },
    "wine": {"file": "public/wine.csv", "target": "target_name", "features": ["alcohol", "color_intensity"]},
    "iris": {"file": "public/iris.csv", "target": "target_name",
             "features": ["sepal length (cm)", "sepal width (cm)"]},
}


def generate_ml():
    """Per-epoch learning curves (MLP) and out-of-fold class predictions."""
    from sklearn.metrics import accuracy_score, log_loss
    from sklearn.model_selection import cross_val_predict, train_test_split
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler

    outdir = OUT / "ml"
    outdir.mkdir(parents=True, exist_ok=True)

    for name, cfg in ML_TRAINING.items():
        df = pd.read_csv(RAW / cfg["file"]).dropna()
        y = df[cfg["target"]].values
        if cfg.get("binarize_median"):
            y = (y > np.median(y)).astype(int)
        X = df.drop(columns=[cfg["target"]]).select_dtypes("number").values
        X_tr, X_va, y_tr, y_va = train_test_split(
            X, y, test_size=0.4, stratify=y, random_state=0
        )
        scaler = StandardScaler().fit(X_tr)
        X_tr, X_va = scaler.transform(X_tr), scaler.transform(X_va)
        # Small train set + wide net + no regularisation so the validation
        # curve turns up: the chart has an overfitting point to annotate.
        clf = MLPClassifier(
            hidden_layer_sizes=(128, 64), alpha=0.0, learning_rate_init=cfg["lr"],
            batch_size=32, random_state=0,
        )
        classes = np.unique(y)
        rows = []
        for epoch in range(1, cfg["epochs"] + 1):
            clf.partial_fit(X_tr, y_tr, classes=classes)
            rows.append(
                {
                    "epoch": epoch,
                    "train_loss": log_loss(y_tr, clf.predict_proba(X_tr), labels=classes),
                    "val_loss": log_loss(y_va, clf.predict_proba(X_va), labels=classes),
                    "train_acc": accuracy_score(y_tr, clf.predict(X_tr)),
                    "val_acc": accuracy_score(y_va, clf.predict(X_va)),
                }
            )
        out = pd.DataFrame(rows).round(5)
        out.to_csv(outdir / f"training_{name}.csv", index=False)
        best = out.loc[out["val_loss"].idxmin()]
        print(f"  ML/training_{name}: {len(out)} epochs, best val_loss at epoch {int(best.epoch)}")

    for name, cfg in ML_PREDICTIONS.items():
        df = pd.read_csv(RAW / cfg["file"]).dropna(subset=cfg["features"] + [cfg["target"]])
        X = df[cfg["features"]].values
        y = df[cfg["target"]].values
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        clf = LogisticRegression(max_iter=10000, random_state=42)
        pred = cross_val_predict(clf, X, y, cv=skf)
        out = pd.DataFrame({"y_true": y, "y_pred": pred})
        out.to_csv(outdir / f"predictions_{name}.csv", index=False)
        print(f"  ML/predictions_{name}: {len(out)} rows, accuracy {np.mean(y == pred):.3f}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Generating pre-computed datasets...\n")

    print("P3: Time Series (annual + rolling)")
    generate_p3()

    print("\nP5: Lollipop (min/avg/max)")
    generate_p5()

    print("\nP6: Decision Boundary (KNN mesh)")
    generate_p6()

    print("\nP7: Heatmap (correlation / pivot)")
    generate_p7()

    print("\nP9: PR/ROC Curves (5-fold CV)")
    generate_p9()

    print("\nML: training curves + out-of-fold predictions")
    generate_ml()

    print("\nDone! Output in data/raw/precomputed/")


if __name__ == "__main__":
    main()
