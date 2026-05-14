"""
TESTS DE API ROUTES (FASTAPI)

Objetivo:
Validar el correcto funcionamiento de los endpoints REST del sistema UrbanNexus.

Estos tests comprueban:
- Creación de zonas y registros
- Consulta de datos individuales
- Eliminación de registros
- Manejo de errores (404)
- Respuestas HTTP correctas (200, 201, 204)

IMPORTANTE:
Cada test es independiente y crea sus propios datos.
No depende del estado de otros tests ni de ejecuciones previas.
"""

import pytest
from fastapi.testclient import TestClient

from main_api import app
from db.database import Base, engine, SessionLocal

from db.models import Usuario
from utils.jwt import create_access_token

client = TestClient(app)

def create_test_admin(db):
    existing_admin = db.query(Usuario).filter(
        Usuario.id_empleado == "E0000P"
    ).first()

    if existing_admin:
        return existing_admin

    admin = Usuario(
        id_empleado="E0000P",
        nombres="Test",
        apellidos="Admin",
        email="admin@test.com",
        password_hash="test_hash",
        rol="admin",
        activo=True
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin

def auth_headers():
    token = create_access_token({
        "id_empleado": "E0000P",
        "rol": "admin"
    })

    return {
        "Authorization": f"Bearer {token}"
    }

# =========================================================
# FIXTURE: RESETEO DE BASE DE DATOS (AISLAMIENTO DE TESTS)
# =========================================================

@pytest.fixture(autouse=True)
def reset_db():
    """
    Asegura que cada test parte de una base de datos limpia.

    Esto evita:
    - datos residuales de otros tests
    - conflictos de IDs
    - errores 404 inesperados
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# =========================================================
# TEST 1: ROOT ENDPOINT
# =========================================================

def test_root_endpoint():
    """
    Verifica que la API responde correctamente en la raíz.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "UrbanNexus API funcionando" in response.json()["message"]


# =========================================================
# TEST 2: CREAR ZONA
# =========================================================

def test_create_zone():

    db = SessionLocal()
    create_test_admin(db)
    db.close()

    payload = {
        "municipio": "Madrid",
        "cod_ine": "28079",
        "id_estacion": "E1",
        "estacion_referencia": "Retiro"
    }

    response = client.post(
        "/api/v1/zones/",
        json=payload,
        headers=auth_headers()
    )

    assert response.status_code == 201
    assert response.json()["municipio"] == "Madrid"


# =========================================================
# TEST 3: OBTENER ZONA
# =========================================================

def test_get_zone():
    """
    Verifica que una zona creada puede ser consultada correctamente.
    """

    db = SessionLocal()
    create_test_admin(db)
    db.close()

    client.post(
        "/api/v1/zones/",
        json={
            "municipio": "Madrid",
            "cod_ine": "28079",
            "id_estacion": "E1",
            "estacion_referencia": "Retiro"
        },
        headers=auth_headers()
    )

    # Consultar zona
    response = client.get(
        "/api/v1/zones/1",
        headers=auth_headers()
    )

    assert response.status_code == 200
    assert response.json()["municipio"] == "Madrid"


# =========================================================
# TEST 4: ZONA NO ENCONTRADA
# =========================================================

def test_get_zone_not_found():
    """
    Verifica que una zona inexistente devuelve 404.
    """

    db = SessionLocal()
    create_test_admin(db)
    db.close()

    response = client.get(
        "/api/v1/zones/999",
        headers=auth_headers()
    )

    assert response.status_code == 404


# =========================================================
# TEST 5: CREAR REGISTRO CLIMÁTICO
# =========================================================

def test_create_record():
    """
    Verifica la creación de un registro climático.

    IMPORTANTE:
    Requiere una zona previa.
    """

    db = SessionLocal()
    create_test_admin(db)
    db.close()

    # Crear zona primero
    client.post(
        "/api/v1/zones/",
        json={
            "municipio": "Madrid",
            "cod_ine": "28079",
            "id_estacion": "E1",
            "estacion_referencia": "Retiro"
        },
        headers=auth_headers()
    )

    payload = {
        "fecha": "2026-05-10T10:00:00",
        "temperatura": 25,
        "humedad": 50,
        "viento": 10,
        "lluvia": 0,
        "id_zona": 1
    }

    response = client.post(
        "/api/v1/records/",
        json=payload,
        headers=auth_headers()
    )

    assert response.status_code == 201
    assert response.json()["temperatura"] == 25


# =========================================================
# TEST 6: ELIMINAR REGISTRO
# =========================================================

def test_delete_record():
    """
    Verifica la eliminación de un registro climático.
    """

    db = SessionLocal()
    create_test_admin(db)
    db.close()

    # Crear zona
    client.post(
        "/api/v1/zones/",
        json={
            "municipio": "Madrid",
            "cod_ine": "28079",
            "id_estacion": "E1",
            "estacion_referencia": "Retiro"
        },
        headers=auth_headers()
    )

    client.post(
        "/api/v1/records/",
        json={
            "fecha": "2026-05-10T10:00:00",
            "temperatura": 25,
            "humedad": 50,
            "viento": 10,
            "lluvia": 0,
            "id_zona": 1
        },
        headers=auth_headers()
    )

    # Eliminar registro
    response = client.delete(
        "/api/v1/records/1",
        headers=auth_headers()
    )

    assert response.status_code == 204
    