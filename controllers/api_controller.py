import json
import os
from datetime import datetime
import requests as http_requests
from flask import Blueprint, jsonify, request
from services.weather_api_service import obtener_clima_por_estacion, obtener_clima_por_coordenadas
from services.normalizer_service import normalizar_datos_aemet
from services.logging_service import log_info, log_error
from db.database import SessionLocal
from repositories.sqlite_repository import SQLiteRepository

api_bp = Blueprint('api', __name__)

repo = SQLiteRepository(SessionLocal())
_ESTACIONES_PATH = os.path.join("static", "js", "estacion_por_municipio.json")
_estaciones_cache = None


def _cargar_estaciones():
    global _estaciones_cache

    if _estaciones_cache is None:
        with open(_ESTACIONES_PATH, encoding="utf-8") as f:
            _estaciones_cache = json.load(f)["estacion_por_municipio"]

    return _estaciones_cache


def _buscar_estacion(nombre_municipio: str):
    """
    Devuelve (id_estacion, nombre_estacion) si el municipio está en el JSON local.
    Este JSON solo se usa como catálogo de estaciones, no como persistencia.
    """

    if not nombre_municipio:
        return None, None

    zonas = _cargar_estaciones()
    nombre_lower = nombre_municipio.strip().lower()

    for zona in zonas:
        if zona["municipio"].lower() == nombre_lower:
            return zona["id_estacion"], zona["estacion_referencia"]

    return None, None


def _obtener_direccion(lat, lon):
    """
    Llama a Nominatim y devuelve el diccionario address.
    """

    try:
        res = http_requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lon,
                "format": "json",
                "accept-language": "es"
            },
            headers={
                "User-Agent": "UrbanNexus/1.0"
            },
            timeout=5
        )

        return res.json().get("address", {})

    except Exception:
        return {}


def _guardar_medicion_en_bd(data, id_estacion=None, nombre_estacion=None):
    """
    Guarda en SQLite una medición climática normalizada.
    """

    db = SessionLocal()
    repo = SQLiteRepository(db)

    try:
        municipio = data.get("ciudad", "Ubicación Detectada")

        zona = repo.get_zone_by_municipality(municipio)

        if not zona:
            zona = repo.create_zone(
                municipio=municipio,
                cod_ine=f"AUTO-{id_estacion or municipio}",
                id_estacion=id_estacion or data.get("estacion_id") or "N/A",
                estacion_referencia=nombre_estacion or municipio
            )

        medicion = repo.upsert_measurement(
            id_zona=zona.id,
            fecha=_convertir_fecha(data.get("fecha")),
            temperatura=data.get("temperatura"),
            humedad=data.get("humedad"),
            viento=data.get("viento"),
            lluvia=data.get("lluvia")
        )

        return medicion

    finally:
        db.close()

def _convertir_fecha(fecha_raw):
    if isinstance(fecha_raw, datetime):
        return fecha_raw

    if not fecha_raw:
        return datetime.now()

    formatos = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y"
    ]

    for formato in formatos:
        try:
            return datetime.strptime(str(fecha_raw), formato)
        except ValueError:
            continue

    return datetime.now()

@api_bp.route("/api/clima")
def api_clima():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({
            "error": "Faltan coordenadas"
        }), 400

    log_info(f"Petición /api/clima recibida: lat={lat}, lon={lon}")

    try:
        addr = _obtener_direccion(lat, lon)

        nombre_display = (
            addr.get("city_district")
            or addr.get("suburb")
            or addr.get("town")
            or addr.get("village")
            or addr.get("city")
        )

        nombre_municipio = (
            addr.get("town")
            or addr.get("village")
            or addr.get("city")
        )

        log_info(
            f"Nominatim: display='{nombre_display}', municipio='{nombre_municipio}'"
        )

        id_estacion, nombre_estacion = _buscar_estacion(nombre_municipio)

        raw_data = None

        if id_estacion:
            log_info(
                f"Usando estación del JSON local: {nombre_estacion} ({id_estacion})"
            )

            raw_data = obtener_clima_por_estacion(id_estacion)

        if raw_data is None:
            log_info(
                "No hubo datos por estación. Usando coordenadas como fallback."
            )

            raw_data = obtener_clima_por_coordenadas(lat, lon)

        if raw_data is None:
            log_error(f"AEMET no devolvió datos para lat={lat}, lon={lon}")
            return jsonify({
                "error": "AEMET no devolvió datos para tu ubicación"
            }), 503

        data = normalizar_datos_aemet(raw_data)

        if "error" in data and "temperatura" not in data:
            log_error(f"Normalización falló: {data.get('error')}")
            return jsonify({
                "error": data["error"]
            }), 503

        data["ciudad"] = (
            nombre_display
            or nombre_municipio
            or data.get("ciudad", "Ubicación Detectada")
        )

        data["fuente"] = "aemet"

        medicion = _guardar_medicion_en_bd(
            data=data,
            id_estacion=id_estacion,
            nombre_estacion=nombre_estacion
        )

        data["id_medicion"] = medicion.id

        log_info(
            f"Clima guardado en BD y devuelto: {data.get('ciudad')} {data.get('temperatura')}°C"
        )

        return jsonify(data), 200

    except Exception as e:
        log_error(f"Error en api_controller: {e}")
        return jsonify({
            "error": str(e)
        }), 500