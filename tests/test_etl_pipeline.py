import pandas as pd

from etl.pipeline import run_pipeline
from etl.extract import extract_records, extract_station_reference
from etl.transform import transform
from etl.load import sync_zones, load_measurements, log_execution


# =====================================================
# TEST 1: EXTRACT records
# =====================================================

def test_extract_records():
    df = extract_records()

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


# =====================================================
# TEST 2: EXTRACT station reference
# =====================================================

def test_extract_station_reference():
    ref = extract_station_reference()

    assert isinstance(ref, list)
    assert "id_estacion" in ref[0]


# =====================================================
# TEST 3: TRANSFORM integrado en pipeline
# =====================================================

def test_transform_integrated():

    df = pd.DataFrame([
        {
            "estacion_id": "E1",
            "fecha": "10-05-2026 10:00",
            "temperatura": 25,
            "humedad": 50,
            "viento": 10,
            "lluvia": 0
        }
    ])

    referencia = [{"id_estacion": "E1"}]

    from etl.transform import transform

    result_df, stats = transform(df, referencia)

    assert len(result_df) == 1
    assert stats["filas_leidas"] == 1


# =====================================================
# TEST 4: SYNC ZONES
# =====================================================

def test_sync_zones(db_session):

    referencia = [
        {
            "municipio": "Madrid",
            "cod_ine": "28079",
            "id_estacion": "E1",
            "estacion_referencia": "Retiro"
        }
    ]

    mapa = sync_zones(db_session, referencia)

    assert "E1" in mapa
    assert isinstance(mapa["E1"], list)


# =====================================================
# TEST 5: LOAD measurements
# =====================================================

def test_load_measurements(db_session):

    df = pd.DataFrame([
        {
            "estacion_id": "E1",
            "fecha_dt": pd.to_datetime("2026-05-10 10:00"),
            "temperatura": 25,
            "humedad": 50,
            "viento": 10,
            "lluvia": 0
        }
    ])

    mapa = {"E1": [1]}

    insertadas, omitidas = load_measurements(db_session, df, mapa)

    assert insertadas >= 0
    assert isinstance(omitidas, int)


# =====================================================
# TEST 6: LOG execution
# =====================================================

def test_log_execution(db_session):

    stats = {
        "filas_leidas": 10,
        "filas_insertadas": 5,
        "filas_modificadas": 0,
        "filas_descartadas": 3,
        "duplicados_eliminados": 2,
    }

    log = log_execution(
        db_session,
        origen="test",
        stats=stats
    )

    assert log.id is not None
    assert log.filas_leidas == 10


# =====================================================
# TEST 7: PIPELINE COMPLETO
# =====================================================

def test_run_pipeline(db_session):

    result = run_pipeline(db_session)

    assert isinstance(result, dict)
    assert "estado" in result
    assert result["estado"] in ["OK", "ERROR"]