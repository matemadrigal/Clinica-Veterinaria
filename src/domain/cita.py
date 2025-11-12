"""
Módulo del dominio: Cita
Representa una cita veterinaria
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class EstadoCita(Enum):
    """Enumeración de estados posibles de una cita"""
    PROGRAMADA = "Programada"
    COMPLETADA = "Completada"
    CANCELADA = "Cancelada"
    EN_CURSO = "En curso"


@dataclass
class Cita:
    """
    Entidad Cita - representa una cita veterinaria.
    Cumple con SRP: responsable únicamente de la lógica de citas.
    """
    cliente_id: int
    mascota_id: int
    veterinario_nombre: str
    fecha_hora: datetime
    motivo: str
    id: Optional[int] = None
    estado: EstadoCita = EstadoCita.PROGRAMADA
    duracion_minutos: int = 30
    observaciones: Optional[str] = None
    diagnostico: Optional[str] = None
    tratamiento: Optional[str] = None
    motivo_cancelacion: Optional[str] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_modificacion: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones en la creación de la cita"""
        self.validar()

    def validar(self) -> None:
        """
        Valida los datos de la cita según las reglas de negocio.
        Lanza ValueError si algún campo no es válido.
        """
        if self.cliente_id is None or self.cliente_id <= 0:
            raise ValueError("Debe asociarse a un cliente válido")

        if self.mascota_id is None or self.mascota_id <= 0:
            raise ValueError("Debe asociarse a una mascota válida")

        if not self.veterinario_nombre or len(self.veterinario_nombre.strip()) < 2:
            raise ValueError("El nombre del veterinario es obligatorio")

        if not self.fecha_hora:
            raise ValueError("La fecha y hora son obligatorias")

        # Solo validar fecha futura para citas nuevas (sin ID)
        if self.id is None and self.fecha_hora < datetime.now():
            raise ValueError("La fecha y hora deben ser futuras")

        if not self.motivo or len(self.motivo.strip()) < 3:
            raise ValueError("El motivo debe tener al menos 3 caracteres")

        if not isinstance(self.estado, EstadoCita):
            raise ValueError("Estado de cita inválido")

        if self.duracion_minutos <= 0 or self.duracion_minutos > 480:
            raise ValueError("La duración debe estar entre 1 y 480 minutos")

        # Validar motivo de cancelación si está cancelada
        if self.estado == EstadoCita.CANCELADA and not self.motivo_cancelacion:
            raise ValueError("Debe especificar el motivo de cancelación")

    def completar(self, diagnostico: str, tratamiento: Optional[str] = None) -> None:
        """
        Marca la cita como completada.
        Registra diagnóstico y tratamiento.
        """
        if self.estado == EstadoCita.CANCELADA:
            raise ValueError("No se puede completar una cita cancelada")

        if not diagnostico or len(diagnostico.strip()) < 3:
            raise ValueError("El diagnóstico es obligatorio y debe tener al menos 3 caracteres")

        self.estado = EstadoCita.COMPLETADA
        self.diagnostico = diagnostico
        self.tratamiento = tratamiento
        self.fecha_modificacion = datetime.now()

    def cancelar(self, motivo: str) -> None:
        """
        Cancela la cita.
        Requiere especificar el motivo de cancelación.
        """
        if self.estado == EstadoCita.COMPLETADA:
            raise ValueError("No se puede cancelar una cita completada")

        if not motivo or len(motivo.strip()) < 3:
            raise ValueError("Debe especificar el motivo de cancelación")

        self.estado = EstadoCita.CANCELADA
        self.motivo_cancelacion = motivo
        self.fecha_modificacion = datetime.now()

    def reprogramar(self, nueva_fecha_hora: datetime) -> None:
        """
        Reprograma la cita para una nueva fecha.
        Solo permite reprogramar citas programadas.
        """
        if self.estado not in [EstadoCita.PROGRAMADA, EstadoCita.EN_CURSO]:
            raise ValueError("Solo se pueden reprogramar citas programadas o en curso")

        if nueva_fecha_hora < datetime.now():
            raise ValueError("La nueva fecha debe ser futura")

        self.fecha_hora = nueva_fecha_hora
        self.estado = EstadoCita.PROGRAMADA
        self.fecha_modificacion = datetime.now()

    def iniciar(self) -> None:
        """Marca la cita como en curso"""
        if self.estado != EstadoCita.PROGRAMADA:
            raise ValueError("Solo se pueden iniciar citas programadas")

        self.estado = EstadoCita.EN_CURSO
        self.fecha_modificacion = datetime.now()

    def obtener_hora_fin(self) -> datetime:
        """Calcula y retorna la hora de finalización de la cita"""
        from datetime import timedelta
        return self.fecha_hora + timedelta(minutes=self.duracion_minutos)

    def solapa_con(self, otra_cita: 'Cita') -> bool:
        """
        Verifica si esta cita se solapa con otra.
        Retorna True si hay solapamiento.
        """
        if self.veterinario_nombre != otra_cita.veterinario_nombre:
            return False

        inicio1 = self.fecha_hora
        fin1 = self.obtener_hora_fin()
        inicio2 = otra_cita.fecha_hora
        fin2 = otra_cita.obtener_hora_fin()

        # Hay solapamiento si el inicio de una está entre el inicio y fin de la otra
        return (inicio1 < fin2 and inicio2 < fin1)

    def __str__(self) -> str:
        return f"Cita({self.fecha_hora.strftime('%Y-%m-%d %H:%M')} - {self.veterinario_nombre})"

    def __repr__(self) -> str:
        return (f"Cita(id={self.id}, fecha_hora={self.fecha_hora}, "
                f"veterinario='{self.veterinario_nombre}', estado={self.estado.value})")
