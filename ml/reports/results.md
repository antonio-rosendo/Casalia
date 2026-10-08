# Walk-forward results

Test years 2010-2021 (12 folds), 16 regions (720 forecasts per model). Each fold trains only on targets observed before the test year starts.

Lower MAE is better. 'vs momentum' is the mean yearly difference in MAE against the momentum baseline, with a 95% bootstrap interval over years; negative means better than momentum.

| Model                     |   MAE (pp of change) |   MAE std across years |   Price error (%) |   Right direction (%) |   Years better than momentum | vs momentum, 95% CI (pp)   |
|:--------------------------|---------------------:|-----------------------:|------------------:|----------------------:|-----------------------------:|:---------------------------|
| Baseline: no change       |                 4.86 |                   2.62 |              5.13 |                n/a    |                            3 | [+0.52, +3.12]             |
| Baseline: momentum        |                 3.05 |                   0.72 |              3.13 |                 82.78 |                            0 | [+0.00, +0.00]             |
| Baseline: historical mean |                 6.18 |                   3.79 |              6.53 |                 24.03 |                            3 | [+1.11, +5.18]             |
| Ridge regression          |                 3.03 |                   1.03 |              3.09 |                 80.69 |                            8 | [-0.21, +0.32]             |
| Gradient boosting         |                 4.37 |                   1.62 |              4.47 |                 68.61 |                            1 | [+0.76, +2.06]             |
| Neural network (MLP)      |                 4.10 |                   1.45 |              4.21 |                 70.97 |                            2 | [+0.39, +1.90]             |

## MAE by test year (pp of change)

| model                     |   2010 |   2011 |   2012 |   2013 |   2014 |   2015 |   2016 |   2017 |   2018 |   2019 |   2020 |   2021 |
|:--------------------------|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
| Baseline: no change       |   5.21 |   8.21 |  10.48 |   7.68 |   4.52 |   3.16 |   2.66 |   3.12 |   3.24 |   2.56 |   2.50 |   5.21 |
| Baseline: momentum        |   2.47 |   3.38 |   3.34 |   3.30 |   4.02 |   3.43 |   2.96 |   2.95 |   2.29 |   2.08 |   2.93 |   4.67 |
| Baseline: historical mean |  10.81 |  11.88 |  12.78 |   8.47 |   4.15 |   2.77 |   2.79 |   4.09 |   4.28 |   3.20 |   2.91 |   5.62 |
| Ridge regression          |   2.19 |   3.14 |   2.79 |   4.01 |   4.00 |   3.06 |   3.75 |   2.99 |   2.10 |   1.87 |   2.72 |   5.58 |
| Gradient boosting         |   3.01 |   7.24 |   4.30 |   2.53 |   5.66 |   5.11 |   3.72 |   5.08 |   3.68 |   2.71 |   4.25 |   7.43 |
| Neural network (MLP)      |   4.62 |   4.45 |   4.05 |   7.84 |   2.90 |   3.22 |   3.28 |   3.95 |   3.13 |   3.00 |   4.13 |   6.08 |

## Ceuta and Melilla (reported apart: tiny, noisy markets)

| Model                     |   MAE (pp of change) |   Right direction (%) |
|:--------------------------|---------------------:|----------------------:|
| Baseline: no change       |                 2.47 |                n/a    |
| Baseline: momentum        |                 2.84 |                 65.56 |
| Baseline: historical mean |                 3.49 |                 40.00 |
| Ridge regression          |                 2.93 |                 62.22 |
| Gradient boosting         |                 3.22 |                 56.67 |
| Neural network (MLP)      |                 5.09 |                 48.89 |
