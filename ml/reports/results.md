# Walk-forward results: development folds (origins 2010-2021)

17 regions, 792 forecasts per model. Each fold trains only on targets observed before the test year starts.

Lower MAE is better. 'vs momentum' is the mean yearly difference in MAE against the momentum baseline (negative = better), with a 95% bootstrap interval that resamples blocks of 2 consecutive years. Actual 12-month change: up (> +1 pp) in 36% of forecasts, flat in 20%, down in 43%. Direction accuracy is balanced across up / flat / down, so always predicting 'up' does not score well.

| Model                     |   MAE (pp of change) |   MAE std across years |   Price error (%) |   Balanced direction accuracy (%) | Years better than momentum   | vs momentum, 95% block-bootstrap CI (pp)   |
|:--------------------------|---------------------:|-----------------------:|------------------:|----------------------------------:|:-----------------------------|:-------------------------------------------|
| Baseline: no change       |                 3.63 |                   2.08 |              3.76 |                            n/a    | 5 of 12                      | [-0.88, +1.57]                             |
| Baseline: momentum        |                 3.35 |                   1.06 |              3.40 |                             48.23 | 0 of 12                      | [+0.00, +0.00]                             |
| Baseline: historical mean |                 4.44 |                   3.41 |              4.63 |                             31.94 | 5 of 12                      | [-0.82, +3.40]                             |
| Ridge regression          |                 4.72 |                   4.08 |              4.91 |                             39.22 | 4 of 12                      | [-0.59, +3.83]                             |
| Gradient boosting         |                 3.66 |                   1.26 |              3.72 |                             40.98 | 4 of 12                      | [-0.29, +0.91]                             |
| Neural network (MLP)      |                 5.56 |                   3.58 |              5.74 |                             43.28 | 4 of 12                      | [+0.14, +4.56]                             |

## MAE by test year (pp of change)

| model                     |   2010 |   2011 |   2012 |   2013 |   2014 |   2015 |   2016 |   2017 |   2018 |   2019 |   2020 |   2021 |
|:--------------------------|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
| Baseline: no change       |   5.36 |   7.84 |   6.82 |   3.58 |   1.86 |   2.08 |   2.00 |   2.61 |   2.60 |   1.48 |   2.45 |   4.37 |
| Baseline: momentum        |   3.39 |   3.59 |   4.90 |   5.00 |   4.09 |   2.27 |   1.89 |   2.02 |   2.15 |   3.70 |   3.68 |   3.28 |
| Baseline: historical mean |   9.77 |  11.11 |   8.50 |   4.28 |   1.80 |   2.08 |   1.99 |   2.54 |   2.45 |   1.68 |   2.21 |   4.02 |
| Ridge regression          |  16.25 |   6.69 |   7.48 |   3.46 |   2.12 |   4.83 |   2.21 |   2.38 |   2.23 |   1.96 |   2.72 |   3.58 |
| Gradient boosting         |   4.57 |   5.54 |   4.53 |   3.22 |   5.29 |   2.29 |   2.38 |   2.89 |   2.26 |   2.98 |   2.71 |   5.07 |
| Neural network (MLP)      |   7.93 |  13.30 |   9.99 |   2.90 |   3.28 |   8.21 |   3.82 |   2.29 |   1.99 |   3.79 |   2.94 |   5.66 |

## Settings chosen by inner validation in each fold

Ridge: regularisation strength alpha. Gradient boosting: (max_depth, max_iter).

| model             | 2010     | 2011     | 2012     | 2013     | 2014     | 2015     | 2016     | 2017     | 2018     | 2019     | 2020     | 2021     |
|:------------------|:---------|:---------|:---------|:---------|:---------|:---------|:---------|:---------|:---------|:---------|:---------|:---------|
| Gradient boosting | (3, 300) | (2, 300) | (2, 100) | (2, 100) | (3, 100) | (3, 100) | (2, 300) | (2, 300) | (2, 300) | (2, 100) | (2, 100) | (2, 100) |
| Ridge regression  | 10.0     | 0.1      | 10000.0  | 10000.0  | 100.0    | 10.0     | 1000.0   | 10000.0  | 10000.0  | 10000.0  | 1000.0   | 10000.0  |

## Ceuta and Melilla (reported apart: tiny, noisy markets)

| Model                     |   MAE (pp of change) |   Balanced direction accuracy (%) |
|:--------------------------|---------------------:|----------------------------------:|
| Baseline: no change       |                 3.08 |                            n/a    |
| Baseline: momentum        |                 4.34 |                             27.75 |
| Baseline: historical mean |                 3.43 |                             32.96 |
| Ridge regression          |                 4.50 |                             28.97 |
| Gradient boosting         |                 3.90 |                             36.54 |
| Neural network (MLP)      |                 6.04 |                             34.79 |
