"""
Utilidades de validación reutilizables.
"""
import re
from datetime import datetime, date
from typing import Optional


def validar_email(email: str) -> bool:
    """Valida formato de email"""
    if not email:
        return False
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email.strip()))


def validar_telefono_espanol(telefono: str) -> bool:
    """Valida formato de teléfono español"""
    if not telefono:
        return False
    telefono_limpio = re.sub(r'[\s\-]', '', telefono)
    patron = r'^(\+34)?[6-9]\d{8}$'
    return bool(re.match(patron, telefono_limpio))


def validar_dni_espanol(dni: str) -> bool:
    """Valida DNI español (8 dígitos + letra)"""
    if not dni:
        return False
    dni = dni.upper().strip()
    patron = r'^\d{8}[A-Z]$'
    if not re.match(patron, dni):
        return False

    letras = 'TRWAGMYFPDXBNJZSQVHLCKE'
    numeros = int(dni[:-1])
    letra = dni[-1]
    return letras[numeros % 23] == letra


def limpiar_telefono(telefono: str) -> str:
    """Limpia y normaliza un número de teléfono"""
    return re.sub(r'[\s\-]', '', telefono)


def validar_fecha_futura(fecha: datetime) -> bool:
    """Verifica si una fecha es futura"""
    return fecha > datetime.now()


def validar_fecha_no_futura(fecha: datetime) -> bool:
    """Verifica si una fecha no es futura"""
    return fecha <= datetime.now()


def calcular_edad(fecha_nacimiento: date) -> dict:
    """
    Calcula la edad en años y meses desde una fecha de nacimiento.
    """
    hoy = date.today()
    años = hoy.year - fecha_nacimiento.year
    meses = hoy.month - fecha_nacimiento.month

    if meses < 0:
        años -= 1
        meses += 12

    if hoy.day < fecha_nacimiento.day:
        meses -= 1
        if meses < 0:
            años -= 1
            meses += 12

    return {"años": años, "meses": meses}


def formatear_moneda(cantidad: float) -> str:
    """Formatea un número como moneda en euros"""
    return f"{cantidad:,.2f}€".replace(",", "X").replace(".", ",").replace("X", ".")


def sanitizar_texto(texto: Optional[str]) -> Optional[str]:
    """Sanitiza texto eliminando caracteres potencialmente peligrosos"""
    if not texto:
        return texto
    # Eliminar caracteres de control y normalizar espacios
    texto = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', texto)
    texto = ' '.join(texto.split())
    return texto.strip()
