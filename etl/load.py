from datetime import datetime

import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models import ETLLog, Medicion, Zona
from services.alert_service import AlertService

# Servicio que evalúa si una medición genera alguna alerta (calor, helada, viento, lluvia)
_alert_service = AlertService()


def _mapear_alertas(alertas: list) -> dict:
    # Convierte la lista de alertas activas en un diccionario con claves específicas
    # para guardarlas como columnas en la tabla Medicion
    return {
        "alerta_calor": next((a for a in alertas if "CALOR" in a), None),
        "alerta_helada": next((a for a in alertas if "FRIO" in a), None),
        "alerta_viento": next((a for a in alertas if "VIENTO" in a), None),
        "alerta_lluvia": next((a for a in alertas if "LLUVIA" in a), None),
    }


def sincronizar_zonas(db: Session, referencia: list[dict]) -> dict[str, list[int]]:
    # Recorre el catálogo de estaciones y crea en la db las Zonas que aún no existen
    # Devuelve un mapa {id_estacion → [id_zona, ...]} que se usará al insertar mediciones
    mapa: dict[str, list[int]] = {}
    for entrada in referencia:
        # Busca si la zona ya existe por su código INE (identificador único del municipio)
        zona = db.query(Zona).filter_by(cod_ine=entrada["cod_ine"]).first()
        if not zona:
            # Si no existe, la crea
            zona = Zona(
                municipio=entrada["municipio"],
                cod_ine=entrada["cod_ine"],
                id_estacion=entrada["id_estacion"],
                estacion_referencia=entrada["estacion_referencia"],
            )
            db.add(zona)
            db.commit()
            db.refresh(zona)
        mapa.setdefault(entrada["id_estacion"], []).append(zona.id)
    return mapa


def cargar_mediciones(db: Session, df: pd.DataFrame, mapa_zonas: dict) -> tuple[int, int]:
    # Recorre cada fila del DataFrame limpio e inserta una Medicion en la db
    # Antes de insertar, calcula si esa medición genera alguna alerta climática
    insertadas = 0
    omitidas = 0
    for _, fila in df.iterrows():
        # Obtiene los IDs de zona que corresponden a esta estación
        ids_zona = mapa_zonas.get(fila["estacion_id"], [])

        # Evalúa si los valores climáticos superan algún umbral de alerta
        alertas = _alert_service.evaluar_alertas({
            "temperatura": fila["temperatura"],
            "humedad": fila["humedad"],
            "viento": fila["viento"],
            "lluvia": fila["lluvia"],
        })
        campos_alerta = _mapear_alertas(alertas)

        # Una misma estación puede cubrir varias zonas, por eso se itera
        for id_zona in ids_zona:
            medicion = Medicion(
                id_zona=id_zona,
                fecha=fila["fecha_dt"],
                temperatura=float(fila["temperatura"]),
                humedad=float(fila["humedad"]),
                viento=float(fila["viento"]),
                lluvia=float(fila["lluvia"]),
                **campos_alerta,
            )
            try:
                db.add(medicion)
                db.commit()
                insertadas += 1
            except IntegrityError:
                # Si ya existe esa medición (misma zona + fecha), se ignora sin romper el proceso
                db.rollback()
                omitidas += 1
    return insertadas, omitidas


def registrar_log(
    db: Session,
    origen: str,
    stats: dict,
    estado: str = "OK",
    mensaje: str = None,
) -> ETLLog:
    # Guarda en la tabla ETL_logs un registro de lo que pasó en esta ejecución
    # Sirve como historial: cuándo corrió, cuántas filas procesó, si hubo errores
    log = ETLLog(
        fecha_ejecucion=datetime.utcnow(),
        origen=origen,
        filas_leidas=stats.get("filas_leidas", 0),
        filas_insertadas=stats.get("filas_insertadas", 0),
        filas_modificadas=stats.get("filas_modificadas", 0),
        filas_descartadas=stats.get("filas_descartadas", 0),
        duplicados_eliminados=stats.get("duplicados_eliminados", 0),
        estado=estado,
        mensaje=mensaje,
    )
    db.add(log)
    db.commit()
    return log
