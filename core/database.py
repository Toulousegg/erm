from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import DATABASE_URL, SECRET_KEY, ALGORITHM
from sqlalchemy.orm import declarative_base

base = declarative_base()

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True) #pool_pre_ping=True es para evitar errores de conexión inactiva, verifica la conexión antes de usarla y la reestablece si es necesario.
                                                                      #future=True es para habilitar características futuras de SQLAlchemy y asegurar compatibilidad con versiones futuras.

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)