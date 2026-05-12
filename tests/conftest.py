import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base


# =====================================================
# TEST DATABASE FIXTURE (SQLite en memoria)
# =====================================================
# Este fixture crea una base de datos temporal en memoria
# para los tests de integración.
#
# Permite ejecutar operaciones reales de SQLAlchemy
# sin afectar la base de datos del proyecto.
#
# Se recrea en cada ejecución de test para asegurar
# aislamiento y evitar efectos secundarios entre pruebas.
# =====================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db_session():
    """
    Proporciona una sesión de base de datos aislada para tests.

    - Crea todas las tablas necesarias antes del test
    - Proporciona una sesión activa de SQLAlchemy
    - Cierra la sesión al finalizar el test

    Garantiza que cada test tenga un entorno limpio y reproducible.
    """

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()