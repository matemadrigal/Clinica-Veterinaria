"""
Configuración de logging para la aplicación.
"""
import logging
import sys
from pathlib import Path


def setup_logger(name: str = "clinica_veterinaria", level: int = logging.INFO) -> logging.Logger:
    """
    Configura y retorna un logger para la aplicación.

    Args:
        name: Nombre del logger
        level: Nivel de logging (default: INFO)

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar duplicar handlers
    if logger.handlers:
        return logger

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "clinica_veterinaria") -> logging.Logger:
    """Obtiene un logger existente o crea uno nuevo"""
    return logging.getLogger(name)
