import pytest

from services.normalizer_service import normalizar_datos_clima


@pytest.fixture
def sample_weather_data():
    return {
        "location": {
            "name": "Madrid-Retiro"
        },
        "current": {
            "last_updated": "2026-04-27 13:00",
            "temp_c": 22.5,
            "humidity": 60,
            "wind_kph": 36.0,
            "pressure_mb": 1013.0,
            "precip_mm": 0.5
        }
    }


def test_normalize_data_correct(monkeypatch, sample_weather_data):
    def fake_alerts(data):
        return ["alerta_test"]

    monkeypatch.setattr(
        "services.normalizer_service.alert_service.evaluar_alertas",
        fake_alerts
    )

    result = normalizar_datos_clima(sample_weather_data)

    assert result["estacion"] == "Madrid-Retiro"
    assert result["fecha"] == "2026-04-27 13:00"
    assert result["temperatura"] == 22.5
    assert result["humedad"] == 60.0
    assert result["viento"] == 36.0  # km/h sin conversión
    assert result["presion"] == 1013.0
    assert result["lluvia"] == 0.5
    assert result["alertas"] == ["alerta_test"]


def test_normalize_data_dict(monkeypatch):
    data = {
        "location": {"name": "Madrid"},
        "current": {
            "last_updated": "2026-04-27 13:00",
            "temp_c": 20.0,
            "humidity": 50,
            "wind_kph": 18.0,
            "pressure_mb": 1000.0,
            "precip_mm": 0.0
        }
    }

    monkeypatch.setattr(
        "services.normalizer_service.alert_service.evaluar_alertas",
        lambda x: []
    )

    result = normalizar_datos_clima(data)

    assert result["estacion"] == "Madrid"
    assert result["temperatura"] == 20.0
    assert result["humedad"] == 50.0
    assert result["viento"] == 18.0  # km/h sin conversión
    assert result["presion"] == 1000.0
    assert result["lluvia"] == 0.0
    assert result["alertas"] == []


def test_normalize_data_none():
    result = normalizar_datos_clima(None)

    assert "error" in result


def test_normalize_data_empty_dict(monkeypatch):
    monkeypatch.setattr(
        "services.normalizer_service.alert_service.evaluar_alertas",
        lambda x: []
    )

    result = normalizar_datos_clima({})

    assert result["estacion"] == "Ubicación Desconocida"
    assert result["fecha"] == "N/A"
    assert result["temperatura"] == 0.0
    assert result["humedad"] == 0.0
    assert result["viento"] == 0.0
    assert result["presion"] == 0.0
    assert result["lluvia"] == 0.0
    assert result["alertas"] == []


def test_normalize_data_internal_error(monkeypatch):
    class BrokenData:
        def get(self, *args, **kwargs):
            raise Exception("error forzado")

    result = normalizar_datos_clima(BrokenData())

    assert "error" in result
