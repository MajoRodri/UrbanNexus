import pytest

from services.alert_service import AlertService


@pytest.fixture
def alert_service():
    """
    Fixture que crea una instancia del servicio de alertas.
    """
    return AlertService()


def build_weather_data(**kwargs):
    """
    Genera un registro válido base para reutilizar en tests.
    """

    data = {
        "fecha": "2026-05-09 10:00:00",
        "temperatura": 20,
        "viento": 10,
        "lluvia": 0,
        "humedad": 50
    }

    data.update(kwargs)

    return data


# =====================================================
# TEST 1: alerta roja por calor extremo
# =====================================================

def test_alerta_roja_calor(alert_service):

    data = build_weather_data(
        temperatura=42,
        viento=10,
        lluvia=0,
        humedad=50
    )

    result = alert_service.evaluar_alertas(data)

    assert "ROJA_CALOR" in result


# =====================================================
# TEST 2: alerta naranja por calor
# =====================================================

def test_alerta_naranja_calor(alert_service):

    data = build_weather_data(
        temperatura=36,
        viento=10,
        lluvia=0,
        humedad=50
    )

    result = alert_service.evaluar_alertas(data)

    assert "NARANJA_CALOR" in result


# =====================================================
# TEST 3: alerta roja por frío extremo
# =====================================================

def test_alerta_roja_frio(alert_service):

    data = build_weather_data(
        temperatura=-10,
        viento=5,
        lluvia=0,
        humedad=40
    )

    result = alert_service.evaluar_alertas(data)

    assert "ROJA_FRIO" in result


# =====================================================
# TEST 4: alerta naranja por viento
# =====================================================

def test_alerta_naranja_viento(alert_service):

    data = build_weather_data(
        temperatura=20,
        viento=50,
        lluvia=0,
        humedad=40
    )

    result = alert_service.evaluar_alertas(data)

    assert "NARANJA_VIENTO" in result


# =====================================================
# TEST 5: alerta roja por lluvia
# =====================================================

def test_alerta_roja_lluvia(alert_service):

    data = build_weather_data(
        temperatura=20,
        viento=10,
        lluvia=35,
        humedad=60
    )

    result = alert_service.evaluar_alertas(data)

    assert "ROJA_LLUVIA" in result


# =====================================================
# TEST 6: alerta por humedad alta
# =====================================================

def test_alerta_humedad(alert_service):

    data = build_weather_data(
        temperatura=22,
        viento=10,
        lluvia=0,
        humedad=95
    )

    result = alert_service.evaluar_alertas(data)

    assert "NARANJA_HUMEDAD" in result


# =====================================================
# TEST 7: clima normal devuelve VERDE
# =====================================================

def test_alerta_verde(alert_service):

    data = build_weather_data(
        temperatura=22,
        viento=10,
        lluvia=0,
        humedad=50
    )

    result = alert_service.evaluar_alertas(data)

    assert result == ["VERDE"]


# =====================================================
# TEST 8: datos inválidos
# =====================================================

def test_alerta_datos_invalidos(alert_service):

    data = build_weather_data(
        temperatura="dato_corrupto",
        viento=None,
        lluvia="error",
        humedad=[]
    )

    result = alert_service.evaluar_alertas(data)

    assert result == []
    