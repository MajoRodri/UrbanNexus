import logging

from db.database import SessionLocal
from etl.extract import extraer_referencia_estaciones, extraer_registros
from etl.load import cargar_mediciones, registrar_log, sincronizar_zonas
from etl.transform import transformar

logger = logging.getLogger(__name__)

# Nombre del archivo de origen, se guarda en el log para saber de dónde vinieron los datos
_ORIGEN = "data/registros_climaticos.json"


def ejecutar_pipeline(db=None) -> dict:
    # Punto de entrada del ETL. Llama a los 3 pasos en orden: extraer → transformar → cargar
    # Si no se pasa una sesión de BD, crea una propia y la cierra al terminar
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # PASO 1 — EXTRAER: lee los archivos JSON de origen
        df_raw = extraer_registros()
        referencia = extraer_referencia_estaciones()

        # PASO 2 — TRANSFORMAR: limpia los datos (quita nulos, duplicados y estaciones inválidas)
        df_limpio, stats_transform = transformar(df_raw, referencia)

        # PASO 3 — CARGAR: guarda zonas y mediciones en la BD
        mapa_zonas = sincronizar_zonas(db, referencia)
        insertadas, omitidas = cargar_mediciones(db, df_limpio, mapa_zonas)

        # Suma los duplicados detectados en transform + los que ya existían en la BD
        total_duplicados = stats_transform["duplicados_eliminados"] + omitidas
        total_descartados = stats_transform["descartados_nulos"] + stats_transform["descartados_sin_zona"]

        # Guarda el historial de esta ejecución en la tabla ETL_logs
        registrar_log(db, _ORIGEN, {
            "filas_leidas": stats_transform["filas_leidas"],
            "filas_insertadas": insertadas,
            "filas_modificadas": 0,
            "filas_descartadas": total_descartados,
            "duplicados_eliminados": total_duplicados,
        })

        # Devuelve un resumen que puede mostrarse en la API o en la consola
        resumen = {
            "estado": "OK",
            "filas_leidas": stats_transform["filas_leidas"],
            "insertadas": insertadas,
            "descartadas": total_descartados,
            "duplicados": total_duplicados,
        }
        logger.info(f"ETL completado: {resumen}")
        return resumen

    except Exception as exc:
        # Si algo falla en cualquier paso, guarda el error en el log y relanza la excepción
        registrar_log(db, _ORIGEN, {}, estado="ERROR", mensaje=str(exc))
        logger.error(f"ETL falló: {exc}")
        raise

    finally:
        # Cierra la sesión de BD solo si este pipeline la abrió (no la cierra si fue pasada externamente)
        if close_db:
            db.close()
