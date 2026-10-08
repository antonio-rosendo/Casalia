# Frozen holdout (2022-2026)

Test years 2022-2025 (4 folds), 17 regions, 238 forecasts per model. Scored once, after the features, models and settings were fixed on the development folds.

Lower MAE is better. 'vs momentum' is the mean yearly difference in MAE against the momentum baseline, with a 95% bootstrap interval over years; negative means better than momentum.

| Model                     |   MAE (pp of change) |   MAE std across years |   Price error (%) |   Right direction (%) |   Years better than momentum | vs momentum, 95% CI (pp)   |
|:--------------------------|---------------------:|-----------------------:|------------------:|----------------------:|-----------------------------:|:---------------------------|
| Baseline: no change       |                 7.51 |                   4.37 |              6.82 |                n/a    |                            0 | [+2.22, +7.58]             |
| Baseline: momentum        |                 3.40 |                   1.35 |              3.11 |                 99.58 |                            0 | [+0.00, +0.00]             |
| Baseline: historical mean |                 6.74 |                   4.09 |              6.12 |                100.00 |                            0 | [+1.62, +6.53]             |
| Ridge regression          |                 6.05 |                   3.77 |              5.49 |                100.00 |                            0 | [+1.06, +5.45]             |
| Gradient boosting         |                 6.24 |                   1.32 |              5.80 |                 50.42 |                            0 | [+1.06, +4.21]             |
| Neural network (MLP)      |                 7.72 |                   1.82 |              7.16 |                 61.76 |                            0 | [+2.88, +5.27]             |

## MAE by test year (pp of change)

| model                     |   2022 |   2023 |   2024 |   2025 |
|:--------------------------|-------:|-------:|-------:|-------:|
| Baseline: no change       |   3.72 |   5.46 |  10.53 |  13.12 |
| Baseline: momentum        |   2.50 |   2.24 |   5.09 |   4.09 |
| Baseline: historical mean |   3.23 |   4.74 |   9.64 |  11.96 |
| Ridge regression          |   2.65 |   4.30 |   8.90 |  10.67 |
| Gradient boosting         |   5.26 |   7.19 |   7.12 |   4.57 |
| Neural network (MLP)      |   5.94 |   7.88 |   9.99 |   6.41 |

## Ceuta and Melilla (reported apart: tiny, noisy markets)

| Model                     |   MAE (pp of change) |   Right direction (%) |
|:--------------------------|---------------------:|----------------------:|
| Baseline: no change       |                 5.01 |                n/a    |
| Baseline: momentum        |                 3.93 |                 78.57 |
| Baseline: historical mean |                 4.39 |                 89.29 |
| Ridge regression          |                 4.38 |                 78.57 |
| Gradient boosting         |                 5.79 |                 35.71 |
| Neural network (MLP)      |                 6.88 |                 57.14 |
