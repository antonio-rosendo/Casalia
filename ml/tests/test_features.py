"""Leakage and train/serve parity checks on the feature code."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from features import FEATURES, SMALL_MARKETS, TARGET, build_features, load_quarterly
from forecast import SOURCE_COLUMNS, latest_complete_origin

WEB_FORECASTS = Path(__file__).resolve().parents[2] / "web" / "public" / "forecasts.json"


@pytest.fixture(scope="module")
def quarterly():
    return load_quarterly()


@pytest.mark.parametrize("cutoff", ["2008-01-01", "2015-07-01", "2022-04-01"])
def test_features_never_see_the_future(quarterly, cutoff):
    """Rewriting every value after a quarter must not change any feature up to it."""
    cutoff = pd.Timestamp(cutoff)
    tampered = quarterly.copy()
    later = tampered["date"] > cutoff
    tampered.loc[later, SOURCE_COLUMNS] = tampered.loc[later, SOURCE_COLUMNS] * 2 + 1

    def up_to_cutoff(df):
        feats = build_features(df, require_target=False)
        return feats[feats["date"] <= cutoff].set_index(["region", "date"])

    before, after = up_to_cutoff(quarterly), up_to_cutoff(tampered)
    pd.testing.assert_frame_equal(before[FEATURES], after[FEATURES])
    # Sanity check that the tampering bites: targets of the last year before the cutoff do change.
    recent = before.index.get_level_values("date") > cutoff - pd.DateOffset(years=1)
    assert not np.allclose(before.loc[recent, TARGET], after.loc[recent, TARGET])


def test_serving_rows_match_training_rows(quarterly):
    """The rows built for serving (no target yet) are the training rows plus newer ones."""
    train = build_features(quarterly)
    serve = build_features(quarterly, require_target=False)
    merged = train.merge(serve, on=["region", "date"], suffixes=("_train", "_serve"))
    assert len(merged) == len(train)
    for f in FEATURES:
        np.testing.assert_array_equal(merged[f"{f}_train"], merged[f"{f}_serve"])
    assert serve["date"].max() > train["date"].max()


def test_origin_waits_for_every_source(quarterly):
    """If one source is missing the latest quarter for one region, step back a quarter."""
    latest = latest_complete_origin(quarterly)
    gap = quarterly.copy()
    gap.loc[(gap["region"] == "madrid") & (gap["date"] == latest), "mortgages"] = np.nan
    assert latest_complete_origin(gap) == latest - pd.DateOffset(months=3)


def test_published_forecasts_match_the_feature_code(quarterly):
    """What the API serves equals what the shared code computes from the dataset."""
    payload = json.loads(WEB_FORECASTS.read_text(encoding="utf-8"))
    year, q = payload["origin"].split("-Q")
    origin = pd.Period(year=int(year), quarter=int(q), freq="Q").to_timestamp()
    feats = build_features(quarterly, require_target=False)
    today = feats[feats["date"] == origin].set_index("region")
    for r in payload["regions"]:
        # The champion (momentum) forecasts the change of the last 12 months.
        assert r["champion"]["chg_12m"] == pytest.approx(today.loc[r["region"], "price_chg_12m"],
                                                         abs=1e-4)
        assert r["champion"]["low"] <= r["champion"]["chg_12m"] <= r["champion"]["high"]
        # SHAP is additive: the average forecast plus the contributions gives the forecast.
        explained = payload["challenger_average_forecast"] + sum(
            r["challenger"]["explanation"].values())
        assert explained == pytest.approx(r["challenger"]["chg_12m"], abs=5e-4)
    main = {r["region"] for r in payload["regions"] if not r["small_market"]}
    assert main == set(quarterly["region"]) - set(SMALL_MARKETS)
