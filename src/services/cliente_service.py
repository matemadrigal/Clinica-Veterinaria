"""
Servicio de dominio para Cliente.
Contiene la lógica de negocio relacionada con clientes.
Cumple con SRP: responsable únicamente de las operaciones de negocio de clientes.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.cliente import Cliente
from src.infrastructure.repositories import ClienteRepository


class ClienteService:
    """
    Servicio de dominio para gestión de clientes.
    Encapsula las reglas de negocio relacionadas con clientes.
    """

    def __init__(self, db: Session):
        self.repository = ClienteRepository(db)

    def registrar_cliente(self, nombre: str, dni: str, telefono: str, email: str,
                         direccion: Optional[str] = None, notas: Optional[str] = None) -> Cliente:
        """
        Registra un nuevo cliente.
        Valida que no exista un cliente con el mismo DNI.
        """
        # Verificar que no exista cliente con ese DNI
        cliente_existente = self.repository.obtener_por_dni(dni)
        if cliente_existente:
            raise ValueError(f"Ya existe un cliente registrado con el DNI {dni}")

        # Crear cliente
        cliente = Cliente(
            nombre=nombre,
            dni=dni,
            telefono=telefono,
            email=email,
            direccion=direccion,
            notas=notas
        )

        return self.repository.crear(cliente)

    def obtener_cliente(self, id: int) -> Optional[Cliente]:
        """Obtiene un cliente por su ID"""
        return self.repository.obtener_por_id(id)

    def obtener_cliente_por_dni(self, dni: str) -> Optional[Cliente]:
        """Obtiene un cliente por su DNI"""
        return self.repository.obtener_por_dni(dni)

    def listar_clientes(self, incluir_inactivos: bool = False) -> List[Cliente]:
        """Lista todos los clientes"""
        return self.repository.listar_todos(incluir_inactivos)

    def buscar_clientes(self, termino: str) -> List[Cliente]:
        """Busca clientes por nombre, DNI o email"""
        if not termino or len(termino.strip()) < 2:
            raise ValueError("El término de búsqueda debe tener al menos 2 caracteres")
        return self.repository.buscar(termino)

    def actualizar_cliente(self, id: int, **kwargs) -> Cliente:
        """
        Actualiza los datos de un cliente.
        Solo permite actualizar campos específicos.
        """
        cliente = self.repository.obtener_por_id(id)
        if not cliente:
            raise ValueError(f"Cliente con ID {id} no encontrado")

        # Si se está cambiando el DNI, verificar que no exista otro con ese DNI
        if 'dni' in kwargs and kwargs['dni'] != cliente.dni:
            otro_cliente = self.repository.obtener_por_dni(kwargs['dni'])
            if otro_cliente:
                raise ValueError(f"Ya existe otro cliente con el DNI {kwargs['dni']}")

        cliente.actualizar_datos(**kwargs)
        return self.repository.actualizar(cliente)

    def dar_de_baja(self, id: int) -> bool:
        """Realiza baja lógica de un cliente"""
        return self.repository.eliminar(id)

    def reactivar_cliente(self, id: int) -> Cliente:
        """Reactiva un cliente dado de baja"""
        cliente = self.repository.obtener_por_id(id)
        if not cliente:
            raise ValueError(f"Cliente con ID {id} no encontrado")

        cliente.activar()
        return self.repository.actualizar(cliente)
