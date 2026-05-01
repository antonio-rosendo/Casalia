import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = Path("data/raw/datos_unidos_meses.csv")
OUT_PATH = Path("data/processed")

def load_raw():
    df = pd.read_csv(DATA_PATH, sep=';')
    # Asegura que la columna temporal es tipo fecha
    # year es una columna del csv
    df['date'] = pd.to_datetime(df['year'], format="%d/%m/%Y")
    df = df.sort_values(['codigo_comunidad', 'date'])
    return df

def add_time_features(df):
    df['year_t0'] = df['date'].dt.year
    df['month_t0'] = df['date'].dt.month
    return df

def add_targets(df):
    # Para cada comunidad, crear precio dentro de 12 meses
    df = df.sort_values(['codigo_comunidad', 'date'])
    df['precio_t_plus_12m'] = df.groupby('codigo_comunidad')['precio'].shift(-12)
    # Eliminar filas sin futuro observado
    df = df.dropna(subset=['precio_t_plus_12m'])
    df['target_price_12m'] = df['precio_t_plus_12m']
    df['target_pct_change_12m'] = (df['precio_t_plus_12m'] - df['precio']) / df['precio']
    return df

def add_lag_features(df):
    # Ejemplo: precio hace 12 meses
    df['precio_lag_12m'] = df.groupby('codigo_comunidad')['precio'].shift(12)
    # Algunas filas iniciales quedarán NaN -> las quitamos
    df = df.dropna(subset=['precio_lag_12m'])
    # También podemos añadir la variación 12m pasada
    df['delta_precio_12m'] = (df['precio'] - df['precio_lag_12m']) / df['precio_lag_12m']
    return df

def select_features(df):
    feature_cols = [
        'precio',          # precio actual
        'precio_lag_12m',  # precio hace 12 meses
        'delta_precio_12m',
        'ipc',
        'mano_obra',
        'num_hipotecas',
        'edad_media',
        'num_inmigracion',
        'precio_Acero',
        'precio_Aluminio',
        'precio_Cemento',
        'precio_Ceramica',
        'precio_Cobre',
        'precio_Energía',
        'precio_Ligantes',
        'precio_Madera',
        'year_t0',
        'month_t0',
    ]

    target_col = 'target_price_12m'

    # Elimina filas con NaN en las columnas seleccionadas
    df = df.dropna(subset=feature_cols + [target_col])

    X = df[feature_cols].values.astype(np.float32)
    y = df[target_col].values.astype(np.float32)

    # Guardamos también comunidad y fecha por si queremos analizar luego
    meta = df[['codigo_comunidad', 'name', 'date']].reset_index(drop=True)

    return X, y, meta, feature_cols, target_col

def main():
    OUT_PATH.mkdir(parents=True, exist_ok=True)
    df = load_raw()
    df = add_time_features(df)
    df = add_targets(df)
    df = add_lag_features(df)

    X, y, meta, feature_cols, target_col = select_features(df)

    # Guardar como npy para que PyTorch lo lea fácil
    np.save(OUT_PATH / "X.npy", X)
    np.save(OUT_PATH / "y.npy", y)
    meta.to_csv(OUT_PATH / "meta.csv", index=False)

    # Guardar lista de columnas por si las necesitas en inference
    with open(OUT_PATH / "features.txt", "w", encoding="utf-8") as f:
        for c in feature_cols:
            f.write(c + "\n")

if __name__ == "__main__":
    main()