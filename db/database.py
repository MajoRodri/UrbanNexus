from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#Usaremos una base de datos SQLite para guardar los datos, 
DATABASE_URL = "sqlite:///./clima.db"

#motor de base de datos de sqlalchemy
#Estamos diciendo que la base de datos se llama clima.db y que se encuentra en el mismo directorio que el archivo 
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

#Session Local nos ayuda a crear conexiones a la base de datos, 
#Cada vez que necesitemos guardar o consultar algo, crearemos una SessionLocal y la cerraremos al terminar
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#Base es el declarativo base de SQLAlchemy.
#Es la plantilla sobre la que construiremos todos nuestros modelos de base de datos.
Base = declarative_base()

#Función que crea todas las tablas en la base de datos
def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()