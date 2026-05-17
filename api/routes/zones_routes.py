from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List
from api.dependencies import get_db
from schemas.zones_schema import ZoneCreate, ZoneUpdate, ZoneOut
from db.models import Zona as Zone, Usuario
from api.security import require_roles


router = APIRouter(tags=["Zones"])

@router.get("/", response_model=List[ZoneOut], summary="Listar zonas geográficas")
async def list_zones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles("admin", "tecnico", "visualizador"))
):
    stmt = select(Zone).offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()

@router.get("/{id_zona}", response_model=ZoneOut, summary="Obtener zona por ID")
def get_zone(id_zona: int, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(require_roles("admin", "tecnico", "visualizador"))):
    zone = db.get(Zone, id_zona)
    if not zone:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    return zone

@router.post("/", response_model=ZoneOut, status_code=status.HTTP_201_CREATED, summary="Crear nueva zona")
async def create_zone(zone_in: ZoneCreate, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(require_roles("admin"))):
    zone = Zone(**zone_in.model_dump())
    db.add(zone)
    try:
        db.commit()
        db.refresh(zone)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una zona con ese municipio o código INE")
    return zone

@router.put("/{id_zona}", response_model=ZoneOut, summary="Actualizar datos de una zona")
def update_zone(id_zona: int, zone_in: ZoneUpdate, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(require_roles("admin", "tecnico"))):
    zone = db.get(Zone, id_zona)
    if not zone:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    update_data = zone_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(zone, key, value)
    db.commit()
    db.refresh(zone)
    return zone

@router.delete("/{id_zona}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar una zona")
def delete_zone(id_zona: int, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(require_roles("admin"))):
    zone = db.get(Zone, id_zona)
    if not zone:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    db.delete(zone)
    db.commit()
