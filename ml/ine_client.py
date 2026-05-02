import requests

BASE_URL = "https://servicios.ine.es/wstempus/js/ES"

# ---- CONSTANTES QUE TÚ COMPLETARÁS CON LOS IDs REALES ----

# Tablas Tempus
IPV_TABLE_ID = 49300   # Índice precios vivienda por CCAA (IPV)[web:203]
IPC_TABLE_ID = 76093   # IPC por CCAA, general y ECOICOP (mensual)[web:198]

# Valores de CCAA en cada tabla (rellena con VALORES_GRUPOSTABLA)
IPV_CCAA_VALUES = {
    # "andalucia": <ID_VALOR_CCAA_EN_TABLA_IPV>,
    # "madrid":    <ID_VALOR_CCAA_EN_TABLA_IPV>,
}

IPC_CCAA_VALUES = {
    # "andalucia": <ID_VALOR_CCAA_EN_TABLA_IPC>,
    # "madrid":    <ID_VALOR_CCAA_EN_TABLA_IPC>,
}

# Otros valores para cada tabla
# IPC: queremos Índice general y Tipo de dato = Índice
IPC_GROUP_GENERAL_VALUE = None  # ID_VALOR del grupo ECOICOP que representa "Índice general"
IPC_DATATYPE_INDEX_VALUE = None # ID_VALOR del tipo de dato que representa "Índice"

# IPV: queremos Índice general y Tipo de dato = Índice
IPV_INDEXTYPE_GENERAL_VALUE = None  # ID_VALOR "General"
IPV_DATATYPE_INDEX_VALUE = None     # ID_VALOR "Index"

# IDs de variables (no de valores) para tv=VAR:VAL
IPC_VAR_CCAA = None       # IdVariable "Comunidades y Ciudades Autónomas"
IPC_VAR_GROUP = None      # IdVariable "Grupos ECOICOP"
IPC_VAR_DATATYPE = None   # IdVariable "Tipo de dato"

IPV_VAR_CCAA = None       # IdVariable "Comunidades y Ciudades Autónomas"
IPV_VAR_INDEXTYPE = None  # IdVariable "Índice type"
IPV_VAR_DATATYPE = None   # IdVariable "Tipo de dato"


# ---- FUNCIONES AUXILIARES ----

class IneError(Exception):
    pass


def _get_json(url: str, params=None):
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        raise IneError(f"Error INE {resp.status_code}: {resp.text[:200]}")
    return resp.json()


def _get_last_and_12_from_table(table_id: int, tv_params: list[str], nult: int = 13):
    """
    Llama a DATOS_TABLA y devuelve (valor_actual, valor_hace_12_periodos).
    tv_params es una lista de strings tipo 'VAR:VAL', que se pasan como &tv=...
    """
    # Construimos query params: nult últimos periodos, tip=AM (auto)
    params = [("nult", nult), ("tip", "AM")]
    for tv in tv_params:
        params.append(("tv", tv))

    url = f"{BASE_URL}/DATOS_TABLA/{table_id}"
    data = _get_json(url, params=params)
    # data es una lista de series, cada una con "Data": [ { "Valor": ..., "Fecha": ...}, ... ]
    if not data or "Data" not in data[0]:
        raise IneError(f"Formato inesperado en DATOS_TABLA/{table_id}")

    values = data[0]["Data"]
    if len(values) < 13:
        raise IneError(f"No hay 13 observaciones para tabla {table_id}")

    last = float(values[-1]["Valor"])
    lag_12 = float(values[-13]["Valor"])
    return last, lag_12


# ---- FUNCIONES ESPECÍFICAS ----

def get_ipv_last_and_12m_ago(ccaa_key: str):
    """
    IPV (índice de precios de vivienda) actual y hace 12 meses para una CCAA.
    """
    if IPV_VAR_CCAA is None or IPV_INDEXTYPE_GENERAL_VALUE is None or IPV_DATATYPE_INDEX_VALUE is None:
        raise IneError("Rellena IPV_VAR_CCAA, IPV_INDEXTYPE_GENERAL_VALUE e IPV_DATATYPE_INDEX_VALUE")
    if ccaa_key not in IPV_CCAA_VALUES:
        raise IneError(f"CCAA {ccaa_key} no mapeada en IPV_CCAA_VALUES")

    tv_params = [
        f"{IPV_VAR_CCAA}:{IPV_CCAA_VALUES[ccaa_key]}",
        f"{IPV_VAR_INDEXTYPE}:{IPV_INDEXTYPE_GENERAL_VALUE}",
        f"{IPV_VAR_DATATYPE}:{IPV_DATATYPE_INDEX_VALUE}",
    ]
    return _get_last_and_12_from_table(IPV_TABLE_ID, tv_params, nult=13)


def get_ipc_last_and_12m_ago(ccaa_key: str):
    """
    IPC general actual y hace 12 meses para una CCAA.
    """
    if IPC_VAR_CCAA is None or IPC_GROUP_GENERAL_VALUE is None or IPC_DATATYPE_INDEX_VALUE is None:
        raise IneError("Rellena IPC_VAR_CCAA, IPC_GROUP_GENERAL_VALUE e IPC_DATATYPE_INDEX_VALUE")
    if ccaa_key not in IPC_CCAA_VALUES:
        raise IneError(f"CCAA {ccaa_key} no mapeada en IPC_CCAA_VALUES")

    tv_params = [
        f"{IPC_VAR_CCAA}:{IPC_CCAA_VALUES[ccaa_key]}",
        f"{IPC_VAR_GROUP}:{IPC_GROUP_GENERAL_VALUE}",
        f"{IPC_VAR_DATATYPE}:{IPC_DATATYPE_INDEX_VALUE}",
    ]
    return _get_last_and_12_from_table(IPC_TABLE_ID, tv_params, nult=13)