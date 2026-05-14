from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.security import require_roles
from db.models import Usuario

from db.database import get_db
from schemas.invitation_schema import (
    InvitationCreateRequest,
    InvitationResponse
)

from services.invitation_service import generate_invitation
from services.email_service import send_invitation_email


router = APIRouter(
    prefix="/invitations",
    tags=["Invitations"]
)


@router.post(
    "/create",
    response_model=InvitationResponse
)
def create_invitation_endpoint(
    request: InvitationCreateRequest,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles("admin"))
):

    try:
        invitacion = generate_invitation(
            db=db,
            nombres=request.nombres,
            apellidos=request.apellidos,
            email=request.email,
            rol=request.rol
        )

        send_invitation_email(
            email_destino="adminurbannexus@gmail.com",
            codigo=invitacion.codigo,
            rol=invitacion.rol,
            nombres=request.nombres,
            apellidos=request.apellidos
        )

        return invitacion

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )