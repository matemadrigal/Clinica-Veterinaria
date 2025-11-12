"""
Módulo del dominio: Mascota
Representa una mascota asociada a un cliente
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from enum import Enum


class Especie(Enum):
    """Enumeración de especies soportadas"""
    PERRO = "Perro"
    GATO = "Gato"
    CONEJO = "Conejo"
    AVE = "Ave"
    ROEDOR = "Roedor"
    REPTIL = "Reptil"
    OTRO = "Otro"


@dataclass
class Mascota:
    """
    Entidad Mascota - representa una mascota de un cliente.
    Cumple con SRP: responsable únicamente de la lógica de la mascota.
    """
    nombre: str
    especie: Especie
    raza: str
    fecha_nacimiento: date
    cliente_id: int
    id: Optional[int] = None
    activo: bool = True
    sexo: Optional[str] = None  # 'M' o 'F'
    color: Optional[str] = None
    peso: Optional[float] = None  # en kg
    microchip: Optional[str] = None
    observaciones: Optional[str] = None
    fecha_registro: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validaciones en la creación de la mascota"""
        self.validar()

    def validar(self) -> None:
        """
        Valida los datos de la mascota según las reglas de negocio.
        Lanza ValueError si algún campo no es válido.
        """
        if not self.nombre or len(self.nombre.strip()) < 1:
            raise ValueError("El nombre es obligatorio")

        if not isinstance(self.especie, Especie):
            raise ValueError("Especie inválida")

        if not self.raza or len(self.raza.strip()) < 1:
            raise ValueError("La raza es obligatoria")

        if not self.fecha_nacimiento:
            raise ValueError("La fecha de nacimiento es obligatoria")

        if self.fecha_nacimiento > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura")

        if self.cliente_id is None or self.cliente_id <= 0:
            raise ValueError("Debe asociarse a un cliente válido")

        if self.sexo and self.sexo not in ['M', 'F']:
            raise ValueError("El sexo debe ser 'M' o 'F'")

        if self.peso is not None and self.peso <= 0:
            raise ValueError("El peso debe ser positivo")

    def calcular_edad(self) -> dict:
        """
        Calcula la edad de la mascota.
        Retorna un diccionario con años y meses.
        """
        hoy = date.today()
        años = hoy.year - self.fecha_nacimiento.year
        meses = hoy.month - self.fecha_nacimiento.month

        if meses < 0:
            años -= 1
            meses += 12

        # Ajuste por días
        if hoy.day < self.fecha_nacimiento.day:
            meses -= 1
            if meses < 0:
                años -= 1
                meses += 12

        return {"años": años, "meses": meses}

    def edad_en_texto(self) -> str:
        """Retorna la edad en formato legible"""
        edad = self.calcular_edad()
        if edad["años"] == 0:
            return f"{edad['meses']} meses"
        elif edad["meses"] == 0:
            return f"{edad['años']} años"
        else:
            return f"{edad['años']} años y {edad['meses']} meses"

    def desactivar(self) -> None:
        """Realiza baja lógica de la mascota"""
        self.activo = False

    def activar(self) -> None:
        """Reactiva una mascota desactivada"""
        self.activo = True

    def actualizar_datos(self, **kwargs) -> None:
        """
        Actualiza los datos de la mascota.
        Solo permite actualizar campos específicos.
        """
        campos_permitidos = {'nombre', 'raza', 'peso', 'color', 'observaciones', 'microchip'}
        for campo, valor in kwargs.items():
            if campo in campos_permitidos:
                setattr(self, campo, valor)
        # Re-validar después de actualizar
        self.validar()

    def __str__(self) -> str:
        return f"Mascota({self.nombre} - {self.especie.value})"

    def __repr__(self) -> str:
        return (f"Mascota(id={self.id}, nombre='{self.nombre}', "
                f"especie={self.especie.value}, cliente_id={self.cliente_id})")
