"""Feature construction shared by evaluation, training and (later) the API.

Each row is a (region, quarter q) forecast origin: we stand at quarter q, once
its data has been published, and predict the % change in the appraised price
per m2 between q and q + 4 quarters.

Timing: a forecast for origin q can only be made once every source has
published quarter q. The binding sources are the MIVAU price (the file with
2026-Q2 was published on 15 Sep 2026, about 2.5 months after the quarter) and
INE mortgages (each month comes out roughly two months later, so the full
quarter is available 2-3 months after it ends). CPI, the EPA unemployment rate
and the Euribor are out sooner. The effective origin is therefore about
quarter end + 3 months, and every feature uses data up to q and nothing later.
The service refuses to forecast until all sources have quarter q.

The data are today's revised series, not the figures known at the time, so
the evaluation is pseudo out-of-sample (see FINDINGS.md).

There are no calendar features (they take values in production that training
never saw) and no raw levels that trend over time; the Euribor and
unemployment rates are kept as levels because they are already bounded rates.
"""

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).parent
DATASET_PATH = BASE_DIR / "data" / "processed" / "dataset.csv"

HORIZON = 4  # quarters ahead (12 months)
SMALL_MARKETS = ("ceuta", "melilla")  # tiny, noisy markets, reported apart

FEATURES = [
    "price_chg_12m",        # momentum: % change in price over the last 12 months
    "price_chg_3m",         # % change over the last quarter (acceleration)
    "cpi_chg_12m",          # regional inflation over the last 12 months
    "mortgages_chg_12m",    # log change in mortgages signed vs a year earlier
    "unemployment_rate",    # regional unemployment rate (%)
    "unemployment_chg_12m", # change in that rate over 12 months (pp)
    "euribor_12m",          # 12-month Euribor (%), the reference for mortgages
    "euribor_chg_12m",      # change in the Euribor over 12 months (pp)
]
TARGET = "target_chg_12m"

# Feature groups used to explain forecasts: correlated features (e.g. the two
# momentum measures) share SHAP credit arbitrarily, so contributions are
# reported per group.
FEATURE_GROUPS = {
    "momentum": ["price_chg_12m", "price_chg_3m"],
    "inflation": ["cpi_chg_12m"],
    "rates": ["euribor_12m", "euribor_chg_12m"],
    "labour": ["unemployment_rate", "unemployment_chg_12m"],
    "credit": ["mortgages_chg_12m"],
}


def load_quarterly(path: Path = DATASET_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.sort_values(["region", "date"]).reset_index(drop=True)
    _check_contiguous_quarters(df)
    return df


def _check_contiguous_quarters(df: pd.DataFrame) -> None:
    """shift(n) assumes one row per quarter with no gaps; fail loudly otherwise."""
    for region, g in df.groupby("region"):
        quarter_index = g["date"].dt.year * 4 + g["date"].dt.quarter
        if not (quarter_index.diff().dropna() == 1).all():
            raise ValueError(f"Non-contiguous quarters for region {region}")


def add_features(g: pd.DataFrame) -> pd.DataFrame:
    """Features for one region's quarterly history (sorted by date)."""
    g = g.copy()
    price = g["price_m2"]
    g["price_chg_12m"] = price / price.shift(4) - 1
    g["price_chg_3m"] = price / price.shift(1) - 1
    g["cpi_chg_12m"] = g["cpi"] / g["cpi"].shift(4) - 1
    # Log change: mortgage counts jump a lot and logs tame the spikes.
    g["mortgages_chg_12m"] = np.log(g["mortgages"] / g["mortgages"].shift(4))
    g["unemployment_chg_12m"] = g["unemployment_rate"] - g["unemployment_rate"].shift(4)
    g["euribor_chg_12m"] = g["euribor_12m"] - g["euribor_12m"].shift(4)
    return g


def build_features(df: pd.DataFrame, require_target: bool = True) -> pd.DataFrame:
    """One row per (region, quarter) with FEATURES, TARGET and metadata.

    With require_target=False, rows whose 12-month future is not known yet are
    kept too: those are the origins we can forecast from today."""
    out = []
    for _, g in df.groupby("region", sort=False):
        g = add_features(g.sort_values("date"))
        g["base_price"] = g["price_m2"]
        g["target_price"] = g["price_m2"].shift(-HORIZON)
        g[TARGET] = g["target_price"] / g["base_price"] - 1
        g["target_date"] = g["date"].shift(-HORIZON)
        out.append(g)
    feats = pd.concat(out, ignore_index=True)
    keep = ["region", "name", "date", "target_date", "base_price", "target_price"]
    feats = feats[keep + FEATURES + [TARGET]]
    # Rows without full history (and, by default, without an observed future) are dropped.
    required = FEATURES + ([TARGET] if require_target else [])
    return feats.dropna(subset=required).reset_index(drop=True)


def load_dataset() -> pd.DataFrame:
    return build_features(load_quarterly())


if __name__ == "__main__":
    ds = load_dataset()
    print(ds["date"].min().date(), "->", ds["date"].max().date(), "|", len(ds), "rows,",
          ds["region"].nunique(), "regions")
    print(ds[FEATURES + [TARGET]].describe().T.round(4))
