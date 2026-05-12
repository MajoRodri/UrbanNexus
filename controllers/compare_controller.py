from datetime import datetime, date

from db.database import SessionLocal
from db.models import Medicion, Zona

from services.weather_api_service import WeatherAPIService
from services.normalizer_service import normalizar_datos_aemet
from services.logging_service import log_info, log_error


def calculate_difference(v1, v2) -> float:
    try:
        val1 = float(v1) if v1 is not None else 0.0
        val2 = float(v2) if v2 is not None else 0.0
        return round(abs(val1 - val2), 2)
    except (ValueError, TypeError):
        return 0.0


def has_discrepancy(differences: dict) -> bool:
    return (
        differences["temperatura"] > 3 or
        differences["humedad"] > 10 or
        differences["viento"] > 10 or
        differences["lluvia"] > 5
    )


def _fecha_to_date(valor):
    if not valor:
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(str(valor), formato).date()
        except ValueError:
            continue

    return None


def _medicion_to_dict(medicion, zona):
    return {
        "id": medicion.id,
        "municipio": zona.municipio if zona else "Desconocido",
        "estacion_id": zona.id_estacion if zona else None,
        "fecha": (
            medicion.fecha.strftime("%d/%m/%Y")
            if hasattr(medicion.fecha, "strftime")
            else str(medicion.fecha)
        ),
        "temperatura": medicion.temperatura,
        "humedad": medicion.humedad,
        "viento": medicion.viento,
        "lluvia": medicion.lluvia,
        "fuente": "manual"
    }


def _buscar_medicion_manual_bd(municipio: str, fecha_html: str | None):
    db = SessionLocal()

    try:
        query = (
            db.query(Medicion, Zona)
            .join(Zona, Medicion.id_zona == Zona.id)
            .filter(Zona.municipio.ilike(f"%{municipio}%"))
            .order_by(Medicion.fecha.desc())
        )

        resultados = query.all()

        fecha_objetivo = _fecha_to_date(fecha_html) if fecha_html else datetime.now().date()

        for medicion, zona in resultados:
            fecha_medicion = _fecha_to_date(medicion.fecha)

            if fecha_medicion == fecha_objetivo:
                return _medicion_to_dict(medicion, zona)

        return None

    finally:
        db.close()


def compare_latest_records(municipio: str, fecha_html: str = None) -> dict:
    """
    Compara el último registro manual guardado en SQLite con los datos oficiales de AEMET.
    """

    if not fecha_html:
        fecha_target = datetime.now().strftime("%d/%m/%Y")
    else:
        try:
            fecha_obj = datetime.strptime(fecha_html, "%Y-%m-%d")
            fecha_target = fecha_obj.strftime("%d/%m/%Y")
        except ValueError:
            fecha_target = fecha_html

    log_info(f"Iniciando comparativa BD/API: {municipio} para el día {fecha_target}")

    manual_record = _buscar_medicion_manual_bd(
        municipio=municipio,
        fecha_html=fecha_html
    )

    if not manual_record:
        return {
            "success": False,
            "message": f"No hay datos manuales en BD para {municipio} el día {fecha_target}."
        }

    id_estacion = manual_record.get("estacion_id")

    try:
        api_service = WeatherAPIService()
        todas_las_obs = api_service._obtener_datos_crudos()

        raw_api_data = next(
            (
                obs for obs in todas_las_obs
                if str(obs.get("idema")) == str(id_estacion)
            ),
            None
        )

        if not raw_api_data:
            return {
                "success": False,
                "message": f"La AEMET no tiene datos hoy para la estación {id_estacion}."
            }

        api_record = normalizar_datos_aemet(raw_api_data)
        api_record["fuente"] = "AEMET (Oficial)"

    except Exception as e:
        log_error(f"Error en comparativa: {e}")
        return {
            "success": False,
            "message": "Error de conexión con la API de AEMET."
        }

    diffs = {
        "temperatura": calculate_difference(
            manual_record.get("temperatura"),
            api_record.get("temperatura")
        ),
        "humedad": calculate_difference(
            manual_record.get("humedad"),
            api_record.get("humedad")
        ),
        "viento": calculate_difference(
            manual_record.get("viento"),
            api_record.get("viento")
        ),
        "lluvia": calculate_difference(
            manual_record.get("lluvia"),
            api_record.get("lluvia")
        )
    }

    return {
        "success": True,
        "municipio": municipio.title(),
        "fecha": fecha_target,
        "manual": manual_record,
        "api": api_record,
        "diferencias": diffs,
        "hay_discrepancia": has_discrepancy(diffs)
    }