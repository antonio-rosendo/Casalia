"""Build the quarterly regional dataset from official sources.

Sources (all public, reusable with attribution; see data/README.md):
- Ministerio de Vivienda y Agenda Urbana (MIVAU): appraised value of free-market
  housing, EUR/m2, quarterly, by autonomous community (Excel 35101000).
- INE (Tempus3 API): consumer price index by region (monthly), number of
  mortgages on dwellings by region (monthly) and unemployment rate by region
  (EPA, quarterly).
- European Central Bank (Data Portal API): 12-month Euribor (monthly).

Raw downloads are cached in data/raw/official/ so the build is repeatable
offline; pass --refresh to download again.

Usage:  python build_dataset.py [--refresh]
Output: data/processed/dataset.csv  (one row per region and quarter)
"""

import argparse
import io
import json
from datetime import date
from pathlib import Path

import pandas as pd
import requests

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "data" / "raw" / "official"
OUT_PATH = BASE_DIR / "data" / "processed" / "dataset.csv"

INE_URL = "https://servicios.ine.es/wstempus/js/ES"
MIVAU_URL = "https://apps.fomento.gob.es/BoletinOnline2/sedal/35101000.XLS"
ECB_URL = (
    "https://data-api.ecb.europa.eu/service/data/FM/"
    "M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA?format=csvdata"
)
EPA_TABLE = 65335  # unemployment rate by autonomous community

# region slug -> (name in the MIVAU Excel, name in the EPA table,
#                 INE CPI series, INE mortgages-on-dwellings series)
REGIONS = {
    "andalucia": ("Andalucía", "Andalucía", "IPC293660", "HPT62881"),
    "aragon": ("Aragón", "Aragón", "IPC293716", "HPT62879"),
    "asturias": ("Asturias (Principado de )", "Asturias, Principado de", "IPC293772", "HPT62877"),
    "baleares": ("Balears (Illes)", "Balears, Illes", "IPC293828", "HPT62875"),
    "canarias": ("Canarias", "Canarias", "IPC293884", "HPT62873"),
    "cantabria": ("Cantabria", "Cantabria", "IPC293940", "HPT62871"),
    "castilla_y_leon": ("Castilla y León", "Castilla y León", "IPC293996", "HPT62869"),
    "castilla_la_mancha": ("Castilla-La Mancha", "Castilla - La Mancha", "IPC294052", "HPT62867"),
    "cataluna": ("Cataluña", "Cataluña", "IPC294108", "HPT62865"),
    "comunitat_valenciana": ("Comunidad Valenciana", "Comunitat Valenciana", "IPC294164", "HPT62863"),
    "extremadura": ("Extremadura", "Extremadura", "IPC294220", "HPT62861"),
    "galicia": ("Galicia", "Galicia", "IPC294276", "HPT62859"),
    "madrid": ("Madrid (Comunidad de)", "Madrid, Comunidad de", "IPC294332", "HPT62857"),
    "murcia": ("Murcia (Región de)", "Murcia, Región de", "IPC294388", "HPT62855"),
    "navarra": ("Navarra (Comunidad Foral de)", "Navarra, Comunidad Foral de", "IPC294444", "HPT62853"),
    "pais_vasco": ("País Vasco", "País Vasco", "IPC294500", "HPT62851"),
    "rioja": ("Rioja (La)", "Rioja, La", "IPC294556", "HPT62849"),
    "ceuta": ("Ceuta", "Ceuta", "IPC294612", "HPT62847"),
    "melilla": ("Melilla", "Melilla", "IPC293604", "HPT62845"),
}


# --------------------------------------------------------------------------
# Download helpers (with cache)
# --------------------------------------------------------------------------

def _cached(name: str, fetch, refresh: bool) -> bytes:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / name
    if refresh or not path.exists():
        path.write_bytes(fetch())
    return path.read_bytes()


def _get(url: str, **params) -> bytes:
    resp = requests.get(url, params=params or None, timeout=60)
    resp.raise_for_status()
    return resp.content


def ine_series(code: str, refresh: bool) -> pd.DataFrame:
    """Full history of an INE series as (year, period, value)."""
    raw = _cached(
        f"ine_{code}.json",
        lambda: _get(f"{INE_URL}/DATOS_SERIE/{code}", date=f"19950101:{date.today():%Y%m%d}"),
        refresh,
    )
    data = json.loads(raw)["Data"]
    return pd.DataFrame(
        [(d["Anyo"], d["FK_Periodo"], d["Valor"]) for d in data if d["Valor"] is not None],
        columns=["year", "period", "value"],
    )


# --------------------------------------------------------------------------
# Sources
# --------------------------------------------------------------------------

