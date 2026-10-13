"""Empirical prediction intervals for the momentum forecast.

The interval at origin q is the momentum forecast plus the 10th and 90th
percentiles of momentum's past errors (actual - forecast). Only errors that
were already observable at q are used: their 12-month target must have ended
by q (the same purge rule as the evaluation), so the interval never uses the
future. Errors are pooled across the 17 main regions.

The one free choice, how far back to look, is made on the development years
(2010-2021) only. Usage:  python intervals.py   -> reports/intervals.md
"""

from pathlib import Path

import numpy as np
import pandas as pd

from features import SMALL_MARKETS, TARGET, load_dataset

REPORT_DIR = Path(__file__).parent / "reports"
LOWER_Q, UPPER_Q = 0.10, 0.90          # 80% nominal interval
MIN_ERRORS = 8 * 17                    # need about two years of errors to start
WINDOWS = {"all history": None, "last 5 years": 20, "last 3 years": 12}  # in quarters
CHOSEN_WINDOW = "last 5 years"  # dev years: coverage closest to 80% (interval scores within 0.5 pp)
DEV_YEARS = range(2010, 2022)
HOLDOUT_YEARS = range(2022, 2026)


def momentum_errors(ds: pd.DataFrame) -> pd.DataFrame:
    main = ds[~ds["region"].isin(SMALL_MARKETS)]
    return main.assign(error=main[TARGET] - main["price_chg_12m"])[["date", "target_date", "error"]]


def error_quantiles(errors: pd.DataFrame, origin: pd.Timestamp, window_quarters):
    """10th/90th percentile of the errors already realised at `origin`."""
    seen = errors[errors["target_date"] <= origin]
    if window_quarters is not None:
        cutoff = origin - pd.DateOffset(months=3 * window_quarters)
        seen = seen[seen["target_date"] > cutoff]
    if len(seen) < MIN_ERRORS:
        return None
    return np.quantile(seen["error"], [LOWER_Q, UPPER_Q])


def interval(ds: pd.DataFrame, origin: pd.Timestamp, forecast: float, window=CHOSEN_WINDOW):
    """(low, high) 80% interval around a momentum forecast made at `origin`."""
    q = error_quantiles(momentum_errors(ds), origin, WINDOWS[window])
    if q is None:
        raise ValueError(f"Not enough realised errors before {origin.date()} for an interval")
    return forecast + q[0], forecast + q[1]


def evaluate_window(ds: pd.DataFrame, window_quarters, years) -> pd.DataFrame:
    errors = momentum_errors(ds)
    rows = []
    test = ds[~ds["region"].isin(SMALL_MARKETS) & ds["date"].dt.year.isin(list(years))]
    for origin, g in test.groupby("date"):
        q = error_quantiles(errors, origin, window_quarters)
        if q is None:
            continue
        low = g["price_chg_12m"] + q[0]
        high = g["price_chg_12m"] + q[1]
        y = g[TARGET]
        alpha = 1 - (UPPER_Q - LOWER_Q)
        # Interval (Winkler) score: width plus a penalty when the actual falls outside.
        score = (high - low) + (2 / alpha) * ((low - y).clip(lower=0) + (y - high).clip(lower=0))
        rows.append(pd.DataFrame({
            "year": origin.year,
            "covered": (y >= low) & (y <= high),
            "width_pp": (high - low) * 100,
            "score_pp": score * 100,
        }))
    return pd.concat(rows, ignore_index=True)


def summary(results: pd.DataFrame) -> dict:
    return {
        "Coverage (%)": results["covered"].mean() * 100,
        "Mean width (pp)": results["width_pp"].mean(),
        "Interval score (pp)": results["score_pp"].mean(),
    }


def main() -> None:
    ds = load_dataset()
    dev = {name: evaluate_window(ds, w, DEV_YEARS) for name, w in WINDOWS.items()}
    dev_table = pd.DataFrame({name: summary(r) for name, r in dev.items()}).T

    chosen = dev[CHOSEN_WINDOW]
    hold = evaluate_window(ds, WINDOWS[CHOSEN_WINDOW], HOLDOUT_YEARS)
    by_year = pd.concat([chosen, hold]).groupby("year").agg(
        coverage=("covered", lambda c: c.mean() * 100),
        width_pp=("width_pp", "mean"),
    )

    text = "\n".join([
        "# 80% prediction interval for the momentum forecast",
        "",
        "Interval = momentum forecast + the 10th and 90th percentiles of momentum's past "
        "errors, using only errors already observable at the forecast origin (pooled over "
        "17 regions). A well-calibrated 80% interval covers the actual value about 80% of "
        "the time. Lower interval score is better (width plus a penalty for misses).",
        "",
        "## Choosing the look-back window (development years 2010-2021 only)",
        "",
        dev_table.to_markdown(floatfmt=".1f"),
        "",
        f"Chosen: **{CHOSEN_WINDOW}**.",
        "",
        "## Coverage by year with the chosen window",
        "",
        "2022-2025 is the holdout period. It was already seen when this interval was designed, "
        "so its coverage is reported but is not a blind test.",
        "",
        by_year.to_markdown(floatfmt=".1f"),
        "",
        "## Holdout 2022-2025 (already seen)",
        "",
        pd.DataFrame([summary(hold)], index=[CHOSEN_WINDOW]).to_markdown(floatfmt=".1f"),
        "",
    ])
    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / "intervals.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
