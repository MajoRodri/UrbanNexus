import json
import pytest

import repositories.json_repository as repo


# =====================================================
# FIXTURE: archivo JSON temporal
# =====================================================

@pytest.fixture
def temp_json_file(tmp_path, monkeypatch):
    """
    Crea un archivo JSON temporal y hace que el repository use ese archivo
    en vez del archivo real data/registros_climaticos.json.
    """

    ruta_archivo = tmp_path / "test_data.json"

    # Dejamos el archivo inicializado con una lista vacía
    ruta_archivo.write_text("[]", encoding="utf-8")

    # El repository actual no usa DATA_FILE.
    # Usa repo._repo.file_path, así que parcheamos esa ruta.
    monkeypatch.setattr(repo._repo, "file_path", str(ruta_archivo))

    return ruta_archivo


# =====================================================
# TEST guardar_registro()
# =====================================================

def test_save_record_correctly(temp_json_file):
    """
    Comprueba que guardar_registro añade un registro al JSON.
    """

    registro = {
        "id": "1",
        "municipio": "Madrid",
        "fecha": "22/04/2026",
        "fuente": "manual",
        "temperatura": 20
    }

    resultado = repo.guardar_registro(registro)

    assert resultado is True

    datos_guardados = json.loads(
        temp_json_file.read_text(encoding="utf-8")
    )

    assert len(datos_guardados) == 1
    assert datos_guardados[0]["municipio"] == "Madrid"


def test_save_multiple_records(temp_json_file):
    """
    Comprueba que se pueden guardar varios registros.
    """

    registro_1 = {
        "id": "1",
        "municipio": "Madrid",
        "fecha": "22/04/2026",
        "fuente": "manual"
    }

    registro_2 = {
        "id": "2",
        "municipio": "Sevilla",
        "fecha": "22/04/2026",
        "fuente": "manual"
    }

    repo.guardar_registro(registro_1)
    repo.guardar_registro(registro_2)

    datos_guardados = json.loads(
        temp_json_file.read_text(encoding="utf-8")
    )

    assert len(datos_guardados) == 2
    assert datos_guardados[0]["municipio"] == "Madrid"
    assert datos_guardados[1]["municipio"] == "Sevilla"


# =====================================================
# TEST filter_records()
# =====================================================

def test_filter_records_empty_file(temp_json_file):
    """
    Si el JSON está vacío, filter_records debe devolver lista vacía.
    """

    resultado = repo.filter_records(municipio="Madrid")

    assert resultado == []


def test_filter_records_by_municipality(temp_json_file):
    """
    Comprueba que filtra correctamente por municipio.
    """

    registros = [
        {
            "id": "1",
            "municipio": "Madrid",
            "fecha": "22/04/2026",
            "fuente": "manual"
        },
        {
            "id": "2",
            "municipio": "Sevilla",
            "fecha": "22/04/2026",
            "fuente": "manual"
        }
    ]

    temp_json_file.write_text(json.dumps(registros), encoding="utf-8")

    resultado = repo.filter_records(municipio="Madrid")

    assert len(resultado) == 1
    assert resultado[0]["municipio"] == "Madrid"


def test_filter_records_by_municipality_case_insensitive(temp_json_file):
    """
    Comprueba que el filtro por municipio no falla por mayúsculas/minúsculas.
    """

    registros = [
        {
            "id": "1",
            "municipio": "Madrid",
            "fecha": "22/04/2026",
            "fuente": "manual"
        }
    ]

    temp_json_file.write_text(json.dumps(registros), encoding="utf-8")

    resultado = repo.filter_records(municipio="madrid")

    assert len(resultado) == 1
    assert resultado[0]["municipio"] == "Madrid"


def test_filter_records_by_date(temp_json_file):
    """
    Comprueba que filtra correctamente por fecha exacta.

    Ojo: el repository compara la fecha exacta.
    """

    registros = [
        {
            "id": "1",
            "municipio": "Madrid",
            "fecha": "22/04/2026",
            "fuente": "manual"
        },
        {
            "id": "2",
            "municipio": "Madrid",
            "fecha": "23/04/2026",
            "fuente": "manual"
        }
    ]

    temp_json_file.write_text(json.dumps(registros), encoding="utf-8")

    resultado = repo.filter_records(fecha="22/04/2026")

    assert len(resultado) == 1
    assert resultado[0]["fecha"] == "22/04/2026"


def test_filter_records_by_source(temp_json_file):
    """
    Comprueba que filtra correctamente por fuente.
    """

    registros = [
        {
            "id": "1",
            "municipio": "Madrid",
            "fecha": "22/04/2026",
            "fuente": "manual"
        },
        {
            "id": "2",
            "municipio": "Madrid",
            "fecha": "22/04/2026",
            "fuente": "weatherapi"
        }
    ]

    temp_json_file.write_text(json.dumps(registros), encoding="utf-8")

    resultado = repo.filter_records(fuente="manual")

    assert len(resultado) == 1
    assert resultado[0]["fuente"] == "manual"


def test_filter_records_by_municipality_date_source(temp_json_file):
    """
    Comprueba que se pueden combinar municipio, fecha y fuente.
    """

    registros = [
        {
            "id": "1",
            "municipio": "Madrid",
            "fecha": "22/04/2026",
            "fuente": "manual"
        },
        {
            "id": "2",
            "municipio": "Madrid",
            "fecha": "22/04/2026",
            "fuente": "weatherapi"
        },
        {
            "id": "3",
            "municipio": "Sevilla",
            "fecha": "22/04/2026",
            "fuente": "manual"
        }
    ]

    temp_json_file.write_text(json.dumps(registros), encoding="utf-8")

    resultado = repo.filter_records(
        municipio="Madrid",
        fecha="22/04/2026",
        fuente="manual"
    )

    assert len(resultado) == 1
    assert resultado[0]["id"] == "1"


# =====================================================
# TEST find_latest_by_municipio_and_source()
# =====================================================

def test_find_latest_record_by_municipality(temp_json_file):
    """
    Comprueba que devuelve el último registro encontrado para un municipio.

    Nota: en el repository actual, obtener_ultimo_registro recibe fuente,
    pero no la usa internamente. Por eso este test comprueba el comportamiento
    real actual: devuelve el último registro del municipio.
    """

    registros = [
        {
            "id": "1",
            "municipio": "Madrid",
            "fecha": "22/04/2026",
            "fuente": "manual"
        },
        {
            "id": "2",
            "municipio": "Madrid",
            "fecha": "23/04/2026",
            "fuente": "weatherapi"
        },
        {
            "id": "3",
            "municipio": "Sevilla",
            "fecha": "23/04/2026",
            "fuente": "manual"
        }
    ]

    temp_json_file.write_text(json.dumps(registros), encoding="utf-8")

    resultado = repo.find_latest_by_municipio_and_source("Madrid", "manual")

    assert resultado is not None
    assert resultado["id"] == "2"
    assert resultado["municipio"] == "Madrid"


def test_find_latest_record_returns_none_if_not_found(temp_json_file):
    """
    Comprueba que devuelve None si no existe el municipio.
    """

    registros = [
        {
            "id": "1",
            "municipio": "Madrid",
            "fecha": "22/04/2026",
            "fuente": "manual"
        }
    ]

    temp_json_file.write_text(json.dumps(registros), encoding="utf-8")

    resultado = repo.find_latest_by_municipio_and_source("Valencia", "manual")

    assert resultado is None

    #para probar py -m pytest tests/test_compare_controller.py 
    #para probar py -m pytest tests/test_compare_controller.py tests/test_json_repository.py 