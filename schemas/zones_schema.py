from pydantic import BaseModel, Field
from typing import Optional

# Esquema base con atributos compartidos por todas las zonas
class ZoneBase(BaseModel):
    municipio: str
    cod_ine: str = Field(..., min_length=5, max_length=5) #El código INE debe ser exactamente de 5 carácteres
    id_estacion: str
    estacion_referencia: str

#Esquema para la creación de nuevas zonas (POST)
class ZoneCreate(ZoneBase):
    pass

#Esquema para actualizaciones parciales (PUT) haciendo todos los campos opcionales
class ZoneUpdate(BaseModel):
    municipio: Optional[str] = None
    cod_ine: Optional[str] = None
    id_estacion: Optional[str] = None
    estacion_referencia: Optional[str] = None

#Esquema para la respuesta de la API hacia el usuario
class ZoneOut(ZoneBase):
    id: int #Incluye el ID generado por la base de datos

    class Config:
        from_attributes = True #Permite a Pydantic leer los datos del modelo de 'Zona' de SQLAlchemy