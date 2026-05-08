from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List
from api.dependencies import get_db
from schemas.records_schema import RecordCreate, RecordUpdate, RecordOut
from db.models import Record, Zone

router = APIRouter()

@router.get("/", response_model=List[RecordOut])
def list_records(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    result = db.execute(select(Record).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{record_id}", response_model=RecordOut)
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = db.get(Record, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return record

@router.get("/zone/{zone_id}", response_model=List[RecordOut])
def records_by_zone(zone_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(Record).where(Record.zone_id == zone_id))
    return result.scalars().all()

@router.post("/", response_model=RecordOut, status_code=status.HTTP_201_CREATED)
def create_record(record_in: RecordCreate, db: Session = Depends(get_db)):
    zone = db.get(Zone, record_in.zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zona no encontrada")

    record = Record(**record_in.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.put("/{record_id}", response_model=RecordOut)
def update_record(record_id: int, record_in: RecordUpdate, db: Session = Depends(get_db)):
    record = db.get(Record, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    data = record_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record

@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.get(Record, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    db.delete(record)
    db.commit()
