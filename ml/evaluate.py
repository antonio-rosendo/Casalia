"""Walk-forward evaluation of every model against naive baselines.

For each test year T (development folds 2010-2021, frozen holdout 2022-2025):
  - test rows: forecast origins in year T;
  - train rows: only origins whose 12-month target was already observed at the
    start of T (target_date <= first test origin). This purge gap stops the
    model from training on prices that overlap the test period.
Models that need tuning or early stopping split their training rows the same
way, so no decision ever looks at test data.

Usage:  python evaluate.py            development folds -> reports/results.md
        python evaluate.py --holdout  also the frozen holdout -> reports/holdout.md
"""

import argparse
import copy
import random
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from features import FEATURES, SMALL_MARKETS, TARGET, load_dataset
from model import PricePredictor

SEED = 42
DEV_YEARS = range(2010, 2022)       # used to choose features, models and settings
HOLDOUT_YEARS = range(2022, 2026)   # frozen: scored once, after everything is fixed
REPORT_DIR = Path(__file__).parent / "reports"
N_BOOTSTRAP = 2000


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


# --------------------------------------------------------------------------
# Walk-forward loop
# --------------------------------------------------------------------------

def walk_forward(ds: pd.DataFrame, years) -> pd.DataFrame:
    """Return one row per (model, test origin) with prediction and actual."""
    rows = []
    for year in years:
        test_start = pd.Timestamp(year=year, month=1, day=1)
        test = ds[ds["date"].dt.year == year]
        train = purged_split(ds, test_start)
        if test.empty or train.empty:
            continue
        for model_cls in MODELS:
            model = model_cls().fit(train)
            pred = model.predict(test)
            rows.append(test.assign(model=model_cls.name, fold=year, pred=pred))
    return pd.concat(rows, ignore_index=True)


def summarise(preds: pd.DataFrame):
    p = preds.assign(
        abs_err_pp=lambda d: (d["pred"] - d[TARGET]).abs() * 100,
        abs_err_price_pct=lambda d: (d["base_price"] * (1 + d["pred"]) - d["target_price"]).abs()
        / d["target_price"] * 100,
        right_direction=lambda d: np.sign(d["pred"]) == np.sign(d[TARGET]),
    )
    by_fold = p.groupby(["model", "fold"])["abs_err_pp"].mean().unstack("fold")
    momentum = by_fold.loc[Momentum.name]

    rng = np.random.default_rng(SEED)
    out = []
    for name, g in p.groupby("model"):
        diff_by_fold = (by_fold.loc[name] - momentum).to_numpy()
        boots = [rng.choice(diff_by_fold, size=len(diff_by_fold)).mean() for _ in range(N_BOOTSTRAP)]
        out.append({
            "Model": name,
            "MAE (pp of change)": g["abs_err_pp"].mean(),
            "MAE std across years": by_fold.loc[name].std(),
            "Price error (%)": g["abs_err_price_pct"].mean(),
            # A flat forecast never states a direction, so the metric does not apply.
            "Right direction (%)": np.nan if name == NoChange.name else g["right_direction"].mean() * 100,
            "Years better than momentum": int((diff_by_fold < 0).sum()),
            "vs momentum, 95% CI (pp)": f"[{np.percentile(boots, 2.5):+.2f}, {np.percentile(boots, 97.5):+.2f}]",
        })
    order = [m.name for m in MODELS]
    table = pd.DataFrame(out).set_index("Model").loc[order]
    return table, by_fold.loc[order]


def plot_regions(preds: pd.DataFrame, model_name: str, regions, path: Path) -> None:
    fig, axes = plt.subplots(len(regions), 1, figsize=(9, 2.6 * len(regions)), sharex=True)
    for ax, region in zip(axes, regions):
        r = preds[preds["region"] == region]
        actual = r[r["model"] == Momentum.name].set_index("date")[TARGET] * 100
        ax.plot(actual.index, actual, color="black", lw=2, label="Actual")
        for name, style in [(Momentum.name, ":"), (model_name, "-")]:
            s = r[r["model"] == name].set_index("date")["pred"] * 100
            ax.plot(s.index, s, style, label=name)
        ax.axhline(0, color="grey", lw=0.5)
        ax.set_title(r["name"].iloc[0], loc="left", fontsize=10)
        ax.set_ylabel("12-month change (%)")
    axes[0].legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def fmt(table: pd.DataFrame) -> str:
    return table.to_markdown(floatfmt=".2f").replace(" nan ", " n/a ")


def report(preds: pd.DataFrame, title: str, intro: str, figure_name: str) -> str:
    main_set = preds[~preds["region"].isin(SMALL_MARKETS)]
    small_set = preds[preds["region"].isin(SMALL_MARKETS)]
    table, by_fold = summarise(main_set)
    small_table, _ = summarise(small_set)

    (REPORT_DIR / "figures").mkdir(parents=True, exist_ok=True)
    candidates = table.drop([NoChange.name, Momentum.name, HistoricalMean.name])
    best_model = candidates["MAE (pp of change)"].idxmin()
    plot_regions(main_set, best_model, ["madrid", "cataluna", "andalucia"],
                 REPORT_DIR / "figures" / figure_name)

    n_regions = main_set["region"].nunique()
    return "\n".join([
        f"# {title}",
        "",
        f"Test years {by_fold.columns.min()}-{by_fold.columns.max()} ({by_fold.shape[1]} folds), "
        f"{n_regions} regions, {len(main_set) // len(MODELS)} forecasts per model. {intro}",
        "",
        "Lower MAE is better. 'vs momentum' is the mean yearly difference in MAE against the "
        "momentum baseline, with a 95% bootstrap interval over years; negative means better "
        "than momentum.",
        "",
        fmt(table),
        "",
        "## MAE by test year (pp of change)",
        "",
        fmt(by_fold),
        "",
        "## Ceuta and Melilla (reported apart: tiny, noisy markets)",
        "",
        fmt(small_table[["MAE (pp of change)", "Right direction (%)"]]),
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--holdout", action="store_true",
        help="also score the frozen 2022-2025 holdout (run once, after choosing the protocol)",
    )
    args = parser.parse_args()

    set_seed()
    ds = load_dataset()
    REPORT_DIR.mkdir(exist_ok=True)

    dev = walk_forward(ds, DEV_YEARS)
    dev.to_csv(REPORT_DIR / "walk_forward_predictions.csv", index=False)
    text = report(dev, "Walk-forward results (development folds)",
                  "Each fold trains only on targets observed before the test year starts.",
                  "predictions_vs_actual.png")
    (REPORT_DIR / "results.md").write_text(text, encoding="utf-8")
    print(text)

    if args.holdout:
        hold = walk_forward(ds, HOLDOUT_YEARS)
        hold.to_csv(REPORT_DIR / "holdout_predictions.csv", index=False)
        text = report(hold, "Frozen holdout (2022-2026)",
                      "Scored once, after the features, models and settings were fixed on the "
                      "development folds.",
                      "holdout_predictions_vs_actual.png")
        (REPORT_DIR / "holdout.md").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
