"""Publish the forecasts for the latest complete quarter.

Writes:
  forecasts/<origin>.json    dated log, committed to git and never edited, so
                             each forecast can be scored once the real data
                             arrive (see score_forecasts.py)
  ../web/public/forecasts.json   the same content, read by the web app

Usage:  python publish_forecasts.py [--refresh]   (--refresh downloads the sources again)
"""

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd

import build_dataset
from features import FEATURE_GROUPS, HORIZON, SMALL_MARKETS
from forecast import forecast_origin

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "forecasts"
WEB_PATH = BASE_DIR.parent / "web" / "public" / "forecasts.json"


def quarter_label(ts: pd.Timestamp) -> str:
    return f"{ts.year}-Q{ts.quarter}"


def to_payload(f: pd.DataFrame) -> dict:
    origin = f.attrs["origin"]
    target = origin + pd.DateOffset(months=3 * HORIZON)
    regions = []
    for _, r in f.iterrows():
        regions.append({
            "region": r["region"],
            "name": r["name"],
            "small_market": r["region"] in SMALL_MARKETS,
            "price_m2_at_origin": round(float(r["base_price"]), 1),
            "champion": {
                "chg_12m": round(float(r["champion_chg_12m"]), 4),
                "low": round(float(r["champion_low"]), 4),
                "high": round(float(r["champion_high"]), 4),
            },
            "challenger": {
                "chg_12m": round(float(r["challenger_chg_12m"]), 4),
                # SHAP: contribution of each feature group, in change units, relative to
                # the model's average forecast; average + contributions = forecast.
                "explanation": {g: round(float(r[f"shap_{g}"]), 4) for g in FEATURE_GROUPS},
            },
        })
    return {
        "generated_on": date.today().isoformat(),
        "origin": quarter_label(origin),
        "target": quarter_label(target),
        "target_meaning": "% change in MIVAU appraised value per m2 between origin and target quarter",
        "champion": f.attrs["champion"],
        "challenger": f.attrs["challenger"],
        "interval": f"80% empirical interval from momentum's realised errors ({f.attrs['interval_window']})",
        "challenger_average_forecast": round(f.attrs["challenger_average"], 4),
        "regions": regions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="download the sources again first")
    args = parser.parse_args()
    if args.refresh:
        build_dataset.OUT_PATH.write_text(build_dataset.build(refresh=True).to_csv(index=False))

    payload = to_payload(forecast_origin())
    LOG_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / f"{payload['origin']}.json"
    if log_path.exists():
        print(f"{log_path.name} already published; the log is never overwritten.")
    else:
        log_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {log_path}")
    WEB_PATH.parent.mkdir(parents=True, exist_ok=True)
    WEB_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {WEB_PATH}")


if __name__ == "__main__":
    main()
