import pytest

from services.weather_api_service import WeatherAPIService


_FAKE_RESPONSE = {
    "location": {
        "name": "Madrid",
        "country": "Spain",
        "lat": 40.42,
        "lon": -3.7
    },
    "current": {
        "last_updated": "2024-01-01 12:00",
        "temp_c": 22.5,
        "humidity": 55,
        "wind_kph": 15.1,
        "pressure_mb": 1015.0,
        "precip_mm": 0.0
    }
}


class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self.json_data


class FakeSession:
    def get(self, url, params=None, timeout=10):
        return FakeResponse(_FAKE_RESPONSE)


class FakeSessionError:
    def get(self, *args, **kwargs):
        raise Exception("Error simulado")


@pytest.fixture
def api_service(monkeypatch):
    monkeypatch.setenv("WEATHERAPI_KEY", "fake_api_key")
    monkeypatch.setattr(
        "services.weather_api_service.get_retry_session",
        lambda: FakeSession()
    )
    return WeatherAPIService()


def test_weather_api_service_init(api_service):
    assert api_service.api_key == "fake_api_key"


def test_weather_api_service_no_api_key(monkeypatch):
    monkeypatch.delenv("WEATHERAPI_KEY", raising=False)

    with pytest.raises(ValueError):
        WeatherAPIService()


def test_get_weather_by_coordinates_success(api_service):
    result = api_service.obtener_clima_por_coordenadas(40.4168, -3.7038)

    assert result is not None
    assert result["location"]["name"] == "Madrid"
    assert result["current"]["temp_c"] == 22.5


def test_get_weather_by_coordinates_error(monkeypatch):
    monkeypatch.setenv("WEATHERAPI_KEY", "fake_api_key")
    monkeypatch.setattr(
        "services.weather_api_service.get_retry_session",
        lambda: FakeSessionError()
    )

    service = WeatherAPIService()
    result = service.obtener_clima_por_coordenadas(40.4168, -3.7038)

    assert result is None


def test_get_weather_by_municipality_success(api_service):
    result = api_service.obtener_clima_por_municipio("Madrid")

    assert result is not None
    assert result["location"]["name"] == "Madrid"


def test_get_weather_by_municipality_error(monkeypatch):
    monkeypatch.setenv("WEATHERAPI_KEY", "fake_api_key")
    monkeypatch.setattr(
        "services.weather_api_service.get_retry_session",
        lambda: FakeSessionError()
    )

    service = WeatherAPIService()
    result = service.obtener_clima_por_municipio("Madrid")

    assert result is None
