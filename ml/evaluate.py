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
BLOCK_YEARS = 2        # bootstrap block length: adjacent years share overlapping targets
FLAT_BAND = 0.01      # |12-month change| below 1 pp counts as "flat" for direction metrics


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


# --------------------------------------------------------------------------
# Walk-forward loop
# --------------------------------------------------------------------------

def walk_forward(ds: pd.DataFrame, years):
    """Return predictions (one row per model and test origin) and the settings
    each tuned model chose in each fold."""
    rows, settings = [], []
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
            chosen = getattr(model, "alpha_", None) or getattr(model, "setting_", None)
            if chosen is not None:
                settings.append({"model": model_cls.name, "fold": year, "setting": str(chosen)})
    return pd.concat(rows, ignore_index=True), pd.DataFrame(settings)


def direction(x) -> np.ndarray:
    """+1 up, -1 down, 0 flat (inside the +/- FLAT_BAND band)."""
    x = np.asarray(x)
    return np.where(x > FLAT_BAND, 1, np.where(x < -FLAT_BAND, -1, 0))


def balanced_direction_accuracy(pred, actual) -> float:
    """Mean recall over the direction classes that actually occurred, so a model
    cannot score well just by always saying "up" in a rising market."""
    p, a = direction(pred), direction(actual)
    recalls = [np.mean(p[a == c] == c) for c in (-1, 0, 1) if np.any(a == c)]
    return float(np.mean(recalls)) * 100


def block_bootstrap_ci(diffs: np.ndarray, rng) -> str:
    """95% interval for the mean yearly difference, resampling blocks of
    BLOCK_YEARS consecutive years (circular) to respect their correlation."""
    n = len(diffs)
    n_blocks = int(np.ceil(n / BLOCK_YEARS))
    means = []
    for _ in range(N_BOOTSTRAP):
        starts = rng.integers(0, n, size=n_blocks)
        idx = np.concatenate([(np.arange(BLOCK_YEARS) + s) % n for s in starts])[:n]
        means.append(diffs[idx].mean())
    return f"[{np.percentile(means, 2.5):+.2f}, {np.percentile(means, 97.5):+.2f}]"


def summarise(preds: pd.DataFrame, with_ci: bool):
    p = preds.assign(
        abs_err_pp=lambda d: (d["pred"] - d[TARGET]).abs() * 100,
        abs_err_price_pct=lambda d: (d["base_price"] * (1 + d["pred"]) - d["target_price"]).abs()
        / d["target_price"] * 100,
    )
    by_fold = p.groupby(["model", "fold"])["abs_err_pp"].mean().unstack("fold")
    momentum = by_fold.loc[Momentum.name]

    rng = np.random.default_rng(SEED)
    out = []
    for name, g in p.groupby("model"):
        diffs = (by_fold.loc[name] - momentum).to_numpy()
        row = {
            "Model": name,
            "MAE (pp of change)": g["abs_err_pp"].mean(),
            "MAE std across years": by_fold.loc[name].std(),
            "Price error (%)": g["abs_err_price_pct"].mean(),
            # A flat forecast never states a direction, so the metric does not apply.
            "Balanced direction accuracy (%)": np.nan if name == NoChange.name
            else balanced_direction_accuracy(g["pred"], g[TARGET]),
            "Years better than momentum": f"{int((diffs < 0).sum())} of {len(diffs)}",
        }
        if with_ci:
            row["vs momentum, 95% block-bootstrap CI (pp)"] = block_bootstrap_ci(diffs, rng)
        out.append(row)
    order = [m.name for m in MODELS]
    table = pd.DataFrame(out).set_index("Model").loc[order]
    return table, by_fold.loc[order]


def base_rates(preds: pd.DataFrame) -> str:
    actual = direction(preds.drop_duplicates(["region", "date"])[TARGET])
    up, flat, down = (np.mean(actual == c) * 100 for c in (1, 0, -1))
    return (f"Actual 12-month change: up (> +1 pp) in {up:.0f}% of forecasts, "
            f"flat in {flat:.0f}%, down in {down:.0f}%.")


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


def report(preds: pd.DataFrame, settings: pd.DataFrame, title: str, intro: str,
           figure_name: str, with_ci: bool) -> str:
    main_set = preds[~preds["region"].isin(SMALL_MARKETS)]
    small_set = preds[preds["region"].isin(SMALL_MARKETS)]
    table, by_fold = summarise(main_set, with_ci)
    small_table, _ = summarise(small_set, with_ci=False)

    (REPORT_DIR / "figures").mkdir(parents=True, exist_ok=True)
    # Always plot the candidate frozen on the development folds, never a model
    # picked by looking at the results being plotted.
    plot_regions(main_set, CANDIDATE, ["madrid", "cataluna", "andalucia"],
                 REPORT_DIR / "figures" / figure_name)

    if with_ci:
        uncertainty = (
            "'vs momentum' is the mean yearly difference in MAE against the momentum baseline "
            "(negative = better), with a 95% bootstrap interval that resamples blocks of "
            f"{BLOCK_YEARS} consecutive years."
        )
    else:
        uncertainty = (
            "With only a few test years no confidence interval is reported: read the per-year "
            "table and the count of years better than momentum."
        )
    chosen = (settings.pivot(index="model", columns="fold", values="setting")
              if not settings.empty else pd.DataFrame())
    n_regions = main_set["region"].nunique()
    return "\n".join([
        f"# {title}",
        "",
        f"{n_regions} regions, {len(main_set) // len(MODELS)} forecasts per model. {intro}",
        "",
        f"Lower MAE is better. {uncertainty} {base_rates(main_set)} Direction accuracy is "
        "balanced across up / flat / down, so always predicting 'up' does not score well.",
        "",
        fmt(table),
        "",
        "## MAE by test year (pp of change)",
        "",
        fmt(by_fold),
        "",
        "## Settings chosen by inner validation in each fold",
        "",
        "Ridge: regularisation strength alpha. Gradient boosting: (max_depth, max_iter).",
        "",
        chosen.to_markdown() if not chosen.empty else "-",
        "",
        "## Ceuta and Melilla (reported apart: tiny, noisy markets)",
        "",
        fmt(small_table[["MAE (pp of change)", "Balanced direction accuracy (%)"]]),
        "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--holdout", action="store_true",
        help="also report the frozen holdout (origins 2022-2025)",
    )
    args = parser.parse_args()

    set_seed()
    ds = load_dataset()
    REPORT_DIR.mkdir(exist_ok=True)

    dev, dev_settings = walk_forward(ds, DEV_YEARS)
    dev.to_csv(REPORT_DIR / "walk_forward_predictions.csv", index=False)
    text = report(dev, dev_settings, "Walk-forward results: development folds (origins 2010-2021)",
                  "Each fold trains only on targets observed before the test year starts.",
                  "predictions_vs_actual.png", with_ci=True)
    (REPORT_DIR / "results.md").write_text(text, encoding="utf-8")
    print(text)

    if args.holdout:
        hold, hold_settings = walk_forward(ds, HOLDOUT_YEARS)
        hold.to_csv(REPORT_DIR / "holdout_predictions.csv", index=False)
        text = report(hold, hold_settings,
                      "Frozen holdout: origins 2022-2025, targets up to 2026-Q2",
                      "Protocol frozen in commit fde3026 and first scored in commit 8758a6a; "
                      "later commits only change how results are reported, not the models "
                      "or features.",
                      "holdout_predictions_vs_actual.png", with_ci=False)
        (REPORT_DIR / "holdout.md").write_text(text, encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
