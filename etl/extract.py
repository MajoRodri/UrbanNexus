import json
import os

import pandas as pd

# Rutas de los archivos de origen que se van a leer
_DATOS_PATH = os.path.join("data", "registros_climaticos.json")        # datos climáticos crudos
_ESTACIONES_PATH = os.path.join("static", "js", "estacion_por_municipio.json")  # catálogo de estaciones


def extraer_registros() -> pd.DataFrame:
    # Abre el JSON de registros climáticos y lo convierte en una tabla (DataFrame)
    # para poder filtrarla y limpiarla fácilmente después
    with open(_DATOS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return pd.DataFrame(raw)


def extraer_referencia_estaciones() -> list[dict]:
    # Lee el catálogo que relaciona cada estación con su municipio
    # Se usa más adelante para validar que los registros pertenezcan a una estación conocida
    with open(_ESTACIONES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data["estacion_por_municipio"]
