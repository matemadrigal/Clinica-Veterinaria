"""
Servicio de dominio para Mascota.
Contiene la lógica de negocio relacionada con mascotas.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from src.domain.mascota import Mascota, Especie
from src.infrastructure.repositories import MascotaRepository, ClienteRepository


class MascotaService:
    """
    Servicio de dominio para gestión de mascotas.
    Encapsula las reglas de negocio relacionadas con mascotas.
    """

    def __init__(self, db: Session):
        self.repository = MascotaRepository(db)
        self.cliente_repository = ClienteRepository(db)

    def registrar_mascota(self, nombre: str, especie: Especie, raza: str,
                         fecha_nacimiento: date, cliente_id: int,
                         sexo: Optional[str] = None, color: Optional[str] = None,
                         peso: Optional[float] = None, microchip: Optional[str] = None,
                         observaciones: Optional[str] = None) -> Mascota:
        """
        Registra una nueva mascota.
        Valida que el cliente exista y esté activo.
        """
        # Verificar que el cliente existe y está activo
        cliente = self.cliente_repository.obtener_por_id(cliente_id)
        if not cliente:
            raise ValueError(f"El cliente con ID {cliente_id} no existe")
        if not cliente.activo:
            raise ValueError(f"El cliente {cliente.nombre} está inactivo")

        # Verificar duplicados por (cliente, nombre, fecha_nacimiento)
        mascotas_cliente = self.repository.listar_por_cliente(cliente_id)
        for mascota in mascotas_cliente:
            if (mascota.nombre.lower() == nombre.lower() and
                mascota.fecha_nacimiento == fecha_nacimiento):
                raise ValueError(
                    f"Ya existe una mascota llamada '{nombre}' con la misma fecha de nacimiento "
                    f"para este cliente. Si es correcto, modifique ligeramente el nombre."
                )

        # Crear mascota
        mascota = Mascota(
            nombre=nombre,
            especie=especie,
            raza=raza,
            fecha_nacimiento=fecha_nacimiento,
            cliente_id=cliente_id,
            sexo=sexo,
            color=color,
            peso=peso,
            microchip=microchip,
            observaciones=observaciones
        )

        return self.repository.crear(mascota)

    def obtener_mascota(self, id: int) -> Optional[Mascota]:
        """Obtiene una mascota por su ID"""
        return self.repository.obtener_por_id(id)

    def listar_mascotas_por_cliente(self, cliente_id: int, incluir_inactivos: bool = False) -> List[Mascota]:
        """Lista todas las mascotas de un cliente"""
        return self.repository.listar_por_cliente(cliente_id, incluir_inactivos)

    def listar_todas_mascotas(self, incluir_inactivos: bool = False) -> List[Mascota]:
        """Lista todas las mascotas"""
        return self.repository.listar_todas(incluir_inactivos)

    def buscar_mascotas(self, termino: str) -> List[Mascota]:
        """Busca mascotas por nombre o microchip"""
        if not termino or len(termino.strip()) < 2:
            raise ValueError("El término de búsqueda debe tener al menos 2 caracteres")
        return self.repository.buscar(termino)

    def actualizar_mascota(self, id: int, **kwargs) -> Mascota:
        """Actualiza los datos de una mascota"""
        mascota = self.repository.obtener_por_id(id)
        if not mascota:
            raise ValueError(f"Mascota con ID {id} no encontrada")

        mascota.actualizar_datos(**kwargs)
        return self.repository.actualizar(mascota)

    def dar_de_baja(self, id: int) -> bool:
        """Realiza baja lógica de una mascota"""
        return self.repository.eliminar(id)

    def reactivar_mascota(self, id: int) -> Mascota:
        """Reactiva una mascota dada de baja"""
        mascota = self.repository.obtener_por_id(id)
        if not mascota:
            raise ValueError(f"Mascota con ID {id} no encontrada")

        mascota.activar()
        return self.repository.actualizar(mascota)
