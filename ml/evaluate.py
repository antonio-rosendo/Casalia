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
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from features import SMALL_MARKETS, TARGET, load_dataset
from models import (CANDIDATE, MODELS, SEED, HistoricalMean, Momentum, NoChange,
                    purged_split, set_seed)

DEV_YEARS = range(2010, 2022)       # used to choose features, models and settings
HOLDOUT_YEARS = range(2022, 2026)   # frozen: scored once, after everything is fixed
REPORT_DIR = Path(__file__).parent / "reports"
N_BOOTSTRAP = 2000
BLOCK_YEARS = 2        # bootstrap block length: adjacent years share overlapping targets
FLAT_BAND = 0.01      # |12-month change| below 1 pp counts as "flat" for direction metrics




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
