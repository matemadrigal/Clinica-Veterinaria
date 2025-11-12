"""
Módulo del dominio: Cliente
Representa un cliente de la clínica veterinaria
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import re


@dataclass
class Cliente:
    """
    Entidad Cliente - representa un cliente de la clínica veterinaria.
    Cumple con SRP: responsable únicamente de la lógica del cliente.
    """
    nombre: str
    dni: str
    telefono: str
    email: str
    id: Optional[int] = None
    activo: bool = True
    fecha_registro: datetime = field(default_factory=datetime.now)
    direccion: Optional[str] = None
    notas: Optional[str] = None

    def __post_init__(self):
        """Validaciones en la creación del cliente"""
        self.validar()

    def validar(self) -> None:
        """
        Valida los datos del cliente según las reglas de negocio.
        Lanza ValueError si algún campo no es válido.
        """
        if not self.nombre or len(self.nombre.strip()) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")

        if not self.validar_dni(self.dni):
            raise ValueError("DNI/NIF inválido")

        if not self.validar_telefono(self.telefono):
            raise ValueError("Teléfono inválido")

        if not self.validar_email(self.email):
            raise ValueError("Email inválido")

    @staticmethod
    def validar_dni(dni: str) -> bool:
        """Valida formato DNI español (8 dígitos + letra)"""
        if not dni:
            return False
        dni = dni.upper().strip()
        # Formato básico: 8 dígitos + letra
        patron = r'^\d{8}[A-Z]$'
        if not re.match(patron, dni):
            return False

        # Validación letra DNI
        letras = 'TRWAGMYFPDXBNJZSQVHLCKE'
        numeros = int(dni[:-1])
        letra = dni[-1]
        return letras[numeros % 23] == letra

    @staticmethod
    def validar_telefono(telefono: str) -> bool:
        """Valida formato de teléfono español"""
        if not telefono:
            return False
        # Eliminar espacios y guiones
        telefono_limpio = re.sub(r'[\s\-]', '', telefono)
        # 9 dígitos, puede empezar con +34
        patron = r'^(\+34)?[6-9]\d{8}$'
        return bool(re.match(patron, telefono_limpio))

    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return False
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(patron, email.strip()))

    def desactivar(self) -> None:
        """Realiza baja lógica del cliente"""
        self.activo = False

    def activar(self) -> None:
        """Reactiva un cliente desactivado"""
        self.activo = True

    def actualizar_datos(self, **kwargs) -> None:
        """
        Actualiza los datos del cliente.
        Solo permite actualizar campos específicos.
        """
        campos_permitidos = {'nombre', 'telefono', 'email', 'direccion', 'notas'}
        for campo, valor in kwargs.items():
            if campo in campos_permitidos:
                setattr(self, campo, valor)
        # Re-validar después de actualizar
        self.validar()

    def __str__(self) -> str:
        return f"Cliente({self.dni} - {self.nombre})"

    def __repr__(self) -> str:
        return (f"Cliente(id={self.id}, dni='{self.dni}', nombre='{self.nombre}', "
                f"email='{self.email}', activo={self.activo})")
