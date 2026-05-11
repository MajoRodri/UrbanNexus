from datetime import datetime

import pandas as pd

_COLUMNAS_REQUERIDAS = ["estacion_id", "fecha", "temperatura", "humedad", "viento", "lluvia"]
_FORMATOS_FECHA = ("%d-%m-%Y %H:%M", "%Y-%m-%dT%H:%M")
_COLUMNAS_NUMERICAS = ["temperatura", "humedad", "viento", "lluvia"]


def _parse_date(valor: str) -> datetime | None:
    for fmt in _FORMATOS_FECHA:
        try:
            return datetime.strptime(str(valor), fmt)
        except (ValueError, TypeError):
            continue
    return None


def _normalize_numerics(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    valores_validos_antes = df[_COLUMNAS_NUMERICAS].notna().sum().sum()
    for col in _COLUMNAS_NUMERICAS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    valores_validos_despues = df[_COLUMNAS_NUMERICAS].notna().sum().sum()
    filas_modificadas = int(valores_validos_antes - valores_validos_despues)
    return df, filas_modificadas


def transform(df: pd.DataFrame, referencia: list[dict]) -> tuple[pd.DataFrame, dict]:
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
