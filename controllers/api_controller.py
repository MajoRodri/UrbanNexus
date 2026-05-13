import json
import os
import requests as http_requests
from flask import Blueprint, jsonify, request
from services.weather_api_service import WeatherAPIService, obtener_clima_por_coordenadas
from services.normalizer_service import normalizar_datos_clima
from services.logging_service import log_info, log_error

api_bp = Blueprint('api', __name__)

_CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'municipios.json')


@api_bp.route("/api/distritos")
def api_distritos():
    try:
        with open(_CATALOG_PATH, encoding='utf-8') as f:
            catalog = json.load(f)
        distritos = []
        for nombre, coords in catalog.items():
            lat, lon = coords.split(",")
            distritos.append({
                "municipio": nombre,
                "id_estacion": nombre,
                "lat": lat.strip(),
                "lon": lon.strip()
            })
        return jsonify(distritos), 200
    except Exception as e:
        log_error(f"Error al cargar catálogo de distritos: {e}")
        return jsonify({"error": "No se pudo cargar el catálogo"}), 500


def _obtener_direccion(lat, lon):
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

        raw_data = obtener_clima_por_coordenadas(lat, lon)

        if raw_data is None:
            log_error(f"WeatherAPI no devolvió datos para lat={lat}, lon={lon}")
            return jsonify({
                "error": "WeatherAPI no devolvió datos para tu ubicación"
            }), 503

        data = normalizar_datos_clima(raw_data)

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

        data["fuente"] = "weatherapi"

        log_info(f"Clima por coordenadas devuelto: {data.get('ciudad')} {data.get('temperatura')}°C")

        return jsonify(data), 200

    except Exception as e:
        log_error(f"Error en api_controller: {e}")
        return jsonify({
            "error": str(e)
        }), 500


@api_bp.route("/api/clima/municipio")
def api_clima_por_municipio():
    nombre = request.args.get("nombre", "").strip()
    lat = request.args.get("lat", "").strip()
    lon = request.args.get("lon", "").strip()
    fecha = request.args.get("fecha", "").strip() or None

    if not nombre and not (lat and lon):
        return jsonify({"error": "Falta el nombre o coordenadas del municipio"}), 400

    try:
        svc = WeatherAPIService()
        if lat and lon:
            raw = svc.obtener_clima_por_coordenadas(lat, lon, fecha)
        else:
            raw = svc.obtener_clima_por_municipio(nombre, fecha)

        if raw is None:
            log_error(f"WeatherAPI no devolvió datos para municipio={nombre or f'{lat},{lon}'}")
            return jsonify({"error": "No hay datos disponibles para este municipio"}), 503

        data = normalizar_datos_clima(raw)

        if "error" in data and "temperatura" not in data:
            log_error(f"Normalización falló para municipio {nombre}: {data.get('error')}")
            return jsonify({"error": data["error"]}), 503

        location = raw.get("location", {})
        data["ciudad"] = location.get("name", nombre)
        data["fuente"] = "weatherapi"

        log_info(f"Consulta clima por municipio: {data.get('ciudad')} {data.get('temperatura')}°C")

        return jsonify(data), 200

    except Exception as e:
        log_error(f"Error en api_clima_por_municipio: {e}")
        return jsonify({"error": str(e)}), 500
