from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.security import require_roles
from db.models import Usuario
from repositories.sqlite_repository import SQLiteRepository, RecordNotFoundError

router = APIRouter(tags=["Users"])


@router.get("/", summary="Listar todos los usuarios")
def list_users(
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_roles("admin"))
):
    repo = SQLiteRepository(db)
    return repo.list_all_users()


@router.put("/{id_empleado}/role", summary="Cambiar el rol de un usuario")
def update_user_role(
    id_empleado: str,
    rol: str,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_roles("admin"))
):
    if rol not in ["admin", "tecnico", "visualizador"]:
        raise HTTPException(status_code=400, detail="Rol no válido")

    try:
        repo = SQLiteRepository(db)
        return repo.update_user_role(id_empleado, rol)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{id_empleado}/state", summary="Activar o desactivar un usuario")
def update_user_state(
    id_empleado: str,
    activo: bool,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_roles("admin"))
):
    try:
        repo = SQLiteRepository(db)
        return repo.update_user_state(id_empleado, activo)
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{id_empleado}", summary="Eliminar un usuario")
def delete_user(
    id_empleado: str,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_roles("admin"))
):
    try:
        repo = SQLiteRepository(db)
        repo.delete_user(id_empleado)
        return {"message": "Usuario eliminado correctamente"}
    except RecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
