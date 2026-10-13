# Diagnostic of the challenger (pre-registered)

Plan and decision rule: [diagnostics_plan.md](diagnostics_plan.md), committed before this script was run. Models are trained and tested on the 17 main regions (evaluate.py also trains on Ceuta and Melilla, so yearly MAEs differ slightly from holdout.md); each fold's own model explains its own test rows.

## Verdicts on the holdout years

|   year | hypothesis     | (a) most negative SHAP group   |   (b) MAE gain without group (pp) | verdict          |
|-------:|:---------------|:-------------------------------|----------------------------------:|:-----------------|
|   2022 | H1 (inflation) | inflation                      |                              1.64 | supported        |
|   2022 | H2 (rates)     | inflation                      |                             -2.03 | not supported    |
|   2023 | H1 (inflation) | rates                          |                              0.33 | not supported    |
|   2023 | H2 (rates)     | rates                          |                              1.35 | supported        |
|   2024 | H1 (inflation) | rates                          |                              0.03 | not supported    |
|   2024 | H2 (rates)     | rates                          |                              0.29 | partly supported |
|   2025 | H1 (inflation) | credit                         |                             -0.42 | not supported    |
|   2025 | H2 (rates)     | credit                         |                             -2.52 | not supported    |

## Mean SHAP contribution by feature group (pp of 12-month change)

Negative = the group pushed the forecast down relative to the model's average forecast.

|   year |   momentum |   inflation |   rates |   labour |   credit |
|-------:|-----------:|------------:|--------:|---------:|---------:|
|   2010 |      -6.97 |       +0.27 |   +2.10 |    +0.30 |    -0.02 |
|   2011 |      -7.57 |       +0.30 |   +1.71 |    +0.07 |    -0.31 |
|   2012 |      -7.63 |       -0.05 |   +0.56 |    -0.40 |    -0.42 |
|   2013 |      -6.64 |       +0.75 |   +0.44 |    -0.75 |    -0.28 |
|   2014 |      -5.85 |       +1.30 |   +0.23 |    -0.01 |    +0.12 |
|   2015 |      -4.37 |       +1.76 |   +1.46 |    -0.03 |    +0.22 |
|   2016 |      -2.53 |       +1.73 |   +1.48 |    +0.94 |    +0.17 |
|   2017 |      -2.39 |       -0.25 |   +0.72 |    +0.68 |    +0.33 |
|   2018 |      -1.27 |       +0.22 |   +1.93 |    +0.87 |    +0.39 |
|   2019 |      -1.30 |       +0.51 |   +1.75 |    +0.41 |    +0.41 |
|   2020 |      -2.88 |       +0.59 |   +1.64 |    -0.26 |    +0.14 |
|   2021 |      -2.08 |       -0.55 |   +0.70 |    +0.17 |    +0.51 |
|   2022 |      -0.08 |       -2.46 |   +0.42 |    +0.18 |    +0.19 |
|   2023 |      -0.23 |       -0.43 |   -2.18 |    +0.09 |    -0.36 |
|   2024 |      +2.32 |       -0.04 |   -0.90 |    +0.11 |    +0.34 |
|   2025 |      +6.07 |       +0.31 |   +2.27 |    +0.49 |    -0.10 |

## Ablation: MAE change when refitting without each group (pp)

Positive = the model was better without that group. 'MAE all features' is the MAE of this diagnostic's model in that year.

|   year |   MAE all features |   without momentum |   without inflation |   without rates |   without labour |   without credit |
|-------:|-------------------:|-------------------:|--------------------:|----------------:|-----------------:|-----------------:|
|   2010 |               5.21 |              -7.70 |                0.80 |            1.59 |             1.85 |             0.50 |
|   2011 |               5.24 |             -11.59 |               -0.63 |            1.16 |             0.07 |             0.17 |
|   2012 |               4.27 |              -0.08 |               -0.09 |           -0.04 |             0.08 |            -0.01 |
|   2013 |               3.28 |               0.22 |               -0.51 |           -0.08 |             0.36 |             0.09 |
|   2014 |               4.91 |               0.37 |               -1.03 |            0.55 |            -0.23 |            -0.89 |
|   2015 |               2.39 |              -2.02 |               -0.62 |            0.29 |             0.16 |            -0.15 |
|   2016 |               2.58 |               0.47 |                0.12 |            0.29 |             0.04 |            -0.16 |
|   2017 |               3.36 |               0.78 |                1.23 |            0.11 |            -0.79 |            -0.34 |
|   2018 |               2.17 |              -0.13 |               -0.06 |           -0.40 |            -0.23 |            -0.17 |
|   2019 |               3.27 |               0.68 |                0.14 |            0.46 |            -0.12 |            -0.12 |
|   2020 |               2.77 |              -0.68 |               -0.39 |           -1.07 |             0.38 |            -0.43 |
|   2021 |               5.15 |               0.65 |                0.42 |           -0.73 |            -0.02 |            -0.44 |
|   2022 |               5.17 |               0.43 |                1.64 |           -2.03 |             0.09 |             0.49 |
|   2023 |               7.86 |               2.81 |                0.33 |            1.35 |             0.62 |             1.14 |
|   2024 |               7.80 |               4.18 |                0.03 |            0.29 |            -0.21 |            -0.61 |
|   2025 |               3.54 |              -3.06 |               -0.42 |           -2.52 |            -0.60 |             1.15 |

## Test rows with inputs outside the training range (%)

|   year |   momentum |   inflation |   rates |   labour |   credit |
|-------:|-----------:|------------:|--------:|---------:|---------:|
|   2010 |          0 |           0 |     100 |       12 |        0 |
|   2011 |          1 |           0 |       0 |       13 |        0 |
|   2012 |          3 |           0 |      50 |       19 |        1 |
|   2013 |          1 |           0 |     100 |       16 |        0 |
|   2014 |          0 |           0 |     100 |        3 |        0 |
|   2015 |          0 |           0 |     100 |        6 |        2 |
|   2016 |          0 |           0 |     100 |        3 |        0 |
|   2017 |          0 |           0 |     100 |        2 |        0 |
|   2018 |          0 |           0 |     100 |        0 |        0 |
|   2019 |          0 |           0 |      50 |        0 |        0 |
|   2020 |          0 |           0 |      75 |        0 |        0 |
|   2021 |          0 |          16 |     100 |        0 |        6 |
|   2022 |          0 |         100 |      50 |        3 |        1 |
|   2023 |          0 |           0 |      75 |        0 |        0 |
|   2024 |          0 |           0 |       0 |        0 |        0 |
|   2025 |          0 |           0 |       0 |        0 |        0 |
