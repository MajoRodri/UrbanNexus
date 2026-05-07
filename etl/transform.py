from datetime import datetime

import pandas as pd

# Columnas que DEBEN existir en cada registro; si falta alguna se considera incompleto
_COLUMNAS_REQUERIDAS = ["estacion_id", "fecha", "temperatura", "humedad", "viento", "lluvia"]

# Formatos de fecha aceptados en el JSON (puede venir en cualquiera de los dos)
_FORMATOS_FECHA = ("%d-%m-%Y %H:%M", "%Y-%m-%dT%H:%M")


def _parsear_fecha(valor: str) -> datetime | None:
    # Intenta convertir el texto de fecha a un objeto datetime real
    # Si no encaja con ningún formato conocido devuelve None (fecha inválida)
    for fmt in _FORMATOS_FECHA:
        try:
            return datetime.strptime(str(valor), fmt)
        except (ValueError, TypeError):
            continue
    return None


def transformar(df: pd.DataFrame, referencia: list[dict]) -> tuple[pd.DataFrame, dict]:
    # Recibe los datos crudos y el catálogo de estaciones
    # Devuelve los datos limpios + un resumen de cuánto se descartó y por qué
    filas_originales = len(df)
    df = df.copy()

    # Si al JSON le falta alguna columna requerida, la agrega vacía para no romper el proceso
    for col in _COLUMNAS_REQUERIDAS:
        if col not in df.columns:
            df[col] = None

    # Convierte la fecha de texto a datetime para poder compararla y guardarla correctamente
    df["fecha_dt"] = df["fecha"].apply(_parsear_fecha)

    # Paso 1: descarta filas que tengan algún campo clave vacío o fecha inválida
    df_limpio = df.dropna(subset=["estacion_id", "fecha_dt", "temperatura", "humedad", "viento", "lluvia"])
    descartados_nulos = filas_originales - len(df_limpio)

    # Paso 2: elimina duplicados — mismo par (estación + fecha) no puede aparecer dos veces
    antes_dedup = len(df_limpio)
    df_limpio = df_limpio.drop_duplicates(subset=["estacion_id", "fecha_dt"])
    duplicados_eliminados = antes_dedup - len(df_limpio)

    # Paso 3: descarta registros de estaciones que no están en el catálogo de referencia
    estaciones_validas = {e["id_estacion"] for e in referencia}
    antes_filtro = len(df_limpio)
    df_limpio = df_limpio[df_limpio["estacion_id"].isin(estaciones_validas)]
    descartados_sin_zona = antes_filtro - len(df_limpio)

    # Resumen de lo que pasó en esta etapa (se guarda en el log al final del pipeline)
    stats = {
        "filas_leidas": filas_originales,
        "duplicados_eliminados": duplicados_eliminados,
        "descartados_nulos": descartados_nulos,
        "descartados_sin_zona": descartados_sin_zona,
    }
    return df_limpio.reset_index(drop=True), stats
