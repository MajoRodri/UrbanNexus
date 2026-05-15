# =====================================================================
# TU CÓDIGO ORIGINAL (MANTENIDO EXACTAMENTE IGUAL, SIN BORRAR NADA)
# =====================================================================
import pytest
from unittest.mock import MagicMock
from repositories.sqlite_repository import SQLiteRepository, RecordNotFoundError


@pytest.fixture
def repo():
    mock_db = MagicMock()
    return SQLiteRepository(mock_db)


def test_create_zone(repo):
    repo.db.add = MagicMock()
    repo.db.commit = MagicMock()
    repo.db.refresh = MagicMock()

    result = repo.create_zone("Madrid", "1234", 1, "Estacion A")

    assert repo.db.add.called
    assert repo.db.commit.called


def test_get_zone_by_id(repo):
    fake_obj = MagicMock()
    repo.db.query().filter().first.return_value = fake_obj

    result = repo.get_zone_by_id(1)

    assert result == fake_obj


def test_record_not_found(repo):
    repo.db.query().filter().first.return_value = None

    with pytest.raises(RecordNotFoundError):
        repo.get_zone_by_id(999)


def test_delete_zone(repo):
    fake_obj = MagicMock()
    repo.db.query().filter().first.return_value = fake_obj

    repo.db.delete = MagicMock()
    repo.db.commit = MagicMock()

    result = repo.delete_zone(1)

    assert repo.db.delete.called


# =====================================================================
# LO NUEVO: TEST PARA VALIDAR QUE EL CLIMA SE ACTUALIZA Y EVITA EL NaN
# =====================================================================
def test_update_zone_climate(repo):
    """
    Verifica que al actualizar el clima de una zona, los datos de
    temperatura, humedad, viento y lluvia se asignen correctamente
    y dejen de ser nulos en la base de datos.
    """
    # 1. Creamos el objeto simulado que representa la fila de la zona
    fake_zone = MagicMock()
    fake_zone.temperatura = None
    fake_zone.humedad = None
    fake_zone.viento = None
    fake_zone.lluvia = None
    
    # 2. Forzamos a que las consultas de SQLAlchemy devuelvan nuestra zona
    repo.db.query().filter().first.return_value = fake_zone
    repo.db.commit = MagicMock()

    # 3. Ejecutamos el nuevo método pasándole datos numéricos reales
    result = repo.update_zone_climate(
        zona_id=1, 
        temperatura=20.5, 
        humedad=65, 
        viento=15.2, 
        lluvia=0.5
    )

    # 4. Aserciones para asegurar que los datos guardados son correctos
    assert fake_zone.temperatura == 20.5
    assert fake_zone.humedad == 65
    assert fake_zone.viento == 15.2
    assert fake_zone.lluvia == 0.5
    
    # Verificamos que se llamó al guardado definitivo
    assert repo.db.commit.called
    assert result == fake_zone