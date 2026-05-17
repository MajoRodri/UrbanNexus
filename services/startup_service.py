import json
import os
from db.database import SessionLocal
from db.models import Usuario, Zona, Medicion
from utils.security import hash_password

_CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'municipios.json')


def _load_catalog():
    with open(_CATALOG_PATH, encoding='utf-8') as f:
        return json.load(f)


def create_default_superadmin():
    db = SessionLocal()
    try:
        usuario_existente = db.query(Usuario).filter(Usuario.rol == "admin").first()
        if usuario_existente:
            print("Superadmin ya existente.")
            return
        superadmin = Usuario(
            id_empleado="E0000P",
            nombres="Admin",
            apellidos="UrbanNexus",
            email=os.getenv("EMAIL_FROM", "admin@urbannexus.com"),
            password_hash=hash_password("Admin1234"),
            rol="admin",
            activo=True
        )
        db.add(superadmin)
        db.commit()
        print("Superadmin creado correctamente.")
    finally:
        db.close()


def seed_zones_from_catalog():
    """Sincroniza la tabla zonas con config/municipios.json: crea las que faltan, elimina las que no están."""
    try:
        catalog = _load_catalog()
    except Exception as e:
        print(f"Error al cargar catálogo de distritos: {e}")
        return

    valid_names = set(catalog.keys())

    db = SessionLocal()
    try:
        to_delete = db.query(Zona).filter(~Zona.id_estacion.in_(valid_names)).all()
        for zona in to_delete:
            db.query(Medicion).filter(Medicion.id_zona == zona.id).delete()
            db.delete(zona)
        if to_delete:
            db.commit()
            print(f"Zonas eliminadas (fuera del catálogo): {len(to_delete)}")

        creadas = 0
        for nombre in valid_names:
            existing = db.query(Zona).filter(Zona.cod_ine == nombre).first()
            if not existing:
                zona = Zona(
                    municipio=nombre,
                    cod_ine=nombre,
                    id_estacion=nombre,
                    estacion_referencia=nombre
                )
                db.add(zona)
                creadas += 1
        if creadas:
            db.commit()
            print(f"Zonas inicializadas desde catálogo: {creadas}")
    except Exception as e:
        db.rollback()
        print(f"Error al sincronizar zonas: {e}")
    finally:
        db.close()
