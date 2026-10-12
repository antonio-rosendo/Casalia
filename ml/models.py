"""Forecasting models, naive baselines and the leakage-safe splits they use.

Shared by evaluate.py (walk-forward evaluation), forecast.py (published
forecasts) and the API, so every part of the project uses the same code.

Champion / challenger: the model served to users is the CHAMPION. A challenger
replaces it only if it beats the champion in the walk-forward evaluation
(evaluate.py) with a confidence interval that excludes zero.
"""

import copy
import random

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from features import FEATURES, TARGET
from model import PricePredictor

SEED = 42


def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


# --------------------------------------------------------------------------
# Splits
# --------------------------------------------------------------------------

def purged_split(df: pd.DataFrame, test_start: pd.Timestamp):
    """Rows usable for training when forecasting from test_start onwards."""
    return df[df["target_date"] <= test_start]


def inner_split(train: pd.DataFrame, n_quarters: int = 4, years_back: int = 1):
    """Hold out a block of n_quarters origins for tuning, ending years_back years
    before the end of the training data, with the same purge as the outer split."""
    dates = np.sort(train["date"].unique())
    val_start = dates[-n_quarters * years_back]
    val_end = dates[-n_quarters * (years_back - 1) - 1] if years_back > 1 else dates[-1]
    val = train[(train["date"] >= val_start) & (train["date"] <= val_end)]
    inner_train = train[train["target_date"] <= val_start]
    return inner_train, val


def tune(make_model, grid, train: pd.DataFrame, n_years: int = 3):
    """Pick the setting with the lowest mean MAE over the last n_years inner
    validation blocks (one block alone is too noisy to choose from)."""
    scores = {}
    for setting in grid:
        errors = []
        for k in range(1, n_years + 1):
            inner_train, val = inner_split(train, years_back=k)
            if inner_train.empty or val.empty:
                continue
            m = make_model(setting).fit(inner_train[FEATURES], inner_train[TARGET])
            errors.append(mae(m.predict(val[FEATURES]), val[TARGET]))
        scores[setting] = np.mean(errors)
    return min(scores, key=scores.get)


def mae(pred, y) -> float:
    return float(np.mean(np.abs(np.asarray(pred) - np.asarray(y))))


# --------------------------------------------------------------------------
# Models: each one is fit on a training frame and predicts the 12-month change
# --------------------------------------------------------------------------

class NoChange:
    name = "Baseline: no change"

    def fit(self, train):
        return self

    def predict(self, df):
        return np.zeros(len(df))


class Momentum:
    name = "Baseline: momentum"  # next year's change = last year's change

    def fit(self, train):
        return self

    def predict(self, df):
        return df["price_chg_12m"].to_numpy()


class HistoricalMean:
    name = "Baseline: historical mean"

    def fit(self, train):
        self.mean_ = train[TARGET].mean()
        return self

    def predict(self, df):
        return np.full(len(df), self.mean_)


class RidgeModel:
    name = "Ridge regression"
    alphas = (0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0)

    @staticmethod
    def _make(alpha):
        return make_pipeline(StandardScaler(), Ridge(alpha=alpha))

    def fit(self, train):
        self.alpha_ = tune(self._make, self.alphas, train)
        self.model_ = self._make(self.alpha_).fit(train[FEATURES], train[TARGET])
        return self

    def predict(self, df):
        return self.model_.predict(df[FEATURES])


class GradientBoosting:
    name = "Gradient boosting"
    # (max_depth, max_iter): shallow trees and few iterations, there are only
    # a few hundred rows per fold.
    grid = ((2, 100), (2, 300), (3, 100), (3, 300))

    @staticmethod
    def _make(setting):
        depth, iters = setting
        return HistGradientBoostingRegressor(
            max_depth=depth, max_iter=iters, learning_rate=0.05,
            min_samples_leaf=20, l2_regularization=1.0, random_state=SEED,
        )

    def fit(self, train):
        self.setting_ = tune(self._make, self.grid, train)
        self.model_ = self._make(self.setting_).fit(train[FEATURES], train[TARGET])
        return self

    def predict(self, df):
        return self.model_.predict(df[FEATURES])


class MLP:
    name = "Neural network (MLP)"
    max_epochs = 300
    patience = 30

    def fit(self, train):
        set_seed()
        inner_train, val = inner_split(train)
        x_tr = torch.tensor(inner_train[FEATURES].to_numpy(), dtype=torch.float32)
        self.mean_ = x_tr.mean(0, keepdim=True)
        self.std_ = x_tr.std(0, keepdim=True) + 1e-8
        x_tr = (x_tr - self.mean_) / self.std_
        y_tr = torch.tensor(inner_train[TARGET].to_numpy(), dtype=torch.float32)
        x_val = self._scale(val)
        y_val = val[TARGET].to_numpy()

        self.model_ = PricePredictor(input_dim=len(FEATURES), hidden_dim1=32, hidden_dim2=16)
        opt = torch.optim.Adam(self.model_.parameters(), lr=1e-3, weight_decay=1e-3)
        loss_fn = nn.MSELoss()
        gen = torch.Generator().manual_seed(SEED)
        best, best_state, waited = float("inf"), None, 0
        for _ in range(self.max_epochs):
            self.model_.train()
            for idx in torch.randperm(len(x_tr), generator=gen).split(64):
                opt.zero_grad()
                loss_fn(self.model_(x_tr[idx]), y_tr[idx]).backward()
                opt.step()
            score = mae(self._raw_predict(x_val), y_val)
            if score < best:
                best, best_state, waited = score, copy.deepcopy(self.model_.state_dict()), 0
            else:
                waited += 1
                if waited >= self.patience:  # early stopping
                    break
        self.model_.load_state_dict(best_state)
        return self

    def _scale(self, df):
        x = torch.tensor(df[FEATURES].to_numpy(), dtype=torch.float32)
        return (x - self.mean_) / self.std_

    def _raw_predict(self, x):
        self.model_.eval()
        with torch.no_grad():
            return self.model_(x).numpy()

    def predict(self, df):
        return self._raw_predict(self._scale(df))


MODELS = [NoChange, Momentum, HistoricalMean, RidgeModel, GradientBoosting, MLP]
CANDIDATE = GradientBoosting.name  # best non-baseline model on the development folds
CHAMPION = Momentum                # served to users: best on development and holdout
CHALLENGER = GradientBoosting      # run in shadow and explained with SHAP
