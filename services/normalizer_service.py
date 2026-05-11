import logging
# 1. Importamos tu servicio de alertas
from services.alert_service import AlertService

# Instanciamos el servicio para tenerlo listo
alert_service = AlertService()

def normalizar_datos_aemet(data):
    """
    Transforma los datos crudos de AEMET en un formato estándar 
    e integra el sistema de alertas.
    """
    try:
        if not data:
            return {"error": "No hay datos disponibles"}

        # Si es una lista, tomamos el último registro (el más reciente)
        latest = data[-1] if isinstance(data, list) else data
        
        # --- SOLUCIÓN AL NOMBRE ---
        # AEMET guarda el nombre en 'ubi'. Lo asignamos a 'ciudad' para el JS.
        nombre_lugar = latest.get("ubi", "Ubicación Desconocida")

        # 2. Creamos el diccionario base
        def parse_float(val, default=0.0):
            if not val:
                return default
            return float(str(val).replace(",", "."))

        datos_normalizados = {
            "ciudad": nombre_lugar,
            "estacion": nombre_lugar,
            "fecha": latest.get("fint", "N/A"),
            "temperatura": parse_float(latest.get("ta")),
            "humedad": parse_float(latest.get("hr")),
            "viento": parse_float(latest.get("vv")),
            "presion": parse_float(latest.get("pres")),
            "lluvia": 0.0 if str(latest.get("prec", "")).strip().lower() == "ip" else parse_float(latest.get("prec")),
        }

        # 3. LLAMADA MÁGICA: Alertas
        datos_normalizados["alertas"] = alert_service.evaluar_alertas(datos_normalizados)

        return datos_normalizados

    except Exception as e:
        logging.error(f"Error en normalización: {e}")
        return {
            "error": "Error al procesar los datos",
            "ciudad": "Error", # Evitamos el undefined incluso en error
            "temperatura": 0
        }