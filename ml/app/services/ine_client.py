import requests

BASE_URL = "https://servicios.ine.es/wstempus/js/ES"

class IneError(Exception):
    pass

IPC_SERIES = {
    "nacional": "IPC290751", "andalucia": "IPC293660", "aragon": "IPC293716", "asturias": "IPC293772",
    "baleares": "IPC293828", "canarias": "IPC293884", "cantabria": "IPC293940", "castilla_y_leon": "IPC293996",
    "castilla_la_mancha": "IPC294052", "cataluna": "IPC294108", "comunitat_valenciana": "IPC294164",
    "extremadura": "IPC294220", "galicia": "IPC294276", "madrid": "IPC294332", "murcia": "IPC294388",
    "navarra": "IPC294444", "pais_vasco": "IPC294500", "rioja": "IPC294556", "ceuta": "IPC294612",
    "melilla": "IPC293604"
}
IPV_SERIES = {
    "nacional": "IPV769", "andalucia": "IPV766", "aragon": "IPV763", "asturias": "IPV760",
    "baleares": "IPV757", "canarias": "IPV754", "cantabria": "IPV751", "castilla_y_leon": "IPV748",
    "castilla_la_mancha": "IPV745", "cataluna": "IPV742", "comunitat_valenciana": "IPV739",
    "extremadura": "IPV736", "galicia": "IPV733", "madrid": "IPV730", "murcia": "IPV727",
    "navarra": "IPV724", "pais_vasco": "IPV721", "rioja": "IPV718", "ceuta": "IPV715",
    "melilla": "IPV712"
}
HIPOTECAS_SERIES = {
    "nacional": "HPT34618", "andalucia": "HPT62881", "aragon": "HPT62879", "asturias": "HPT62877",
    "baleares": "HPT62875", "canarias": "HPT62873", "cantabria": "HPT62871", "castilla_y_leon": "HPT62869",
    "castilla_la_mancha": "HPT62867", "cataluna": "HPT62865", "comunitat_valenciana": "HPT62863",
    "extremadura": "HPT62861", "galicia": "HPT62859", "madrid": "HPT62857", "murcia": "HPT62855",
    "navarra": "HPT62853", "pais_vasco": "HPT62851", "rioja": "HPT62849", "ceuta": "HPT62847",
    "melilla": "HPT62845"
}
EDAD_SERIES = {
    "nacional": "IDB85660", "andalucia": "IDB86230", "aragon": "IDB86227", "asturias": "IDB86224",
    "baleares": "IDB86221", "canarias": "IDB86218", "cantabria": "IDB86215", "castilla_y_leon": "IDB86212",
    "castilla_la_mancha": "IDB86209", "cataluna": "IDB86206", "comunitat_valenciana": "IDB86203",
    "extremadura": "IDB86200", "galicia": "IDB86197", "madrid": "IDB86194", "murcia": "IDB86191",
    "navarra": "IDB86188", "pais_vasco": "IDB86185", "rioja": "IDB86182", "ceuta": "IDB86179",
    "melilla": "IDB86176"
}
INMIGRACION_SERIES = {
    "nacional": "EM754670", "andalucia": "EM761473", "aragon": "EM1295933", "asturias": "EM690633",
    "baleares": "EM924171", "canarias": "EM1037891", "cantabria": "EM955263", "castilla_y_leon": "EM1093240",
    "castilla_la_mancha": "EM1204944", "cataluna": "EM1253990", "comunitat_valenciana": "EM1288444",
    "extremadura": "EM1147865", "galicia": "EM947154", "madrid": "EM1238935", "murcia": "EM700391",
    "navarra": "EM700211", "pais_vasco": "EM936835", "rioja": "EM880841", "ceuta": "EM953182",
    "melilla": "EM657872"
}

def _get_json(url: str, params: dict = None):
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        raise IneError(f"Error INE {resp.status_code}: {resp.text[:200]}")
    return resp.json()

def _get_series_data_lag(serie_code: str, force_periodos: int = 13):
    if not serie_code:
        raise IneError("Codigo de serie en blanco")
    
    url = f"{BASE_URL}/DATOS_SERIE/{serie_code}"
    data = _get_json(url, {"nult": force_periodos})
    
    if not isinstance(data, dict) or "Data" not in data:
        raise IneError(f"Formato inesperado para la serie {serie_code}")
        
    values = data["Data"]
    if len(values) < force_periodos:
        pass
        
    last = float(values[0]["Valor"])
    lag = float(values[-1]["Valor"])
    
    if values[0]["Fecha"] < values[-1]["Fecha"]:
        last = float(values[-1]["Valor"])
        lag = float(values[0]["Valor"])

    return last, lag

def _get_series_data_last(serie_code: str):
    if not serie_code:
        raise IneError("Codigo de serie en blanco")
        
    url = f"{BASE_URL}/DATOS_SERIE/{serie_code}"
    data = _get_json(url, {"nult": 1})
    
    if not isinstance(data, dict) or "Data" not in data or not data["Data"]:
        raise IneError(f"No hay observaciones para la serie {serie_code}")
        
    return float(data["Data"][0]["Valor"])


def get_ipv_last_and_lag(ccaa_key: str):
    # IPV es trimestral, 1 año = 4 trimestres (+1 actual = 5)
    return _get_series_data_lag(IPV_SERIES.get(ccaa_key), force_periodos=5)

def get_ipc_last_and_lag(ccaa_key: str):
    return _get_series_data_lag(IPC_SERIES.get(ccaa_key), force_periodos=13)

def get_hipotecas_last_and_lag(ccaa_key: str):
    last, lag = _get_series_data_lag(HIPOTECAS_SERIES.get(ccaa_key), force_periodos=13)
    return last * 3.0, lag * 3.0  # Emulating quarterly aggregates from monthly data

def get_edad_media(ccaa_key: str):
    return _get_series_data_last(EDAD_SERIES.get(ccaa_key))

def get_num_inmigracion(ccaa_key: str):
    return _get_series_data_last(INMIGRACION_SERIES.get(ccaa_key))
