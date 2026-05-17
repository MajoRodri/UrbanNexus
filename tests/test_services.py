import pytest

from services.normalizer_service import normalizar_datos_clima
from services.alert_service import AlertService


def test_normalizer_returns_zero_rain_without_precipitation():
    raw_data = {
        "location": {"name": "Madrid"},
        "current": {
            "last_updated": "2026-05-12 12:00",
            "temp_c": 20.0,
            "humidity": 50,
            "wind_kph": 18.0,
            "pressure_mb": 1015.0,
            "precip_mm": 0.0
        }
    }

    normalized = normalizar_datos_clima(raw_data)

    assert normalized["lluvia"] == 0.0
    assert isinstance(normalized["lluvia"], float)


def test_alert_service_returns_list():
    service = AlertService()

    data = {
        "temperatura": 20.0,
        "viento": 10.0,
        "lluvia": 0.0,
        "humedad": 50
    }

    alertas = service.evaluar_alertas(data)

    assert isinstance(alertas, list)


def test_alert_service_no_alerts_with_normal_weather():
    service = AlertService()

    data = {
        "temperatura": 20.0,
        "viento": 10.0,
        "lluvia": 0.0,
        "humedad": 50
    }

    alertas = service.evaluar_alertas(data)

    assert alertas == []
