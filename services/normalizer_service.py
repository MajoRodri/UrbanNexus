import logging
from services.alert_service import AlertService

alert_service = AlertService()


def normalizar_datos_clima(data):
    try:
        if data is None:
            return {"error": "No hay datos disponibles"}

        location = data.get("location", {})
        nombre_lugar = location.get("name", "Ubicación Desconocida")

        forecastday = data.get("forecast", {}).get("forecastday", [])
        if forecastday:
            day = forecastday[0].get("day", {})
            datos_normalizados = {
                "ciudad": nombre_lugar,
                "estacion": nombre_lugar,
                "fecha": forecastday[0].get("date", "N/A"),
                "temperatura": float(day.get("avgtemp_c", 0.0)),
                "humedad": float(day.get("avghumidity", 0.0)),
                "viento": float(day.get("maxwind_kph", 0.0)),
                "presion": 0.0,
                "lluvia": float(day.get("totalprecip_mm", 0.0)),
            }
        else:
            current = data.get("current", {})
            datos_normalizados = {
                "ciudad": nombre_lugar,
                "estacion": nombre_lugar,
                "fecha": current.get("last_updated", "N/A"),
                "temperatura": float(current.get("temp_c", 0.0)),
                "humedad": float(current.get("humidity", 0.0)),
                "viento": float(current.get("wind_kph", 0.0)),
                "presion": float(current.get("pressure_mb", 0.0)),
                "lluvia": float(current.get("precip_mm", 0.0)),
            }

        datos_normalizados["alertas"] = alert_service.evaluar_alertas(datos_normalizados)

        return datos_normalizados

    except Exception as e:
        logging.error(f"Error en normalización: {e}")
        return {
            "error": "Error al procesar los datos",
            "ciudad": "Error",
            "temperatura": 0
        }
