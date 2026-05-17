import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(_BASE_DIR, 'clima.db')}")

# Motor con timeout de 30 segundos para evitar choques entre FastAPI y Flask
engine = create_engine(
    DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    }
)

# Sesión para SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa
Base = declarative_base()

# Función para crear tablas
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print(">>> [DB] Tablas verificadas/creadas en clima.db")
    except Exception as e:
        print(f">>> [DB] Error al crear tablas: {e}")

# Generador de sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()