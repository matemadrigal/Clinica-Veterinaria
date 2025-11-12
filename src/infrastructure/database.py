"""
Configuración de la base de datos SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

# Base para los modelos ORM
Base = declarative_base()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clinica_veterinaria.db")

# Crear engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Cambiar a True para ver queries SQL
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Generador de sesiones de base de datos.
    Uso con context manager para asegurar cierre correcto.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.
    Debe llamarse al inicio de la aplicación.
    """
    from src.infrastructure.models import (
        ClienteModel, MascotaModel, CitaModel,
        FacturaModel, LineaFacturaModel
    )
    Base.metadata.create_all(bind=engine)


def drop_all_tables() -> None:
    """
    Elimina todas las tablas de la base de datos.
    USAR CON PRECAUCIÓN - solo para desarrollo/testing.
    """
    Base.metadata.drop_all(bind=engine)
