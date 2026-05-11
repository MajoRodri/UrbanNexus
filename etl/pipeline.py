import logging

from db.database import SessionLocal
from etl.extract import extract_records, extract_station_reference
from etl.load import load_measurements, log_execution, sync_zones
from etl.transform import transform

logger = logging.getLogger(__name__)

# Nombre del archivo de origen, se guarda en el log para saber de dónde vinieron los datos
_ORIGEN = "data/registros_climaticos.json"


def run_pipeline(db=None) -> dict:
    # Punto de entrada del ETL. Llama a los 3 pasos en orden: extraer → transformar → cargar
    # Si no se pasa una sesión de BD, crea una propia y la cierra al terminar
    cerrar_bd = False
    if db is None:
        db = SessionLocal()
        cerrar_bd = True

    try:
        # PASO 1 — EXTRAER: lee los archivos JSON de origen
        df_raw = extract_records()
        referencia = extract_station_reference()

        # PASO 2 — TRANSFORMAR: limpia los datos (quita nulos, duplicados y estaciones inválidas)
        df_limpio, stats_transform = transform(df_raw, referencia)

        # PASO 3 — CARGAR: guarda zonas y mediciones en la BD
        mapa_zonas = sync_zones(db, referencia)
        insertadas, omitidas = load_measurements(db, df_limpio, mapa_zonas)

        # Suma los duplicados detectados en transform + los que ya existían en el db
        total_duplicados = stats_transform["duplicados_eliminados"] + omitidas
        total_descartados = stats_transform["descartados_nulos"] + stats_transform["descartados_sin_zona"]

        # Guarda el historial de esta ejecución en la tabla ETL_logs
        log_execution(db, _ORIGEN, {
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
        log_execution(db, _ORIGEN, {}, estado="ERROR", mensaje=str(exc))
        logger.error(f"ETL falló: {exc}")
        raise

    finally:
        # Cierra la sesión de BD solo si este pipeline la abrió (no la cierra si fue pasada externamente)
        if cerrar_bd:
            db.close()
