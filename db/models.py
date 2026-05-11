from datetime import datetime
from sqlalchemy import (Column, Integer, String, Float, DateTime, UniqueConstraint, ForeignKey)
from sqlalchemy.orm import relationship
from .database import Base

class Zona(Base):
    __tablename__ = "zonas"

    id = Column(Integer, primary_key=True, index=True)
    municipio = Column(String, unique=True, index=True)
    cod_ine = Column(String, unique=True, nullable=False, index=True)
    id_estacion = Column(String, nullable=False, index=True)
    estacion_referencia = Column(String, nullable=False)

    mediciones = relationship("Medicion", back_populates="zona")

class Medicion(Base):
    __tablename__= "mediciones"

    id = Column(Integer, primary_key=True, index=True)
    id_zona = Column(Integer, ForeignKey("zonas.id"), nullable=False, index=True)
    fecha = Column(DateTime, nullable=False, index=True)
    temperatura = Column(Float, nullable=False)
    humedad = Column(Float, nullable=False)
    viento = Column(Float, nullable=False)
    lluvia = Column(Float, nullable=False)

    alerta_calor = Column(String, nullable=True)
    alerta_helada = Column(String, nullable=True)
    alerta_viento = Column(String, nullable=True)
    alerta_lluvia = Column(String, nullable=True)

    zona = relationship("Zona", back_populates="mediciones")
    
    #Restricción de unicidad para evitar duplicados, asegurando que no haya dos mediciones para la misma zona y fecha   
    __table_args__ = (UniqueConstraint('id_zona', 'fecha', name='uq_zona_fecha'),)

##Creamos una tabla para guardar los logs del ETL, lo que nos da trazabilidad sobre la ingesta de datos
class ETLLog(Base):
    __tablename__ = "ETL_logs"

    id = Column(Integer, primary_key=True, index=True)
    fecha_ejecucion = Column(DateTime, default=datetime.utcnow)
    origen = Column(String, nullable=False)
    filas_leidas = Column(Integer, default=0)
    filas_insertadas = Column(Integer, default=0)
    filas_modificadas = Column(Integer, default=0)
    filas_descartadas = Column(Integer, default=0)
    duplicados_eliminados = Column(Integer, default=0)

    estado = Column(String, default="OK")
    mensaje = Column(String, nullable=True)