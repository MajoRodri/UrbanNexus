import pandas as pd
import pytest

from etl.transform import transform


# =====================================================
# TEST: TRANSFORMACIÓN Y LIMPIEZA DE DATOS
# =====================================================
# Este conjunto de tests valida la lógica del proceso ETL
# en su fase de TRANSFORMACIÓN.
#
# Se comprueba que:
# - Se eliminan registros incompletos o inválidos
# - Se parsean correctamente las fechas
# - Se eliminan duplicados
# - Se filtran estaciones no válidas según referencia
# - Se generan correctamente las estadísticas del proceso
#
# Esta fase es crítica porque garantiza que solo datos
# fiables lleguen a la base de datos.
# =====================================================


# =====================================================
# TEST 1: eliminación de datos nulos e inválidos
# =====================================================

def test_transform_elimina_datos_invalidos():

    """
    Verifica que los registros con campos obligatorios vacíos,
    nulos o incorrectos son descartados correctamente.

    Esto evita insertar datos corruptos en la base de datos.
    """

    df = pd.DataFrame([
        {
            "estacion_id": "E1",
            "fecha": "10-05-2026 10:00",
            "temperatura": 25,
            "humedad": 50,
            "viento": 10,
            "lluvia": 0
        },
        {
            "estacion_id": None,  # inválido
            "fecha": "10-05-2026 10:00",
            "temperatura": 25,
            "humedad": 50,
            "viento": 10,
            "lluvia": 0
        }
    ])

    referencia = [{"id_estacion": "E1"}]

    df_limpio, stats = transform(df, referencia)

    assert len(df_limpio) == 1
    assert stats["descartados_nulos"] == 1


# =====================================================
# TEST 2: eliminación de duplicados
# =====================================================

def test_transform_elimina_duplicados():

    """
    Verifica que no se permiten registros duplicados
    con el mismo (estacion_id + fecha).

    Evita duplicación de mediciones en la base de datos.
    """

    df = pd.DataFrame([
        {
            "estacion_id": "E1",
            "fecha": "10-05-2026 10:00",
            "temperatura": 25,
            "humedad": 50,
            "viento": 10,
            "lluvia": 0
        },
        {
            "estacion_id": "E1",
            "fecha": "10-05-2026 10:00",
            "temperatura": 26,
            "humedad": 51,
            "viento": 11,
            "lluvia": 0
        }
    ])

    referencia = [{"id_estacion": "E1"}]

    df_limpio, stats = transform(df, referencia)

    assert len(df_limpio) == 1
    assert stats["duplicados_eliminados"] == 1


# =====================================================
# TEST 3: filtrado de estaciones no válidas
# =====================================================

def test_transform_filtra_estaciones_no_validas():

    """
    Verifica que solo se conservan registros de estaciones
    presentes en el catálogo de referencia.

    Esto evita insertar datos de estaciones desconocidas.
    """

    df = pd.DataFrame([
        {
            "estacion_id": "E1",
            "fecha": "10-05-2026 10:00",
            "temperatura": 25,
            "humedad": 50,
            "viento": 10,
            "lluvia": 0
        },
        {
            "estacion_id": "INVALIDA",
            "fecha": "10-05-2026 10:00",
            "temperatura": 30,
            "humedad": 60,
            "viento": 5,
            "lluvia": 0
        }
    ])

    referencia = [{"id_estacion": "E1"}]

    df_limpio, stats = transform(df, referencia)

    assert len(df_limpio) == 1
    assert stats["descartados_sin_zona"] == 1


# =====================================================
# TEST 4: conversión correcta de fechas
# =====================================================

def test_transform_convierte_fechas():

    """
    Verifica que el campo fecha se convierte correctamente
    a datetime para su posterior uso en base de datos.

    Esto es clave para evitar errores de formato en SQL.
    """

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

    df_limpio, _ = transform(df, referencia)

    assert "fecha_dt" in df_limpio.columns
    assert pd.api.types.is_datetime64_any_dtype(df_limpio["fecha_dt"])