def load_prices(refresh: bool) -> pd.DataFrame:
    """MIVAU appraised value (EUR/m2): one sheet per 4 years, one row per region."""
    raw = _cached("mivau_valor_tasado_35101000.xls", lambda: _get(MIVAU_URL), refresh)
    book = pd.read_excel(io.BytesIO(raw), sheet_name=None, header=None)
    name_to_slug = {v[0]: k for k, v in REGIONS.items()}
    rows = []
    for sheet in book.values():
        year_row = sheet.iloc[11]  # "Año 1995", "Año 1996", ...
        quarter_row = sheet.iloc[13]  # "1º", "2º", ...
        years = year_row.ffill()
        for _, r in sheet.iloc[14:].iterrows():
            slug = name_to_slug.get(str(r[1]).strip())
            if slug is None:
                continue
            for col in range(2, sheet.shape[1]):
                y, q, v = years[col], quarter_row[col], r[col]
                # Non-numeric cells such as "n.r" (not representative) are skipped.
                if (isinstance(y, str) and y.startswith("Año") and str(q)[:1].isdigit()
                        and isinstance(v, (int, float)) and pd.notna(v)):
                    rows.append((slug, int(y.split()[1]), int(str(q)[0]), float(v)))
    df = pd.DataFrame(rows, columns=["region", "year", "quarter", "price_m2"])
    return df.drop_duplicates(["region", "year", "quarter"])


def load_monthly_ine(column: str, index: int, how: str, refresh: bool) -> pd.DataFrame:
    """Monthly INE series aggregated to quarters ('mean' or 'sum'); full quarters only."""
    frames = []
    for slug, spec in REGIONS.items():
        s = ine_series(spec[index], refresh)
        s = s[s["period"].between(1, 12)]
        s["quarter"] = (s["period"] - 1) // 3 + 1
        g = s.groupby(["year", "quarter"])["value"]
        q = g.agg(how).where(g.count() == 3).dropna().reset_index()
        frames.append(q.assign(region=slug).rename(columns={"value": column}))
    return pd.concat(frames, ignore_index=True)


def load_unemployment(refresh: bool) -> pd.DataFrame:
    raw = _cached(f"ine_table_{EPA_TABLE}.json", lambda: _get(f"{INE_URL}/DATOS_TABLA/{EPA_TABLE}", nult=200), refresh)
    epa_to_slug = {v[1]: k for k, v in REGIONS.items()}
    rows = []
    for series in json.loads(raw):
        parts = [p.strip() for p in series["Nombre"].split(".")]
        # "Tasa de paro de la población. <Region>. Ambos sexos. Total."
        if len(parts) < 4 or parts[2] != "Ambos sexos" or parts[3] != "Total":
            continue
        slug = epa_to_slug.get(parts[1])
        if slug is None:
            continue
        for d in series["Data"]:
            if d["Valor"] is not None and 19 <= d["FK_Periodo"] <= 22:  # 19..22 = Q1..Q4
                rows.append((slug, d["Anyo"], d["FK_Periodo"] - 18, d["Valor"]))
    return pd.DataFrame(rows, columns=["region", "year", "quarter", "unemployment_rate"])


def load_euribor(refresh: bool) -> pd.DataFrame:
    raw = _cached("ecb_euribor_12m.csv", lambda: _get(ECB_URL), refresh)
    df = pd.read_csv(io.BytesIO(raw), usecols=["TIME_PERIOD", "OBS_VALUE"])
    period = pd.PeriodIndex(df["TIME_PERIOD"], freq="M")
    df = df.assign(year=period.year, quarter=period.quarter)
    g = df.groupby(["year", "quarter"])["OBS_VALUE"]
    out = g.mean().where(g.count() == 3).dropna().reset_index()
    return out.rename(columns={"OBS_VALUE": "euribor_12m"})


# --------------------------------------------------------------------------

def build(refresh: bool = False) -> pd.DataFrame:
    keys = ["region", "year", "quarter"]
    prices = load_prices(refresh)
    # Complete quarterly grid per region: quarters the source marks as not
    # representative (e.g. Navarra 2015-2018) stay as NaN instead of vanishing,
    # so "n quarters ago" is always n rows back.
    grid = []
    for slug, g in prices.groupby("region"):
        first = g.sort_values(["year", "quarter"]).iloc[0]
        last = prices.sort_values(["year", "quarter"]).iloc[-1]
        start = pd.Period(year=first["year"], quarter=first["quarter"], freq="Q")
        end = pd.Period(year=last["year"], quarter=last["quarter"], freq="Q")
        p = pd.period_range(start, end, freq="Q")
        grid.append(pd.DataFrame({"region": slug, "year": p.year, "quarter": p.quarter}))
    df = pd.concat(grid, ignore_index=True).merge(prices, on=keys, how="left")
    df = df.merge(load_monthly_ine("cpi", 2, "mean", refresh), on=keys, how="left")
    df = df.merge(load_monthly_ine("mortgages", 3, "sum", refresh), on=keys, how="left")
    df = df.merge(load_unemployment(refresh), on=keys, how="left")
    df = df.merge(load_euribor(refresh), on=["year", "quarter"], how="left")
    df["date"] = pd.PeriodIndex.from_fields(year=df["year"], quarter=df["quarter"], freq="Q").to_timestamp()
    df["name"] = df["region"].map({k: v[0] for k, v in REGIONS.items()})
    df = df.sort_values(["region", "date"]).reset_index(drop=True)
    return df[["region", "name", "date", "price_m2", "cpi", "mortgages", "unemployment_rate", "euribor_12m"]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="download sources again")
    args = parser.parse_args()
    df = build(args.refresh)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"{len(df)} rows, {df['region'].nunique()} regions -> {OUT_PATH}")
    print(df.groupby("region")["date"].agg(["min", "max", "count"]).head())
    print(df.drop(columns=["region", "name"]).describe().T.round(2))
    print("Missing values per column:\n", df.isna().sum())


if __name__ == "__main__":
    main()
