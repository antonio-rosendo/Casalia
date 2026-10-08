"""Feature construction shared by evaluation, training and (later) the API.

Each row is a (region, quarter q) forecast origin: we stand at quarter q, once
its data has been published, and predict the % change in price per m2 between
q and q + 4 quarters.

Leakage rules (see FINDINGS.md):
- Price, CPI and mortgages for quarter q are published about two months after
  the quarter ends, all at roughly the same time, so they can be used at q.
- Immigration in the raw file is an annual stock (value at 1 January) linearly
  interpolated across the year, so quarters 2-4 already contain next year's
  figure. We only keep the 1 January values and use the one from the previous
  year, which is certainly published by then.
- Median age is semiannual and published with a delay of about six months, so
  it is lagged two quarters.
- No calendar features: they take values in production that training never saw.
"""

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).parent
RAW_PATH = BASE_DIR / "data" / "raw" / "datos_unidos_meses.csv"

HORIZON = 4  # quarters ahead (12 months)
SMALL_MARKETS = ("ceuta", "melilla")  # tiny, noisy markets reported apart

FEATURES = [
    "price_chg_12m",       # momentum: % change in price over the last 12 months
    "price_chg_3m",        # % change over the last quarter (acceleration)
    "cpi_chg_12m",         # inflation over the last 12 months
    "mortgages_chg_12m",   # log change in mortgages signed vs a year earlier
    "immigration_chg_1y",  # growth of the foreign-born stock (lagged a year)
    "median_age",          # population median age (lagged two quarters)
]
TARGET = "target_chg_12m"


def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["year"], format="%Y-%m-%d")
    df = df.sort_values(["comunidad", "date"]).reset_index(drop=True)
    _check_contiguous_quarters(df)
    return df


def _check_contiguous_quarters(df: pd.DataFrame) -> None:
    """shift(n) assumes one row per quarter with no gaps; fail loudly otherwise."""
    for region, g in df.groupby("comunidad"):
        quarter_index = g["date"].dt.year * 4 + g["date"].dt.quarter
        if not (quarter_index.diff().dropna() == 1).all():
            raise ValueError(f"Non-contiguous quarters for region {region}")


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return one row per (region, quarter) with FEATURES, TARGET and metadata."""
    out = []
    for region, g in df.groupby("comunidad", sort=False):
        g = g.sort_values("date").copy()
        price = g["precio"]

        g["price_chg_12m"] = price / price.shift(4) - 1
        g["price_chg_3m"] = price / price.shift(1) - 1
        g["cpi_chg_12m"] = g["IPC"] / g["IPC"].shift(4) - 1
        # Log change: mortgage counts jump a lot (up to +438%) and logs tame the spikes.
        g["mortgages_chg_12m"] = np.log(g["num_hipotecas"] / g["num_hipotecas"].shift(4))

        # Immigration: keep only the real annual values (quarter 1), carry them
        # through the year, then use last year's growth.
        annual = g["num_inmigracion"].where(g["date"].dt.quarter == 1).ffill()
        annual_prev = annual.shift(4)       # value at 1 Jan of the previous year
        annual_prev2 = annual.shift(8)      # and the year before
        g["immigration_chg_1y"] = annual_prev / annual_prev2 - 1

        g["median_age"] = g["edad_media"].shift(2)

        g["base_price"] = price
        g["target_price"] = price.shift(-HORIZON)
        g[TARGET] = g["target_price"] / price - 1
        g["target_date"] = g["date"].shift(-HORIZON)
        out.append(g)

    feats = pd.concat(out, ignore_index=True)
    keep = ["comunidad", "name", "date", "target_date", "base_price", "target_price"]
    feats = feats[keep + FEATURES + [TARGET]]
    # Drop rows without full history or without an observed future.
    feats = feats.dropna(subset=FEATURES + [TARGET]).reset_index(drop=True)
    return feats


def load_dataset() -> pd.DataFrame:
    return build_features(load_raw())


if __name__ == "__main__":
    ds = load_dataset()
    print(ds.groupby("comunidad").size().describe())
    print(ds["date"].min(), "->", ds["date"].max(), "|", len(ds), "rows")
    print(ds[FEATURES + [TARGET]].describe().T.round(4))
