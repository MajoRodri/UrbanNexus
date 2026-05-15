import json
import os

import pandas as pd

_DATOS_PATH = os.path.join("data", "registros_climaticos.json")
_CATALOG_PATH = os.path.join("config", "municipios.json")


def extract_records() -> pd.DataFrame:
    with open(_DATOS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return pd.DataFrame(raw)


def extract_station_reference() -> list[dict]:
    with open(_CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)
    return [
        {"municipio": nombre, "cod_ine": nombre, "id_estacion": nombre, "estacion_referencia": nombre}
        for nombre in catalog
    ]
