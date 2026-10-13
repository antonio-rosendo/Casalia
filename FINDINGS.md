# Findings

The numbers come from the reports in [ml/reports/](ml/reports/), which the scripts regenerate.

**In short**

- **The first version (v1)** had leakage, unverifiable data and no baseline, so its results meant little.
- **The rebuild** uses official data, a purged walk-forward evaluation, three naive baselines and a holdout frozen before scoring.
- **The result:** a momentum rule beat Ridge, gradient boosting and an MLP in development and in every holdout year. Gradient boosting came closest, within the margin of error in development.
- **What is served:** momentum with an empirical 80% range, plus gradient boosting in shadow mode with SHAP. The forecasts are logged in git before the outcome is known.

## 1. The first version and what was wrong with it

The May 2026 version (tag [`v1.0-tfg`](https://github.com/antonio-rosendo/Casalia/tree/v1.0-tfg)) trained a PyTorch MLP on a CSV of regional prices and macro data. It split the data once: training up to 2015, validation 2016-2018, test from 2019. Looking at it again in October 2026, I found these problems:

- **Unknown data.** Nobody could say where the CSV came from, and its prices did not match the official series. For example, Madrid 2003-Q1 was 1,790 EUR/m² in the file and 1,936.9 in the MIVAU table.
- **Leakage through interpolation.** Immigration is an annual figure, but the file had it rising in identical steps every quarter (Andalucía, 2003-Q1 to 2004-Q1: 205,704 → 213,822 → 221,941 → 230,060 → 238,178). Each quarter was interpolated towards the next year's value, so it contained information from the future.
- **No purge.** A row at the end of 2015 has its 12-month target in 2016, which is validation data. The single split did not remove those rows.
- **Features that cannot generalise:**
  - the calendar (year, month), which takes values in production that training never saw;
  - raw levels that trend over time (price, CPI, number of mortgages).
- **No baseline.** There was no way to tell whether the network beat anything simple.
- **Checkpoint bug.** `model.state_dict()` returns live references, so the "best" checkpoint changed after every epoch and the saved model was always the last one. Fixed with `copy.deepcopy` in [25761f3](https://github.com/antonio-rosendo/Casalia/commit/25761f3).

## 2. The rebuild

### Data

[`build_dataset.py`](ml/build_dataset.py) downloads:

| Source | Series |
|---|---|
| MIVAU table 35101000 | appraised value per m², by region, quarterly |
| INE (Tempus3 API) | CPI, mortgages on homes, EPA unemployment rate |
| ECB Data Portal | 12-month Euribor, monthly |

It builds a complete quarterly grid for 19 regions (17 plus Ceuta and Melilla). Missing quarters are explicit: MIVAU marks Navarra 2015-2018 as "n.r.", and Melilla 2013-Q3 is missing. The modelled data start in 2004, the first year every source is available.

### Features

There are eight, all built only from data up to the forecast quarter:
- the 12-month and 3-month price change;
- 12-month inflation;
- the log change in mortgages signed;
- the unemployment rate and its 12-month change;
- the Euribor and its 12-month change.

There are no calendar features and no trending levels. The target is the % change in price over the next four quarters.

MIVAU and the INE mortgage series come out about 2-3 months after each quarter ends. So forecasts are only made from quarters that every source has published.

### Evaluation protocol

- **Walk-forward by year.** To forecast year *t*, models are trained only on rows whose target quarter is no later than the first origin of year *t*. Every target was therefore already published when that forecast was made (the purge). Hyperparameters are chosen by averaging the error over the last three years inside the training window.
- **Development folds:** origins 2010-2021, used to choose features, models and settings.
- **Frozen holdout:** origins 2022-2025, with targets up to 2026-Q2. The protocol was fixed in commit [fde3026](https://github.com/antonio-rosendo/Casalia/commit/fde3026), and the holdout was first scored in [8758a6a](https://github.com/antonio-rosendo/Casalia/commit/8758a6a).
- **Baselines:**
  - no change (0%);
  - momentum (the last 12 months' change);
  - the historical mean change, pooled over all regions in the training window.
- **Models:**
  - Ridge regression with standardised inputs (alpha from 0.1 to 10,000);
  - gradient boosting (scikit-learn `HistGradientBoostingRegressor`, depth 2-3, 100-300 trees);
  - an MLP in PyTorch (32-16 hidden units, Adam, weight decay, early stopping, fixed seeds).
- **Metrics:**
  - mean absolute error of the change, in percentage points;
  - direction accuracy (up, flat within ±1 pp, or down), balanced across the three classes and reported next to the base rates;
  - a 95% circular block bootstrap of each model's yearly gap to momentum, resampling two-year blocks because errors are correlated within and across nearby years.
- **Ceuta and Melilla** are tiny, noisy markets, so they are reported separately.

## 3. Results

### Development, origins 2010-2021 (792 forecasts per model)

| Model | MAE (pp) | Years better than momentum | Gap to momentum, 95% CI (pp) | Balanced direction accuracy |
|---|---:|---:|---|---:|
| Momentum | 3.35 | — | — | 48% |
| No change | 3.63 | 5 of 12 | −0.88 to +1.57 | n/a |
| Gradient boosting | 3.66 | 4 of 12 | −0.29 to +0.91 | 41% |
| Historical mean | 4.44 | 5 of 12 | −0.82 to +3.40 | 32% |
| Ridge regression | 4.72 | 4 of 12 | −0.59 to +3.83 | 39% |
| MLP | 5.56 | 4 of 12 | +0.14 to +4.56 | 43% |

The actual changes were up in 36% of cases, flat in 20% and down in 43%.
- **Gradient boosting** was the best trained model, so it became the challenger. Its gap to momentum is not significant.
- **Ridge** chose the largest alpha in half the development years and in all four holdout years. In practice it is little more than an average; the data hold little stable linear signal.

### Frozen holdout, origins 2022-2025 (238 forecasts per model)

| Model | 2022 | 2023 | 2024 | 2025 | MAE (pp) |
|---|---:|---:|---:|---:|---:|
| Momentum | 2.50 | 2.24 | 5.09 | 4.09 | **3.40** |
| Ridge regression | 2.65 | 4.30 | 8.90 | 10.67 | 6.05 |
| Gradient boosting | 5.26 | 7.19 | 7.12 | 4.57 | 6.24 |
| Historical mean | 3.23 | 4.74 | 9.64 | 11.96 | 6.74 |
| No change | 3.72 | 5.46 | 10.53 | 13.12 | 7.51 |
| MLP | 5.94 | 7.88 | 9.99 | 6.41 | 7.72 |

- **No model beat momentum** in any of the four years.
- **96% of the actual changes were rises,** so raw direction accuracy would be meaningless. The balanced version is in [holdout.md](ml/reports/holdout.md).
- **Ridge did slightly better than gradient boosting here.** The challenger had been chosen on development data before the holdout was scored, so it was not changed.

## 4. The 80% range

The range is the momentum forecast plus the 10th and 90th percentiles of momentum's past errors. It uses only errors already observable at the forecast origin, pooled across the 17 regions. The look-back window was chosen on development years only:

| Window | Coverage | Mean width (pp) | Interval score (pp) |
|---|---:|---:|---:|
| All history | 85.9% | 13.9 | 17.7 |
| Last 5 years (chosen) | 78.0% | 12.0 | 17.8 |
| Last 3 years | 75.5% | 11.2 | 17.3 |

The interval scores are within 0.5 pp of each other, and five years gives the coverage closest to 80%.

- **Holdout coverage was 75.6%.** The range was designed after the holdout had been seen, so this is not a blind test.
- **Coverage drops when the market changes direction or pace:** 42% in 2019, 50% in 2020 and 2024, and 65-68% in 2012-13 and 2021. In the steadier years (2010-11, 2014-18, 2022-23) it was 84-97%.
- **The current range sits mostly above the forecast,** because momentum has underestimated the recent rise.

## 5. What is served, and the forecast log

- **Main forecast (champion):** momentum, best in development and again in the holdout. It was also the best model on the development years alone, so the choice holds without the holdout.
- **ML forecast (challenger):** gradient boosting, run in shadow mode and explained with grouped TreeSHAP. The contributions plus the model's average add up to each forecast.
- **Replacing momentum:** a challenger takes over only if it beats momentum in the walk-forward evaluation with a 95% interval of the gap that excludes zero. Because the holdout has been seen, it must then also beat momentum on the forecast log. The rule is stated in [`models.py`](ml/models.py).
- **The forecast log:** each quarter's forecasts go to [ml/forecasts/](ml/forecasts/) and are never edited. [`score_forecasts.py`](ml/score_forecasts.py) scores them once MIVAU publishes the target quarter. The log is the project's only fully blind test.
  - The first entry, 2026-Q2 → 2027-Q2, is also marked by the release `forecast-2026-Q2`.
  - It predates the SHAP fields, which were added in [d3bea56](https://github.com/antonio-rosendo/Casalia/commit/d3bea56). Later entries will include them.

## 6. Why the models missed 2022-2025: a pre-registered diagnostic

The [plan](ml/reports/diagnostics_plan.md) was committed in [8ff61e3](https://github.com/antonio-rosendo/Casalia/commit/8ff61e3), before [`diagnostics.py`](ml/diagnostics.py) was run in [f303b86](https://github.com/antonio-rosendo/Casalia/commit/f303b86). It set two hypotheses, each saying that one group of inputs drove gradient boosting's forecasts down in a given holdout year:
- **H1:** inflation.
- **H2:** rates.

A hypothesis is *supported* if (a) its group has the most negative mean SHAP contribution and (b) refitting without that group cuts the year's MAE by at least 0.5 pp. It is *partly supported* if only one of (a) and (b) holds.

| Year | Verdict | Evidence |
|---|---|---|
| 2022 | H1 supported | Inflation SHAP −2.46 pp; refitting without it cut the MAE by 1.64 pp. Inflation ran at 5.7-12.1% against a training maximum of 5.6% (2008), so every row was out of range. |
| 2023 | H2 supported | Rates SHAP −2.18 pp; refitting without them cut the MAE by 1.35 pp. The Euribor rose up to 3.9 pp in a year, against at most 1.4 pp in training. |
| 2024 | H2 partly supported | Rates had the most negative SHAP, but refitting without them gained only 0.29 pp. Outside the hypotheses, refitting without the momentum inputs cut the error by 4.18 pp. |
| 2025 | Neither supported | Still unexplained. |

**Caveats:**
- **H1 was not tested blind.** The inflation hypothesis came from an earlier exploratory look at 2022, as the plan notes.
- **SHAP explains the model, not the market:** it shows what the model did, not what moves housing prices.
- **The diagnostic's model differs slightly from the evaluated one.** It trains on the 17 main regions, while `evaluate.py` also trains on Ceuta and Melilla. Its yearly MAEs therefore differ from the holdout table, by up to about 1 pp (2025).

## 7. How far to trust the holdout

- **Commit order, not proof.** Local commit times can be edited, so the freeze ([fde3026](https://github.com/antonio-rosendo/Casalia/commit/fde3026), four minutes before the first holdout score) and the diagnostic plan ([8ff61e3](https://github.com/antonio-rosendo/Casalia/commit/8ff61e3)) rest on commit order. The forecast log is dated independently by the GitHub release `forecast-2026-Q2`.
- **The holdout commit also changed `evaluate.py`,** but only to plot a fixed model rather than the best one. A later commit, [81e0ea3](https://github.com/antonio-rosendo/Casalia/commit/81e0ea3), re-ran the holdout to change how results were reported, and every MAE was identical.
- **Look-ahead through domain knowledge.** I chose the Euribor as a feature already knowing what happened in 2022-2025.
- **The holdout is now spent.** Any new method scored on 2022-2025 would be chosen with knowledge of those years, so new ideas will be judged on the forecast log.

## 8. Limits

- **Appraisals, not sales.** MIVAU's appraised values lag and smooth the market, which helps momentum. INE's transaction-based index (IPV) would be a harder and more realistic target.
- **Revised data.** The series are today's revised versions, not the vintages known at the time, so the backtest is pseudo out-of-sample.
- **Little data.**
  - Each fold trains on about 400 to 1,500 rows.
  - Rows from the same quarter share the same Euribor.
  - Consecutive targets overlap by nine months.
  - The effective number of independent episodes is small, which favours simple models.
- **Regional averages.** The site and the API apply the regional change to a user's figure. They know nothing about the home itself.

## 9. What I would try next

- **Learn the error of momentum** instead of the price, so a model corrects the baseline rather than replacing it. It would be judged on the forecast log only.
- **Add affordability and supply data:** price to income or rent, building permits, number of transactions.
- **Repeat the exercise on the IPV** (sale prices) and with real-time data vintages.
