import json
import os
import requests as http_requests
from flask import Blueprint, jsonify, request
from services.weather_api_service import obtener_clima_por_estacion, obtener_clima_por_coordenadas
from services.normalizer_service import normalizar_datos_aemet
from services.logging_service import log_info, log_error
from repositories.json_repository import guardar_registro

api_bp = Blueprint('api', __name__)

_ESTACIONES_PATH = os.path.join("static", "js", "estacion_por_municipio.json")
_estaciones_cache = None


def _cargar_estaciones():
    global _estaciones_cache
    if _estaciones_cache is None:
        with open(_ESTACIONES_PATH, encoding="utf-8") as f:
            _estaciones_cache = json.load(f)["estacion_por_municipio"]
    return _estaciones_cache


def _buscar_estacion(nombre_municipio: str):
    """Devuelve (id_estacion, nombre_estacion) si el municipio está en el JSON."""
    if not nombre_municipio:
        return None, None
    zonas = _cargar_estaciones()
    nombre_lower = nombre_municipio.strip().lower()
    for zona in zonas:
        if zona["municipio"].lower() == nombre_lower:
            return zona["id_estacion"], zona["estacion_referencia"]
    return None, None


def _obtener_direccion(lat, lon):
    """Llama a Nominatim y devuelve el dict address completo."""
    try:
        res = http_requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "accept-language": "es"},
            headers={"User-Agent": "UrbanNexus/1.0"},
            timeout=5
        )
        return res.json().get("address", {})
    except Exception:
        return {}


@api_bp.route("/api/clima")
def api_clima():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Faltan coordenadas"}), 400

    log_info(f"Petición /api/clima recibida: lat={lat}, lon={lon}")

    try:
        # 1. Nominatim → nombre display + municipio para búsqueda
        addr = _obtener_direccion(lat, lon)
        nombre_display = (
            addr.get("city_district")
            or addr.get("suburb")
            or addr.get("town")
            or addr.get("village")
            or addr.get("city")
        )
        nombre_municipio = addr.get("town") or addr.get("village") or addr.get("city")

        log_info(f"Nominatim: display='{nombre_display}', municipio='{nombre_municipio}'")

        # 2. Buscar estación en el JSON local
        id_estacion, nombre_estacion = _buscar_estacion(nombre_municipio)

        # 3. Obtener datos de AEMET
        if id_estacion:
            log_info(f"Usando estación del JSON: {nombre_estacion} ({id_estacion})")
            raw_data = obtener_clima_por_estacion(id_estacion)
        else:
            log_info(f"'{nombre_municipio}' no está en el JSON, usando Haversine como fallback")
            raw_data = obtener_clima_por_coordenadas(lat, lon)

        if raw_data is None:
            log_error(f"AEMET no devolvió datos para lat={lat}, lon={lon}")
            return jsonify({"error": "AEMET no devolvió datos para tu ubicación"}), 503

        # 4. Normalizar
        data = normalizar_datos_aemet(raw_data)

        if "error" in data and "temperatura" not in data:
            log_error(f"Normalización falló: {data.get('error')}")
            return jsonify({"error": data["error"]}), 503

        # 5. Asignar nombre real del lugar
        data["ciudad"] = nombre_display or nombre_municipio or data.get("ciudad", "Ubicación Detectada")

        data["fuente"] = "aemet"
        guardar_registro(data)

        log_info(f"Clima devuelto: {data.get('ciudad')} {data.get('temperatura')}°C")
        return jsonify(data), 200

    except Exception as e:
        log_error(f"Error en api_controller: {e}")
        return jsonify({"error": str(e)}), 500
