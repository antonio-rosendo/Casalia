import pandas as pd
import numpy as np
from pathlib import Path

RAW_PATH = Path("data/raw/datos_unidos_meses.csv")
OUT_PATH = Path("data/processed")


def load_raw() -> pd.DataFrame:
    """
    Carga el CSV original y crea la columna date a partir de 'year'.
    Ajusta sep/decimal si tu fichero es distinto.
    """
    df = pd.read_csv(
        RAW_PATH,
        sep=",",       
        decimal="."
    )

    # year viene en formato 'YYYY-MM-DD'
    df["date"] = pd.to_datetime(df["year"], format="%Y-%m-%d", errors="coerce")

    # Ordenar por comunidad y fecha
    df = df.sort_values(["codigo_comunidad", "date"])

    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade año y mes como features numéricos.
    """
    df["year_t0"] = df["date"].dt.year
    df["month_t0"] = df["date"].dt.month
    return df


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade histórico de 12 meses (lags) y variaciones para:
      - precio
      - IPC
      - num_hipotecas
    """
    df = df.sort_values(["codigo_comunidad", "date"])

    # Precio hace 12 meses (4 trimestres)
    df["precio_lag_12m"] = df.groupby("codigo_comunidad")["precio"].shift(4)
    df["delta_precio_12m"] = (df["precio"] - df["precio_lag_12m"]) / df["precio_lag_12m"]

    # IPC hace 12 meses (4 trimestres)
    df["IPC_lag_12m"] = df.groupby("codigo_comunidad")["IPC"].shift(4)
    df["delta_IPC_12m"] = (df["IPC"] - df["IPC_lag_12m"]) / df["IPC_lag_12m"]

    # Hipotecas hace 12 meses (4 trimestres)
    df["num_hipotecas_lag_12m"] = df.groupby("codigo_comunidad")["num_hipotecas"].shift(4)
    df["delta_num_hipotecas_12m"] = (
        df["num_hipotecas"] - df["num_hipotecas_lag_12m"]
    ) / df["num_hipotecas_lag_12m"]

    # Quitamos filas sin histórico suficiente
    df = df.dropna(
        subset=[
            "precio_lag_12m",
            "IPC_lag_12m",
            "num_hipotecas_lag_12m",
        ]
    )

    return df


def add_targets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea target a 12 meses (4 trimestres):
      - target_price_12m: precio dentro de 12 meses.
      - target_pct_change_12m: variación porcentual en 12 meses.
    """
    df = df.sort_values(["codigo_comunidad", "date"])

    df["precio_t_plus_12m"] = df.groupby("codigo_comunidad")["precio"].shift(-4)

    # Quitamos filas sin futuro observado (final de la serie)
    df = df.dropna(subset=["precio_t_plus_12m"])

    df["target_price_12m"] = df["precio_t_plus_12m"]
    df["target_pct_change_12m"] = (
        df["precio_t_plus_12m"] - df["precio"]
    ) / df["precio"]

    return df


def select_features(df: pd.DataFrame):
    """
    Selecciona columnas de entrada (X) y salida (y),
    y devuelve también meta-info.
    """
    feature_cols = [
        # Precio actual y su dinámica
        "precio",
        "precio_lag_12m",
        "delta_precio_12m",
        # IPC actual y su dinámica
        "IPC",
        "IPC_lag_12m",
        "delta_IPC_12m",
        # Hipotecas y su dinámica
        "num_hipotecas",
        "num_hipotecas_lag_12m",
        "delta_num_hipotecas_12m",
        # Contexto demográfico (sin lags)
        "edad_media",
        "num_inmigracion",
        # Tiempo
        "year_t0",
        "month_t0",
    ]

    # Target: variación porcentual de precio a 12 meses
    target_col = "target_pct_change_12m"

    # Quitamos filas con NaN en cualquier feature o en el target
    df = df.dropna(subset=feature_cols + [target_col])

    X = df[feature_cols].to_numpy(dtype=np.float32)
    y = df[target_col].to_numpy(dtype=np.float32)

    # Meta para análisis (no entra al modelo)
    meta = df[["codigo_comunidad", "comunidad", "name", "date"]].reset_index(
        drop=True
    )

    return X, y, meta, feature_cols, target_col


def train_val_test_split(X, y, meta):
    """
    Divide en train / val / test respetando el tiempo.
    Ajusta los años según el rango real de tu dataset.
    """
    years = meta["date"].dt.year.to_numpy()

    train_mask = years <= 2015
    val_mask = (years >= 2016) & (years <= 2018)
    test_mask = years >= 2019

    splits = {}
    for name, mask in [("train", train_mask), ("val", val_mask), ("test", test_mask)]:
        splits[name] = {
            "X": X[mask],
            "y": y[mask],
            "meta": meta[mask].reset_index(drop=True),
        }
    return splits


def main():
    OUT_PATH.mkdir(parents=True, exist_ok=True)

    df = load_raw()
    df = add_time_features(df)
    df = add_lag_features(df)
    df = add_targets(df)

    X, y, meta, feature_cols, target_col = select_features(df)

    splits = train_val_test_split(X, y, meta)

    # Guardar splits
    for name, split in splits.items():
        np.save(OUT_PATH / f"X_{name}.npy", split["X"])
        np.save(OUT_PATH / f"y_{name}.npy", split["y"])
        split["meta"].to_csv(OUT_PATH / f"meta_{name}.csv", index=False)

    # Guardar nombres de columnas de entrada
    with open(OUT_PATH / "features.txt", "w", encoding="utf-8") as f:
        for c in feature_cols:
            f.write(c + "\n")


if __name__ == "__main__":
    main()