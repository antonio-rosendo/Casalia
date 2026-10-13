# Pre-registered diagnostic: why did the challenger miss 2022-2025?

Committed **before** running `diagnostics.py`. The results will be reported as they come out, whatever they show.

**Question.** In the frozen holdout, the challenger (gradient boosting) predicted far smaller rises than happened (MAE 6.24 pp against 3.40 for momentum). Which inputs drove its forecasts?

**Disclosure.** During the external review, a reviewer ran exploratory checks on the 2022 fold. They suggested that out-of-range inflation pushed the model's forecasts down, and that the Euribor did not. So this analysis is not blind to that idea. It tests both explanations under rules fixed in advance, on every fold.

## Analyses
They run on every development fold (2010-2021) and every holdout fold (2022-2025). Each fold's own model explains its own test rows.

1. **Grouped SHAP.** Interventional TreeSHAP, with that fold's training rows as background (a random sample of at most 300 rows, fixed seed). Contributions are summed by group:
   - momentum: `price_chg_12m`, `price_chg_3m`
   - inflation: `cpi_chg_12m`
   - rates: `euribor_12m`, `euribor_chg_12m`
   - labour: `unemployment_rate`, `unemployment_chg_12m`
   - credit: `mortgages_chg_12m`

   The output is the mean contribution of each group per test year, in pp of 12-month change.
2. **Group ablation.** Refit the challenger without each group, with the same tuning procedure, and report the change in MAE per test year.
3. **Out-of-range inputs.** For each group and test year, the share of test rows with a feature outside the training min-max range. Trees cannot extrapolate, so they treat such rows as the most extreme training case.

## Hypotheses and decision rule
- **H1 (inflation):** in a given holdout year, the challenger's forecasts were pulled down mainly by inflation.
- **H2 (rates):** in a given holdout year, they were pulled down mainly by the Euribor.

For each holdout year, a hypothesis is:
- **supported** if (a) its group has the most negative mean SHAP contribution among the five groups **and** (b) refitting without that group lowers that year's MAE by at least 0.5 pp;
- **partly supported** if only one of (a) and (b) holds;
- **not supported** otherwise.

## Caveats, stated in advance
- SHAP explains what the model did, not what moves the housing market.
- Correlated features share credit arbitrarily, which is why the groups exist.
- Ablation refits answer a different question ("would a model without this input have done better?") than SHAP ("what did this model rely on?"), so both are reported.
