import os
import time
from typing import Dict, Any, Optional

from services.retry_service import get_retry_session
from services.logging_service import log_info, log_error
from utils.helpers import calcular_distancia


_BASE = "https://opendata.aemet.es/opendata/api"
_CACHE_TTL = 600

_cache_observaciones = {
    "datos": [],
    "timestamp": 0
}


class WeatherAPIService:
    def __init__(self):
        self.api_key = os.getenv("AEMET_API_KEY")

        if not self.api_key:
            raise ValueError("AEMET_API_KEY no encontrada en .env")

        self.session = get_retry_session()

    def _get_datos(self, url: str):
        try:
            respuesta_meta = self.session.get(
                url,
                params={"api_key": self.api_key},
                timeout=20
            )

            if respuesta_meta.status_code == 429:
                log_error("AEMET ha bloqueado temporalmente por demasiadas peticiones.")
                return None

            respuesta_meta.raise_for_status()

            datos_url = respuesta_meta.json().get("datos")

            if not datos_url:
                log_error(f"AEMET no devolvió URL de datos. Respuesta: {respuesta_meta.text}")
                return None

            respuesta_datos = self.session.get(
                datos_url,
                timeout=20
            )

            respuesta_datos.raise_for_status()

            return respuesta_datos.json()

        except Exception as error:
            log_error(f"Error al obtener datos de AEMET: {type(error).__name__}")
            return None

    def obtener_clima_por_estacion(self, id_estacion: str) -> Optional[Dict[str, Any]]:
        url = f"{_BASE}/observacion/convencional/datos/estacion/{id_estacion}"

        datos = self._get_datos(url)

        if datos:
            datos_ordenados = sorted(
                datos,
                key=lambda obs: obs.get("fint", ""),
                reverse=True
            )   

            log_info(f"Datos obtenidos para estación {id_estacion}")
            return datos_ordenados[0]

        return None

    def _obtener_todas(self) -> list:
        ahora = time.time()

        if (
            _cache_observaciones["datos"]
            and ahora - _cache_observaciones["timestamp"] < _CACHE_TTL
        ):
            log_info("Usando observaciones AEMET en caché")
            return _cache_observaciones["datos"]

        datos = self._get_datos(
            f"{_BASE}/observacion/convencional/todas"
        )

        if datos:
            _cache_observaciones["datos"] = datos
            _cache_observaciones["timestamp"] = ahora
            return datos

        return _cache_observaciones["datos"]

    def obtener_clima_por_coordenadas(
        self,
        user_lat: float,
        user_lon: float
    ) -> Optional[Dict[str, Any]]:

        observaciones = self._obtener_todas()

        if not observaciones:
            log_error("AEMET devolvió lista de observaciones vacía")
            return None

        estacion_cercana = None
        distancia_minima = float("inf")

        for obs in observaciones:
            try:
                distancia = calcular_distancia(
                    float(user_lat),
                    float(user_lon),
                    float(obs["lat"]),
                    float(obs["lon"])
                )

                if distancia < distancia_minima:
                    distancia_minima = distancia
                    estacion_cercana = obs

            except (KeyError, ValueError, TypeError):
                continue

        if estacion_cercana:
            log_info(
                f"Estación más cercana: {estacion_cercana.get('ubi')} a {distancia_minima:.2f} km"
            )
            return estacion_cercana

        log_error(f"No se encontró estación válida para lat={user_lat}, lon={user_lon}")
        return None


def obtener_clima_por_coordenadas(lat, lon):
    return WeatherAPIService().obtener_clima_por_coordenadas(lat, lon)


def obtener_clima_por_estacion(id_estacion):
    return WeatherAPIService().obtener_clima_por_estacion(id_estacion)