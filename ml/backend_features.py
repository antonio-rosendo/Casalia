from datetime import datetime
from ine_client import (
    get_ipv_last_and_lag,
    get_ipc_last_and_lag,
    get_hipotecas_last_and_lag,
    get_edad_media,
    get_num_inmigracion,
)
from inference import predict_pct_change_12m

def build_features_for_request(comunidad_autonoma: str, precio_total: float, metros_cuadrados: float) -> dict:
    now = datetime.now()
    year = now.year
    month = now.month

    precio_m2 = precio_total / metros_cuadrados

    try:
        ipv_actual, ipv_lag = get_ipv_last_and_lag(comunidad_autonoma)
        factor_lag = ipv_actual / (ipv_lag if ipv_lag else 1)
        precio_lag = precio_m2 / factor_lag
        delta_precio = (precio_m2 - precio_lag) / precio_lag
    except Exception as e:
        precio_lag = precio_m2
        delta_precio = 0.0

    try:
        ipc_actual, ipc_lag = get_ipc_last_and_lag(comunidad_autonoma)
        delta_ipc = (ipc_actual - ipc_lag) / (ipc_lag if ipc_lag else 1)
    except Exception as e:
        ipc_actual = 110.0
        ipc_lag = 110.0
        delta_ipc = 0.0

    try:
        hipotecas_actual, hipotecas_lag = get_hipotecas_last_and_lag(comunidad_autonoma)
        delta_hipotecas = (hipotecas_actual - hipotecas_lag) / (hipotecas_lag if hipotecas_lag else 1)
    except Exception as e:
        hipotecas_actual = 20000.0
        hipotecas_lag = 20000.0
        delta_hipotecas = 0.0

    try:
        edad_media = get_edad_media(comunidad_autonoma)
    except Exception as e:
        edad_media = 40.0

    try:
        num_inmigracion = get_num_inmigracion(comunidad_autonoma)
    except Exception as e:
        num_inmigracion = 10000.0

    features = {
        "precio": precio_m2,
        "precio_lag_12m": precio_lag,
        "delta_precio_12m": delta_precio,
        "IPC": ipc_actual,
        "IPC_lag_12m": ipc_lag,
        "delta_IPC_12m": delta_ipc,
        "num_hipotecas": hipotecas_actual,
        "num_hipotecas_lag_12m": hipotecas_lag,
        "delta_num_hipotecas_12m": delta_hipotecas,
        "edad_media": edad_media,
        "num_inmigracion": num_inmigracion,
        "year_t0": year,
        "month_t0": month,
    }
    return features


def run_prediction(comunidad_autonoma: str, precio_total: float, metros_cuadrados: float):
    features = build_features_for_request(comunidad_autonoma, precio_total, metros_cuadrados)
    pct_change_12m = predict_pct_change_12m(features)

    # El porcentaje de output hay que respetarlo absoluto tal cual da 
    precio_futuro = precio_total * (1.0 + pct_change_12m)

    return {
        "pct_change_12m": pct_change_12m,
        "precio_actual_vivienda": precio_total,
        "precio_futuro_vivienda": precio_futuro,
    }
