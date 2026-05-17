from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Atributos base para las mediciones climáticas
class RecordBase(BaseModel):
    fecha: datetime

    # Validaciones técnicas para asegurar la integridad de los datos climáticos
    temperatura: float = Field(..., ge=-50, le=60)       #Rango de temperatura razonable
    humedad: float = Field(..., ge=0, le=100)            #Rango de humedad (0 - 100)
    viento: float = Field(..., ge=0)                     #Velocidad del viento (No negativa)
    lluvia: float = Field(..., ge=0)                     #Precipitación (No negativo)

# Esquema para la ingesta de datos (POST)
class RecordCreate(RecordBase):
    id_zona: int  #Relación con la tabla de zonas

# Esquema para modificar registros existentes (PUT)
class RecordUpdate(BaseModel):
    fecha: Optional[datetime] = None
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    viento: Optional[float] = None
    lluvia: Optional[float] = None

# Esquema de salida que expone las alertas calculadas por el sistema
class RecordOut(RecordBase):
    id: int
    id_zona: int

    # Campos opcionales para mostrar alertas adecuadas (Calor, Humedad, etc)
    alerta_calor: Optional[str] = None
    alerta_helada: Optional[str] = None
    alerta_viento: Optional[str] = None
    alerta_lluvia: Optional[str] = None

    class Config:
        from_attributes = True  #Mapea datos directamente desde el modelo 'Medicion' (alias Record)
