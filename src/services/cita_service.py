"""
Servicio de dominio para Cita.
Contiene la lógica de negocio relacionada con citas, incluyendo validación de solapes.
"""
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

from src.domain.cita import Cita, EstadoCita
from src.infrastructure.repositories import CitaRepository, ClienteRepository, MascotaRepository


class CitaService:
    """
    Servicio de dominio para gestión de citas.
    Implementa reglas de negocio como la prevención de solapes.
    """

    def __init__(self, db: Session):
        self.repository = CitaRepository(db)
        self.cliente_repository = ClienteRepository(db)
        self.mascota_repository = MascotaRepository(db)

    def agendar_cita(self, cliente_id: int, mascota_id: int, veterinario_nombre: str,
                    fecha_hora: datetime, motivo: str, duracion_minutos: int = 30,
                    observaciones: Optional[str] = None) -> Cita:
        """
        Agenda una nueva cita.
        Valida que cliente y mascota existan, y que no haya solapes de veterinario.
        """
        # Verificar que el cliente existe y está activo
        cliente = self.cliente_repository.obtener_por_id(cliente_id)
        if not cliente:
            raise ValueError(f"El cliente con ID {cliente_id} no existe")
        if not cliente.activo:
            raise ValueError(f"El cliente {cliente.nombre} está inactivo")

        # Verificar que la mascota existe, está activa y pertenece al cliente
        mascota = self.mascota_repository.obtener_por_id(mascota_id)
        if not mascota:
            raise ValueError(f"La mascota con ID {mascota_id} no existe")
        if not mascota.activo:
            raise ValueError(f"La mascota {mascota.nombre} está inactiva")
        if mascota.cliente_id != cliente_id:
            raise ValueError(f"La mascota {mascota.nombre} no pertenece al cliente {cliente.nombre}")

        # Crear cita
        cita = Cita(
            cliente_id=cliente_id,
            mascota_id=mascota_id,
            veterinario_nombre=veterinario_nombre,
            fecha_hora=fecha_hora,
            duracion_minutos=duracion_minutos,
            motivo=motivo,
            observaciones=observaciones
        )

        # Verificar solapes con otras citas del mismo veterinario
        if self._tiene_solape(cita):
            raise ValueError(
                f"El veterinario {veterinario_nombre} ya tiene una cita agendada "
                f"en ese horario. Por favor, elija otro horario."
            )

        return self.repository.crear(cita)

    def _tiene_solape(self, cita: Cita) -> bool:
        """
        Verifica si la cita se solapa con otras citas del mismo veterinario.
        Ignora citas canceladas.
        """
        # Obtener citas del veterinario en la misma fecha
        citas_dia = self.repository.listar_por_veterinario(
            cita.veterinario_nombre,
            cita.fecha_hora.date()
        )

        for cita_existente in citas_dia:
            # Ignorar la misma cita (en caso de actualización) y citas canceladas
            if (cita.id and cita_existente.id == cita.id) or \
               cita_existente.estado == EstadoCita.CANCELADA:
                continue

            if cita.solapa_con(cita_existente):
                return True

        return False

    def obtener_cita(self, id: int) -> Optional[Cita]:
        """Obtiene una cita por su ID"""
        return self.repository.obtener_por_id(id)

    def listar_citas(self) -> List[Cita]:
        """Lista todas las citas"""
        return self.repository.listar_todas()

    def listar_citas_por_fecha(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Cita]:
        """Lista citas en un rango de fechas"""
        return self.repository.listar_por_fecha(fecha_inicio, fecha_fin)

    def listar_citas_del_dia(self, fecha: date, veterinario: Optional[str] = None) -> List[Cita]:
        """Lista citas de un día específico, opcionalmente filtradas por veterinario"""
        fecha_inicio = datetime.combine(fecha, datetime.min.time())
        fecha_fin = datetime.combine(fecha, datetime.max.time())

        if veterinario:
            return self.repository.listar_por_veterinario(veterinario, fecha)
        else:
            return self.repository.listar_por_fecha(fecha_inicio, fecha_fin)

    def listar_citas_por_estado(self, estado: EstadoCita) -> List[Cita]:
        """Lista citas por estado"""
        return self.repository.listar_por_estado(estado)

    def completar_cita(self, id: int, diagnostico: str, tratamiento: Optional[str] = None) -> Cita:
        """
        Completa una cita registrando diagnóstico y tratamiento.
        """
        cita = self.repository.obtener_por_id(id)
        if not cita:
            raise ValueError(f"Cita con ID {id} no encontrada")

        cita.completar(diagnostico, tratamiento)
        return self.repository.actualizar(cita)

    def cancelar_cita(self, id: int, motivo: str) -> Cita:
        """
        Cancela una cita registrando el motivo.
        """
        cita = self.repository.obtener_por_id(id)
        if not cita:
            raise ValueError(f"Cita con ID {id} no encontrada")

        cita.cancelar(motivo)
        return self.repository.actualizar(cita)

    def reprogramar_cita(self, id: int, nueva_fecha_hora: datetime) -> Cita:
        """
        Reprograma una cita para una nueva fecha.
        Valida que no haya solapes en la nueva fecha.
        """
        cita = self.repository.obtener_por_id(id)
        if not cita:
            raise ValueError(f"Cita con ID {id} no encontrada")

        # Guardar fecha original
        fecha_original = cita.fecha_hora

        # Intentar reprogramar
        try:
            cita.reprogramar(nueva_fecha_hora)

            # Verificar solapes en la nueva fecha
            if self._tiene_solape(cita):
                # Restaurar fecha original
                cita.fecha_hora = fecha_original
                raise ValueError(
                    f"El veterinario {cita.veterinario_nombre} ya tiene una cita "
                    f"agendada en ese horario. Por favor, elija otro horario."
                )

            return self.repository.actualizar(cita)
        except ValueError as e:
            # Restaurar fecha original si hay error
            cita.fecha_hora = fecha_original
            raise e

    def iniciar_cita(self, id: int) -> Cita:
        """Marca una cita como en curso"""
        cita = self.repository.obtener_por_id(id)
        if not cita:
            raise ValueError(f"Cita con ID {id} no encontrada")

        cita.iniciar()
        return self.repository.actualizar(cita)
