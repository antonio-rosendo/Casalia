# Walk-forward results (development folds)

Test years 2010-2021 (12 folds), 17 regions, 792 forecasts per model. Each fold trains only on targets observed before the test year starts.

Lower MAE is better. 'vs momentum' is the mean yearly difference in MAE against the momentum baseline, with a 95% bootstrap interval over years; negative means better than momentum.

| Model                     |   MAE (pp of change) |   MAE std across years |   Price error (%) |   Right direction (%) |   Years better than momentum | vs momentum, 95% CI (pp)   |
|:--------------------------|---------------------:|-----------------------:|------------------:|----------------------:|-----------------------------:|:---------------------------|
| Baseline: no change       |                 3.63 |                   2.08 |              3.76 |                n/a    |                            5 | [-0.77, +1.30]             |
| Baseline: momentum        |                 3.35 |                   1.06 |              3.40 |                 64.77 |                            0 | [+0.00, +0.00]             |
| Baseline: historical mean |                 4.44 |                   3.41 |              4.63 |                 45.96 |                            5 | [-0.55, +2.90]             |
| Ridge regression          |                 4.72 |                   4.08 |              4.91 |                 53.03 |                            4 | [-0.43, +3.80]             |
| Gradient boosting         |                 3.66 |                   1.26 |              3.72 |                 56.94 |                            4 | [-0.35, +0.91]             |
| Neural network (MLP)      |                 5.56 |                   3.58 |              5.74 |                 55.05 |                            4 | [+0.35, +4.17]             |

## MAE by test year (pp of change)

| model                     |   2010 |   2011 |   2012 |   2013 |   2014 |   2015 |   2016 |   2017 |   2018 |   2019 |   2020 |   2021 |
|:--------------------------|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
| Baseline: no change       |   5.36 |   7.84 |   6.82 |   3.58 |   1.86 |   2.08 |   2.00 |   2.61 |   2.60 |   1.48 |   2.45 |   4.37 |
| Baseline: momentum        |   3.39 |   3.59 |   4.90 |   5.00 |   4.09 |   2.27 |   1.89 |   2.02 |   2.15 |   3.70 |   3.68 |   3.28 |
| Baseline: historical mean |   9.77 |  11.11 |   8.50 |   4.28 |   1.80 |   2.08 |   1.99 |   2.54 |   2.45 |   1.68 |   2.21 |   4.02 |
| Ridge regression          |  16.25 |   6.69 |   7.48 |   3.46 |   2.12 |   4.83 |   2.21 |   2.38 |   2.23 |   1.96 |   2.72 |   3.58 |
| Gradient boosting         |   4.57 |   5.54 |   4.53 |   3.22 |   5.29 |   2.29 |   2.38 |   2.89 |   2.26 |   2.98 |   2.71 |   5.07 |
| Neural network (MLP)      |   7.93 |  13.30 |   9.99 |   2.90 |   3.28 |   8.21 |   3.82 |   2.29 |   1.99 |   3.79 |   2.94 |   5.66 |

## Ceuta and Melilla (reported apart: tiny, noisy markets)

| Model                     |   MAE (pp of change) |   Right direction (%) |
|:--------------------------|---------------------:|----------------------:|
| Baseline: no change       |                 3.08 |                n/a    |
| Baseline: momentum        |                 4.34 |                 51.09 |
| Baseline: historical mean |                 3.43 |                 60.87 |
| Ridge regression          |                 4.50 |                 52.17 |
| Gradient boosting         |                 3.90 |                 56.52 |
| Neural network (MLP)      |                 6.04 |                 54.35 |
