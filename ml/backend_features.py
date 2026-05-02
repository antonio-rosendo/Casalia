# ml/backend_features.py
from ine_client import (
    get_ipv_last_and_12m_ago,
    get_ipc_last_and_12m_ago,
    # cuando tengas hipotecas/demografía, añadirás funciones similares
)
from inference import predict_pct_change_12m


def build_features_for_request(payload: dict) -> dict:
    ccaa = payload["comunidad_id"]   # p.ej. "andalucia"
    year = int(payload["year"])
    month = int(payload["month"])

    precio_viv = float(payload["precio_actual_vivienda"])
    metros = float(payload["metros_cuadrados"])
    precio_m2 = precio_viv / metros

    # IPV para reconstruir precio_lag_12m
    ipv_actual, ipv_12m_ago = get_ipv_last_and_12m_ago(ccaa)
    factor_12m = ipv_actual / ipv_12m_ago
    precio_lag_12m = precio_m2 / factor_12m
    delta_precio_12m = (precio_m2 - precio_lag_12m) / precio_lag_12m

    # IPC
    ipc_actual, ipc_12m_ago = get_ipc_last_and_12m_ago(ccaa)
    delta_ipc_12m = (ipc_actual - ipc_12m_ago) / ipc_12m_ago

    # TODO: hipotecas, edad_media, num_inmigracion con el mismo patrón
    # por ahora los puedes dejar a 0 o a la media histórica si quieres probar

    features = {
        "precio": precio_m2,
        "precio_lag_12m": precio_lag_12m,
        "delta_precio_12m": delta_precio_12m,
        "IPC": ipc_actual,
        "IPC_lag_12m": ipc_12m_ago,
        "delta_IPC_12m": delta_ipc_12m,
        "num_hipotecas": 0.0,
        "num_hipotecas_lag_12m": 0.0,
        "delta_num_hipotecas_12m": 0.0,
        "edad_media": 0.0,
        "num_inmigracion": 0.0,
        "year_t0": year,
        "month_t0": month,
    }
    return features


def run_prediction(payload: dict):
    features = build_features_for_request(payload)
    pct_change_12m = predict_pct_change_12m(features)

    precio_viv = float(payload["precio_actual_vivienda"])
    precio_futuro = precio_viv * (1.0 + pct_change_12m)

    return {
        "pct_change_12m": pct_change_12m,
        "precio_actual_vivienda": precio_viv,
        "precio_futuro_vivienda": precio_futuro,
    }