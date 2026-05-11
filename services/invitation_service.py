import secrets
import string
from datetime import datetime, timedelta
from db.models import Invitacion
from db.database import SessionLocal

#Roles permitidos en el sistema
ROLES_PERMITIDOS = {"admin", "tecnico", "visualizador"}

#Generar codigo alfanumerico aleatorio 
def generate_invitation_code(rol: str, length: int = 8) -> str:
    
    prefijo_rol = {
        "admin": "ADM",
        "tecnico": "TEC",
        "visualizador": "VIS"
    }

    if rol not in prefijo_rol:
        raise ValueError("Rol no valido")

    #Generate random code
    codigo_random = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    return f"{prefijo_rol[rol]}-{codigo_random}"

#Generate a random code for the invitation
def generate_invitation(db, email: str, rol: str, creado_por: str | None = None) -> Invitacion:
    
    if rol not in ROLES_PERMITIDOS:
        raise ValueError("Rol no válido.")

    while True:
        codigo = generate_invitation_code(rol)

        invitacion_existente = db.query(Invitacion).filter(
            Invitacion.codigo == codigo
        ).first()

        if not invitacion_existente:
            break

    invitacion = Invitacion(
        codigo=codigo,
        email=email,
        rol=rol,
        usado=False,
        expira_en=datetime.utcnow() + timedelta(days=7),
        creado_por=creado_por
    )

    db.add(invitacion)
    db.commit()
    db.refresh(invitacion)

    return invitacion

##Validamos una invitacion antes de registrar el usuario
def validate_invitation(db, codigo: str, email: str):
    invitacion = db.query(Invitacion).filter(
        Invitacion.codigo == codigo
    ).first()
    if not invitacion:
        raise ValueError("Invitación no encontrada.")
    if invitacion.email != email:
        raise ValueError("El email no coincide con la invitación.")
    if invitacion.usada:
        raise ValueError("La invitación ya ha sido usada.")
    if invitacion.expiracion < datetime.utcnow():
        raise ValueError("La invitación ha expirado.")
    return invitacion

##Definimos la funcion que indica si la invitacion ya fue usada
def mark_invitation_as_used(db, invitacion: Invitacion) -> None:
    invitacion.usada = True
    db.commit()
    
