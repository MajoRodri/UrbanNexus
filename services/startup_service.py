from db.database import SessionLocal
from db.models import Usuario

from utils.security import hash_password


def create_default_superadmin():

    db = SessionLocal()

    try:

        usuario_existente = db.query(Usuario).filter(
            Usuario.rol == "admin"
        ).first()

        if usuario_existente:
            print("Superadmin ya existente.")
            return

        superadmin = Usuario(
            id_empleado="E0000P",
            nombres="Admin",
            apellidos="UrbanNexus",
            email="[EMAIL_FROM]",
            password_hash=hash_password("Admin1234"),
            rol="admin",
            activo=True
        )

        db.add(superadmin)
        db.commit()

        print("Superadmin creado correctamente.")

    finally:
        db.close()