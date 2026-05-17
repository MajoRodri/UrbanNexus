from datetime import datetime

import pandas as pd

_COLUMNAS_REQUERIDAS = ["estacion_id", "fecha", "temperatura", "humedad", "viento", "lluvia"]
# AEMET puede enviar la fecha en cualquiera de estos dos formatos según el endpoint usado
_FORMATOS_FECHA = ("%d-%m-%Y %H:%M", "%Y-%m-%dT%H:%M")
_COLUMNAS_NUMERICAS = ["temperatura", "humedad", "viento", "lluvia"]


def _parse_date(valor: str) -> datetime | None:
    # Prueba cada formato conocido hasta que alguno encaje.
    # Devuelve None si ninguno funciona; esa fila será descartada en el paso dropna del transform.
    for fmt in _FORMATOS_FECHA:
        try:
            return datetime.strptime(str(valor), fmt)
        except (ValueError, TypeError):
            continue
    return None


def _normalize_numerics(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    # Convierte las columnas numéricas de string a float usando coerce,
    # dejando NaN donde el valor no sea convertible (p.ej. "N/A" o cadena vacía).
    # También cuenta cuántos valores se perdieron en la conversión para reportarlo en el log del ETL.
    valores_validos_antes = df[_COLUMNAS_NUMERICAS].notna().sum().sum()
    for col in _COLUMNAS_NUMERICAS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    valores_validos_despues = df[_COLUMNAS_NUMERICAS].notna().sum().sum()
    filas_modificadas = int(valores_validos_antes - valores_validos_despues)
    return df, filas_modificadas


def transform(df: pd.DataFrame, referencia: list[dict]) -> tuple[pd.DataFrame, dict]:
    # Pipeline de limpieza en 5 pasos aplicados en orden:
    # 1. Añade columnas faltantes para evitar KeyError en pasos posteriores.
    # 2. Convierte campos numéricos a float y parsea la fecha a datetime.
    # 3. Descarta filas con cualquier campo crítico nulo (estacion_id, fecha, temperatura...).
    # 4. Elimina duplicados exactos (misma estación + misma fecha).
    # 5. Filtra estaciones que no aparecen en el catálogo de referencia (zonas desconocidas).
    # Devuelve el DataFrame limpio y un dict de estadísticas para el log del ETL.
    filas_originales = len(df)
    df = df.copy()

    for col in _COLUMNAS_REQUERIDAS:
        if col not in df.columns:
            df[col] = None

    df, filas_modificadas = _normalize_numerics(df)
    df["fecha_dt"] = df["fecha"].apply(_parse_date)

    df_limpio = df.dropna(subset=["estacion_id", "fecha_dt", "temperatura", "humedad", "viento", "lluvia"])
    descartados_nulos = filas_originales - len(df_limpio)

    antes_dedup = len(df_limpio)
    df_limpio = df_limpio.drop_duplicates(subset=["estacion_id", "fecha_dt"])
    duplicados_eliminados = antes_dedup - len(df_limpio)

    # Solo se cargan mediciones de estaciones que existen en el catálogo local;
    # las demás se descartan para evitar referencias huérfanas en la tabla Zona.
    estaciones_validas = {e["id_estacion"] for e in referencia}
    antes_filtro = len(df_limpio)
    df_limpio = df_limpio[df_limpio["estacion_id"].isin(estaciones_validas)]
    descartados_sin_zona = antes_filtro - len(df_limpio)

    stats = {
        "filas_leidas": filas_originales,
        "filas_modificadas": filas_modificadas,
        "duplicados_eliminados": duplicados_eliminados,
        "descartados_nulos": descartados_nulos,
        "descartados_sin_zona": descartados_sin_zona,
    }
    return df_limpio.reset_index(drop=True), stats
