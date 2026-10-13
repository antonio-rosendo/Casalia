"""The evaluation and the interval never use outcomes that were not observed yet."""

import numpy as np
import pandas as pd
import pytest

from evaluate import DEV_YEARS, HOLDOUT_YEARS
from features import load_dataset
from intervals import CHOSEN_WINDOW, WINDOWS, error_quantiles, momentum_errors
from models import inner_split, purged_split


@pytest.fixture(scope="module")
def ds():
    return load_dataset()


@pytest.mark.parametrize("year", [*DEV_YEARS, *HOLDOUT_YEARS])
def test_training_outcomes_end_before_the_test_year(ds, year):
    test_start = pd.Timestamp(year=year, month=1, day=1)
    train = purged_split(ds, test_start)
    assert train["target_date"].max() <= test_start
    # The inner splits used for tuning follow the same rule.
    for years_back in (1, 2, 3):
        inner_train, val = inner_split(train, years_back=years_back)
        assert inner_train["target_date"].max() <= val["date"].min()


def test_interval_only_uses_errors_already_observed(ds):
    """Corrupting every error that ends after the origin must not move the interval."""
    errors = momentum_errors(ds)
    origin = pd.Timestamp("2018-04-01")
    window = WINDOWS[CHOSEN_WINDOW]
    tampered = errors.copy()
    tampered.loc[tampered["target_date"] > origin, "error"] = 99.0
    np.testing.assert_array_equal(error_quantiles(errors, origin, window),
                                  error_quantiles(tampered, origin, window))
