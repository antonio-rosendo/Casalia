"""Score every logged forecast whose target quarter has been published.

Each file in forecasts/ was committed before its target data existed, so this
is a truly prospective test of champion and challenger.

Usage:  python score_forecasts.py   -> reports/prospective.md
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from features import SMALL_MARKETS, load_quarterly

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "forecasts"
REPORT_PATH = BASE_DIR / "reports" / "prospective.md"


def quarter_start(label: str) -> pd.Timestamp:
    year, q = label.split("-Q")
    return pd.Period(year=int(year), quarter=int(q), freq="Q").to_timestamp()


def main() -> None:
    prices = load_quarterly().set_index(["region", "date"])["price_m2"]
    lines = ["# Prospective forecasts", "",
             "Forecasts committed to git before their target data existed.", "",
             "| Origin | Target | Status | Champion MAE (pp) | Challenger MAE (pp) | Interval coverage |",
             "|---|---|---|---|---|---|"]
    for path in sorted(LOG_DIR.glob("*.json")):
        log = json.loads(path.read_text(encoding="utf-8"))
        target = quarter_start(log["target"])
        rows = []
        for r in log["regions"]:
            if r["small_market"] or (r["region"], target) not in prices.index:
                continue
            actual = prices[(r["region"], target)] / r["price_m2_at_origin"] - 1
            c = r["champion"]
            rows.append((abs(c["chg_12m"] - actual), abs(r["challenger"]["chg_12m"] - actual),
                         c["low"] <= actual <= c["high"]))
        if not rows:
            lines.append(f"| {log['origin']} | {log['target']} | waiting for data | | | |")
            continue
        champ, chall, covered = (np.array(x) for x in zip(*rows))
        lines.append(f"| {log['origin']} | {log['target']} | scored ({len(rows)} regions) | "
                     f"{champ.mean() * 100:.2f} | {chall.mean() * 100:.2f} | {covered.mean() * 100:.0f}% |")
    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
