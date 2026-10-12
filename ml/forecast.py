"""Forecasts for the latest quarter that every source has published.

For each region it returns the champion forecast (momentum) with its 80%
interval, and the challenger forecast (gradient boosting) run in shadow.
publish_forecasts.py writes them to a dated JSON that is committed to git, so
every published forecast can be scored later against what actually happened.
"""

import pandas as pd

from features import FEATURES, SMALL_MARKETS, build_features, load_quarterly
from intervals import CHOSEN_WINDOW, interval
from models import CHALLENGER, CHAMPION, purged_split, set_seed

SOURCE_COLUMNS = ["price_m2", "cpi", "mortgages", "unemployment_rate", "euribor_12m"]


class IncompleteDataError(RuntimeError):
    """Raised when a source has not published the quarter we want to forecast from."""


def latest_complete_origin(quarterly: pd.DataFrame) -> pd.Timestamp:
    """Latest quarter for which every source has data for all main regions."""
    main = quarterly[~quarterly["region"].isin(SMALL_MARKETS)]
    complete = main.groupby("date")[SOURCE_COLUMNS].apply(lambda g: g.notna().all().all())
    if not complete.any():
        raise IncompleteDataError("No quarter has complete data")
    return complete[complete].index.max()


def forecast_origin(origin: pd.Timestamp | None = None) -> pd.DataFrame:
    """One row per region: champion forecast, interval and challenger forecast."""
    quarterly = load_quarterly()
    if origin is None:
        origin = latest_complete_origin(quarterly)
    feats = build_features(quarterly, require_target=False)
    today = feats[feats["date"] == origin]
    missing = sorted(set(quarterly.loc[~quarterly["region"].isin(SMALL_MARKETS), "region"])
                     - set(today["region"]))
    if missing:
        raise IncompleteDataError(f"Missing data at {origin.date()} for: {', '.join(missing)}")

    history = build_features(quarterly)  # rows whose 12-month outcome is known
    train = purged_split(history, origin)

    champion = CHAMPION().fit(train)
    set_seed()
    challenger = CHALLENGER().fit(train)

    out = today[["region", "name", "date", "base_price"] + FEATURES].copy()
    out["champion_chg_12m"] = champion.predict(today)
    lows, highs = zip(*(interval(history, origin, f) for f in out["champion_chg_12m"]))
    out["champion_low"], out["champion_high"] = lows, highs
    out["challenger_chg_12m"] = challenger.predict(today)
    out.attrs.update(origin=origin, champion=CHAMPION.name, challenger=CHALLENGER.name,
                     interval_window=CHOSEN_WINDOW, challenger_model=challenger)
    return out.reset_index(drop=True)


if __name__ == "__main__":
    f = forecast_origin()
    print("Origin:", f.attrs["origin"].date())
    cols = ["region", "champion_chg_12m", "champion_low", "champion_high", "challenger_chg_12m"]
    print((f[cols].set_index("region") * 100).round(1))
