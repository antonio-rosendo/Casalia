# Data

`processed/dataset.csv` is built by `ml/build_dataset.py` from the official sources below and committed as a snapshot, because the sources are revised over time. Snapshot downloaded on **2026-10-08**; it covers 1995-Q1 to 2026-Q2.

One row per region and quarter, for 17 autonomous communities plus Ceuta and Melilla.

| Column | Meaning | Source | Original frequency |
|---|---|---|---|
| `price_m2` | Mean appraised value of free-market housing, EUR/m² | Ministerio de Vivienda y Agenda Urbana (MIVAU), *Estadística de valor tasado de vivienda*, table 35101000 | Quarterly |
| `cpi` | Consumer price index, general, base 2021 (quarterly mean) | INE, IPC (Tempus3 API) | Monthly |
| `mortgages` | Number of mortgages on dwellings (quarterly sum) | INE, Estadística de Hipotecas (Tempus3 API) | Monthly |
| `unemployment_rate` | Unemployment rate, % | INE, Encuesta de Población Activa, table 65335 (Tempus3 API) | Quarterly |
| `euribor_12m` | 12-month Euribor, % (quarterly mean), same for every region | European Central Bank Data Portal, series `FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA` | Monthly |

Gaps kept as empty values:
- **Navarra 2015-2018:** the source marks the price as "n.r." (not representative).
- **Melilla 2013-Q3:** has no price.
- **Ceuta and Melilla:** start in 2004.
- **Before 2002-2003:** CPI, mortgages and unemployment have no data.

Rows that need a missing value are left out of the model.

## Reuse terms
All three publishers allow reuse of their statistics as long as the source is acknowledged:
- **INE:** aviso legal.
- **MIVAU:** Spanish public sector information reuse law, Ley 37/2007.
- **European Central Bank:** statistics reuse policy.

This file is that acknowledgement.

## Legacy data
`raw/datos_unidos_meses.csv` is the dataset used by the original May 2026 version (tag `v1.0-tfg`). Its source is undocumented, and its values do not match the official series above. For example, Madrid 2003-Q1 is 1,790 EUR/m² there and 1,936.9 in MIVAU. It is kept only so that version can still run.
