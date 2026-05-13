import os
from typing import Dict, Any, Optional

from services.retry_service import get_retry_session
from services.logging_service import log_info, log_error


_BASE = "https://api.weatherapi.com/v1"


class WeatherAPIService:
    def __init__(self):
        self.api_key = os.getenv("WEATHERAPI_KEY")

        if not self.api_key:
            raise ValueError("WEATHERAPI_KEY no encontrada en .env")

        self.session = get_retry_session()

    def _get(self, query: str) -> Optional[Dict[str, Any]]:
        try:
            resp = self.session.get(
                f"{_BASE}/current.json",
                params={"key": self.api_key, "q": query, "lang": "es"},
                timeout=10
            )

            if resp.status_code == 429:
                log_error("WeatherAPI ha bloqueado temporalmente por demasiadas peticiones.")
                return None

            if resp.status_code >= 400:
                try:
                    msg = resp.json().get("error", {}).get("message", resp.text[:200])
                except Exception:
                    msg = resp.text[:200]
                log_error(f"WeatherAPI error {resp.status_code} para '{query}': {msg}")
                return None

            return resp.json()

        except Exception as error:
            log_error(f"Error al obtener datos de WeatherAPI: {type(error).__name__}")
            return None

    def _get_historical(self, query: str, fecha: str) -> Optional[Dict[str, Any]]:
        try:
            resp = self.session.get(
                f"{_BASE}/history.json",
                params={"key": self.api_key, "q": query, "dt": fecha, "lang": "es"},
                timeout=10
            )

            if resp.status_code == 429:
                log_error("WeatherAPI ha bloqueado temporalmente por demasiadas peticiones.")
                return None

            if resp.status_code >= 400:
                try:
                    msg = resp.json().get("error", {}).get("message", resp.text[:200])
                except Exception:
                    msg = resp.text[:200]
                log_error(f"WeatherAPI historical error {resp.status_code} para '{query}': {msg}")
                return None

            return resp.json()

        except Exception as error:
            log_error(f"Error al obtener datos históricos de WeatherAPI: {type(error).__name__}")
            return None

    def obtener_clima_por_coordenadas(
        self,
        lat: float,
        lon: float,
        fecha: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        query = f"{lat},{lon}"
        data = self._get_historical(query, fecha) if fecha else self._get(query)
        if data:
            log_info(f"Datos obtenidos para lat={lat}, lon={lon}")
        return data

    def obtener_clima_por_municipio(self, nombre: str, fecha: Optional[str] = None) -> Optional[Dict[str, Any]]:
        data = self._get_historical(nombre, fecha) if fecha else self._get(nombre)
        if data:
            log_info(f"Datos obtenidos para municipio={nombre}")
        return data


def obtener_clima_por_coordenadas(lat, lon):
    return WeatherAPIService().obtener_clima_por_coordenadas(lat, lon)
