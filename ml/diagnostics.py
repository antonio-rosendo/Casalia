"""Pre-registered diagnostic of the challenger (see reports/diagnostics_plan.md).

For every fold (development 2010-2021 and holdout 2022-2025), the fold's own
gradient boosting model is explained on its own test rows with grouped
interventional TreeSHAP, refit without each feature group (ablation), and its
test inputs are checked against the training range.

Usage:  python diagnostics.py   -> reports/diagnostics.md
"""

from pathlib import Path

import numpy as np
import pandas as pd
import shap

from features import FEATURES, SMALL_MARKETS, TARGET, load_dataset
from models import SEED, GradientBoosting, mae, purged_split, set_seed

REPORT_PATH = Path(__file__).parent / "reports" / "diagnostics.md"
YEARS = range(2010, 2026)
HOLDOUT_YEARS = range(2022, 2026)
BACKGROUND_ROWS = 300
MIN_MAE_GAIN = 0.5  # pp, from the decision rule

GROUPS = {
    "momentum": ["price_chg_12m", "price_chg_3m"],
    "inflation": ["cpi_chg_12m"],
    "rates": ["euribor_12m", "euribor_chg_12m"],
    "labour": ["unemployment_rate", "unemployment_chg_12m"],
    "credit": ["mortgages_chg_12m"],
}
HYPOTHESES = {"H1 (inflation)": "inflation", "H2 (rates)": "rates"}


def grouped_shap(model: GradientBoosting, train: pd.DataFrame, test: pd.DataFrame) -> dict:
    background = train[FEATURES].sample(min(BACKGROUND_ROWS, len(train)), random_state=SEED)
    # An explicit masker keeps all background rows (shap would otherwise subsample to 100).
    masker = shap.maskers.Independent(background, max_samples=len(background))
    explainer = shap.TreeExplainer(model.model_, data=masker,
                                   feature_perturbation="interventional")
    values = explainer.shap_values(test[FEATURES])
    contrib = pd.DataFrame(values, columns=FEATURES)
    return {g: contrib[cols].sum(axis=1).mean() * 100 for g, cols in GROUPS.items()}


def out_of_range(train: pd.DataFrame, test: pd.DataFrame) -> dict:
    out = {}
    for g, cols in GROUPS.items():
        lo, hi = train[cols].min(), train[cols].max()
        outside = ((test[cols] < lo) | (test[cols] > hi)).any(axis=1)
        out[g] = outside.mean() * 100
    return out


def main() -> None:
    set_seed()
    ds = load_dataset()
    ds = ds[~ds["region"].isin(SMALL_MARKETS)]
    shap_rows, ablation_rows, range_rows = [], [], []

    for year in YEARS:
        test_start = pd.Timestamp(year=year, month=1, day=1)
        test = ds[ds["date"].dt.year == year].reset_index(drop=True)
        train = purged_split(ds, test_start)
        if test.empty or train.empty:
            continue

        full = GradientBoosting().fit(train)
        base_mae = mae(full.predict(test), test[TARGET]) * 100
        shap_rows.append({"year": year, **grouped_shap(full, train, test)})
        range_rows.append({"year": year, **out_of_range(train, test)})

        ablation = {"year": year, "MAE all features": base_mae}
        for g, cols in GROUPS.items():
            kept = [f for f in FEATURES if f not in cols]
            m = GradientBoosting(features=kept).fit(train)
            # Positive = MAE went down (better) when the group was removed.
            ablation[f"without {g}"] = base_mae - mae(m.predict(test), test[TARGET]) * 100
        ablation_rows.append(ablation)

    shap_df = pd.DataFrame(shap_rows).set_index("year")
    abl_df = pd.DataFrame(ablation_rows).set_index("year")
    rng_df = pd.DataFrame(range_rows).set_index("year")

    verdicts = []
    for year in HOLDOUT_YEARS:
        most_negative = shap_df.loc[year].idxmin()
        for hyp, group in HYPOTHESES.items():
            a = most_negative == group
            b = abl_df.loc[year, f"without {group}"] >= MIN_MAE_GAIN
            verdict = "supported" if a and b else "partly supported" if a or b else "not supported"
            verdicts.append({
                "year": year, "hypothesis": hyp,
                "(a) most negative SHAP group": most_negative,
                "(b) MAE gain without group (pp)": round(abl_df.loc[year, f"without {group}"], 2),
                "verdict": verdict,
            })
    verdict_df = pd.DataFrame(verdicts)

    text = "\n".join([
        "# Diagnostic of the challenger (pre-registered)",
        "",
        "Plan and decision rule: [diagnostics_plan.md](diagnostics_plan.md), committed before "
        "this script was run. 17 main regions; each fold's own model explains its own test rows.",
        "",
        "## Verdicts on the holdout years",
        "",
        verdict_df.to_markdown(index=False),
        "",
        "## Mean SHAP contribution by feature group (pp of 12-month change)",
        "",
        "Negative = the group pushed the forecast down relative to the model's average forecast.",
        "",
        shap_df.to_markdown(floatfmt="+.2f"),
        "",
        "## Ablation: MAE change when refitting without each group (pp)",
        "",
        "Positive = the model was better without that group. 'MAE all features' is the "
        "challenger's MAE in that year.",
        "",
        abl_df.to_markdown(floatfmt=".2f"),
        "",
        "## Test rows with inputs outside the training range (%)",
        "",
        rng_df.to_markdown(floatfmt=".0f"),
        "",
    ])
    REPORT_PATH.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
