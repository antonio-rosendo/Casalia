# 80% prediction interval for the momentum forecast

Interval = momentum forecast + the 10th and 90th percentiles of momentum's past errors, using only errors already observable at the forecast origin (pooled over 17 regions). A well-calibrated 80% interval covers the actual value about 80% of the time. Lower interval score is better (width plus a penalty for misses).

## Choosing the look-back window (development years 2010-2021 only)

|              |   Coverage (%) |   Mean width (pp) |   Interval score (pp) |
|:-------------|---------------:|------------------:|----------------------:|
| all history  |           85.9 |              13.9 |                  17.7 |
| last 5 years |           78.0 |              12.0 |                  17.8 |
| last 3 years |           75.5 |              11.2 |                  17.3 |

Chosen: **last 5 years**.

## Coverage by year with the chosen window

2022-2025 is the holdout period. It was already seen when this interval was designed, so its coverage is reported but is not a blind test.

|   year |   coverage |   width_pp |
|-------:|-----------:|-----------:|
|   2010 |       91.2 |       14.0 |
|   2011 |       94.1 |       15.1 |
|   2012 |       67.6 |       14.7 |
|   2013 |       64.7 |       15.6 |
|   2014 |       90.6 |       14.1 |
|   2015 |       96.9 |       13.3 |
|   2016 |       96.9 |       12.4 |
|   2017 |       93.8 |       11.3 |
|   2018 |       84.4 |        9.5 |
|   2019 |       42.2 |        8.3 |
|   2020 |       50.0 |        7.6 |
|   2021 |       66.2 |        8.2 |
|   2022 |       83.8 |        9.4 |
|   2023 |       92.6 |        9.8 |
|   2024 |       50.0 |        9.8 |
|   2025 |       76.5 |        9.7 |

## Holdout 2022-2025 (already seen)

|              |   Coverage (%) |   Mean width (pp) |   Interval score (pp) |
|:-------------|---------------:|------------------:|----------------------:|
| last 5 years |           75.6 |               9.7 |                  13.8 |
