import os
import time
from typing import Dict, Any, Optional
from services.retry_service import get_retry_session
from services.logging_service import log_info, log_error
from utils.helpers import calcular_distancia

_cache_observaciones = {"datos": [], "timestamp": 0}
_CACHE_TTL = 300  # 5 minutos

_BASE = "https://opendata.aemet.es/opendata/api"


class WeatherAPIService:
    def __init__(self):
        self.api_key = os.getenv("AEMET_API_KEY")
        if not self.api_key:
            raise ValueError("AEMET_API_KEY no encontrada en .env")
        self.session = get_retry_session()

    def _get_datos(self, url: str) -> list:
        res_meta = self.session.get(url, params={"api_key": self.api_key}, timeout=20)
        res_meta.raise_for_status()
        datos_url = res_meta.json().get("datos")
        if not datos_url:
            return []
        res_datos = self.session.get(datos_url, timeout=20)
        res_datos.raise_for_status()
        return res_datos.json()

    def obtener_clima_por_estacion(self, id_estacion: str) -> Optional[Dict[str, Any]]:
        observaciones = self._obtener_todas()
        if observaciones:
            for obs in observaciones:
                if obs.get("idema") == id_estacion:
                    log_info(f"Estación {id_estacion} encontrada en caché: {obs.get('ubi')}")
                    return obs

        url = f"{_BASE}/observacion/convencional/datos/estacion/{id_estacion}"
        try:
            datos = self._get_datos(url)
            if datos:
                return datos[-1]
        except Exception as e:
            log_error(f"Error al obtener estación {id_estacion}: {e}")

        return None

    def _obtener_todas(self) -> list:
        ahora = time.time()
        if _cache_observaciones["datos"] and ahora - _cache_observaciones["timestamp"] < _CACHE_TTL:
            log_info("Usando observaciones AEMET en caché")
            return _cache_observaciones["datos"]
        try:
            observaciones = self._get_datos(f"{_BASE}/observacion/convencional/todas")
            if observaciones:
                _cache_observaciones["datos"] = observaciones
                _cache_observaciones["timestamp"] = ahora
                return observaciones
        except Exception as e:
            log_error(f"Error al conectar con AEMET: {e}")
        return _cache_observaciones["datos"]

    def obtener_clima_por_coordenadas(self, user_lat: float, user_lon: float) -> Optional[Dict[str, Any]]:
        """Fallback: descarga todas las observaciones y devuelve la estación más cercana."""
        observaciones = self._obtener_todas()

        if not observaciones:
            log_error("AEMET devolvió lista de observaciones vacía")
            return None

        estacion_cercana = None
        distancia_minima = float('inf')
        for obs in observaciones:
            try:
                dist = calcular_distancia(
                    float(user_lat), float(user_lon),
                    float(obs['lat']), float(obs['lon'])
                )
                if dist < distancia_minima:
                    distancia_minima = dist
                    estacion_cercana = obs
            except (KeyError, ValueError, TypeError):
                continue

        if estacion_cercana:
            log_info(f"Estación más cercana: {estacion_cercana.get('ubi')} a {distancia_minima:.2f}km")
        else:
            log_error(f"No se encontró estación válida para lat={user_lat}, lon={user_lon}")
        return estacion_cercana


def obtener_clima_por_coordenadas(lat, lon):
    return WeatherAPIService().obtener_clima_por_coordenadas(lat, lon)


def obtener_clima_por_estacion(id_estacion):
    return WeatherAPIService().obtener_clima_por_estacion(id_estacion)
