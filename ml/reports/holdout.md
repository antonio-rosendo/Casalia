# Frozen holdout: origins 2022-2025, targets up to 2026-Q2

17 regions, 238 forecasts per model. Protocol frozen in commit fde3026 and first scored in commit 8758a6a; later commits only change how results are reported, not the models or features.

Lower MAE is better. With only a few test years no confidence interval is reported: read the per-year table and the count of years better than momentum. Actual 12-month change: up (> +1 pp) in 96% of forecasts, flat in 4%, down in 0%. Direction accuracy is balanced across up / flat / down, so always predicting 'up' does not score well.

| Model                     |   MAE (pp of change) |   MAE std across years |   Price error (%) |   Balanced direction accuracy (%) | Years better than momentum   |
|:--------------------------|---------------------:|-----------------------:|------------------:|----------------------------------:|:-----------------------------|
| Baseline: no change       |                 7.51 |                   4.37 |              6.82 |                            n/a    | 0 of 4                       |
| Baseline: momentum        |                 3.40 |                   1.35 |              3.11 |                             47.15 | 0 of 4                       |
| Baseline: historical mean |                 6.74 |                   4.09 |              6.12 |                             57.46 | 0 of 4                       |
| Ridge regression          |                 6.05 |                   3.77 |              5.49 |                             52.98 | 0 of 4                       |
| Gradient boosting         |                 6.24 |                   1.32 |              5.80 |                             32.37 | 0 of 4                       |
| Neural network (MLP)      |                 7.72 |                   1.82 |              7.16 |                             26.97 | 0 of 4                       |

## MAE by test year (pp of change)

| model                     |   2022 |   2023 |   2024 |   2025 |
|:--------------------------|-------:|-------:|-------:|-------:|
| Baseline: no change       |   3.72 |   5.46 |  10.53 |  13.12 |
| Baseline: momentum        |   2.50 |   2.24 |   5.09 |   4.09 |
| Baseline: historical mean |   3.23 |   4.74 |   9.64 |  11.96 |
| Ridge regression          |   2.65 |   4.30 |   8.90 |  10.67 |
| Gradient boosting         |   5.26 |   7.19 |   7.12 |   4.57 |
| Neural network (MLP)      |   5.94 |   7.88 |   9.99 |   6.41 |

## Settings chosen by inner validation in each fold

Ridge: regularisation strength alpha. Gradient boosting: (max_depth, max_iter).

| model             | 2022     | 2023     | 2024     | 2025     |
|:------------------|:---------|:---------|:---------|:---------|
| Gradient boosting | (3, 100) | (3, 100) | (3, 300) | (3, 300) |
| Ridge regression  | 10000.0  | 10000.0  | 10000.0  | 10000.0  |

## Ceuta and Melilla (reported apart: tiny, noisy markets)

| Model                     |   MAE (pp of change) |   Balanced direction accuracy (%) |
|:--------------------------|---------------------:|----------------------------------:|
| Baseline: no change       |                 5.01 |                            n/a    |
| Baseline: momentum        |                 3.93 |                             24.24 |
| Baseline: historical mean |                 4.39 |                             39.39 |
| Ridge regression          |                 4.38 |                             24.85 |
| Gradient boosting         |                 5.79 |                             23.94 |
| Neural network (MLP)      |                 6.88 |                             15.15 |
