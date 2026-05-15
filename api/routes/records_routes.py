from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List
from api.dependencies import get_db
from schemas.records_schema import RecordCreate, RecordUpdate, RecordOut
from db.models import Medicion as Record, Zona as Zone
from api.security import require_roles
from db.models import Usuario

router = APIRouter()

@router.get("/", response_model=List[RecordOut])
async def list_records(
    skip: int = Query(0, ge=0), 
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_roles("admin", "tecnico", "visualizador"))
):
    stmt = select(Record).offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()

@router.get("/{record_id}", response_model=RecordOut)
async def get_record(record_id: int, db: Session = Depends(get_db)):
    record = db.get(Record, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return record

@router.get("/zone/{id_zona}", response_model=List[RecordOut])
async def records_by_zone(id_zona: int, db: Session = Depends(get_db)):
    stmt = select(Record).where(Record.id_zona == id_zona)
    result = db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=RecordOut, status_code=status.HTTP_201_CREATED)
async def create_record(record_in: RecordCreate, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(require_roles("admin", "tecnico"))):
    zone = db.get(Zone, record_in.id_zona)
    if not zone:
        raise HTTPException(status_code=404, detail="Zona no encontrada")
    record = Record(**record_in.model_dump())
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe un registro para esta zona y fecha")
    return record

@router.put("/{record_id}", response_model=RecordOut)
async def update_record(record_id: int, record_in: RecordUpdate, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(require_roles("admin", "tecnico"))):
    record = db.get(Record, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    update_data = record_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(record_id: int, db: Session = Depends(get_db), usuario_actual: Usuario = Depends(require_roles("admin", "tecnico"))):
    record = db.get(Record, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    db.delete(record)
    db.commit()
