from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from utils.jwt import create_access_token

from db.database import get_db
from db.models import Usuario

from schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    UserResponse
)

from services.invitation_service import (
    validate_invitation,
    mark_invitation_as_used
)

from utils.employee_id import generate_employee_id, generate_unique_id
from utils.security import hash_password, verify_password


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    # Verificar si el email ya existe
    usuario_existente = db.query(Usuario).filter(
        Usuario.email == request.email
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado."
        )

    # Validar invitación
    invitacion = validate_invitation(
        db,
        request.codigo_invitacion,
        request.email
    )

    # Obtener rol desde invitación
    rol = invitacion.rol

    # Generar ID único
    id_empleado = generate_unique_id(
        rol,
        db,
        Usuario
    )

    # Crear usuario
    usuario = Usuario(
        id_empleado=id_empleado,
        nombres=request.nombres,
        apellidos=request.apellidos,
        email=request.email,
        password_hash=hash_password(request.password),
        rol=rol,
        activo=True
    )

    db.add(usuario)

    # Marcar invitación usada
    mark_invitation_as_used(db, invitacion)

    db.commit()
    db.refresh(usuario)

    return usuario


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    # Buscar usuario por email
    usuario = db.query(Usuario).filter(
        Usuario.id_empleado == request.id_empleado
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas."
        )

    # Verificar contraseña
    if not verify_password(
        request.password,
        usuario.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas."
        )

    # Verificar usuario activo
    if not usuario.activo:
        raise HTTPException(
            status_code=403,
            detail="La cuenta está desactivada."
        )

    # Generar JWT
    access_token = create_access_token(
        data={
            "sub": usuario.id_empleado,
"id_empleado": usuario.id_empleado,
"rol": usuario.rol
        }
    )

    # Respuesta final
    return {
        "message": "Login correcto.",
        "access_token": access_token,
        "token_type": "bearer",
        "id_empleado": usuario.id_empleado,
        "rol": usuario.rol
    }