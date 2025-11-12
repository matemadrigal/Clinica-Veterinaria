"""
Repositorios para acceso a datos.
Implementan el patrón Repository y cumplen con Dependency Inversion Principle (DIP).
"""
from typing import List, Optional, Protocol
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.domain.cliente import Cliente
from src.domain.mascota import Mascota, Especie
from src.domain.cita import Cita, EstadoCita
from src.domain.factura import Factura, LineaFactura
from src.infrastructure.models import (
    ClienteModel, MascotaModel, CitaModel,
    FacturaModel, LineaFacturaModel
)
from decimal import Decimal


# Interfaces (Protocols) para seguir DIP
class IClienteRepository(Protocol):
    """Interfaz para el repositorio de clientes"""
    def crear(self, cliente: Cliente) -> Cliente: ...
    def obtener_por_id(self, id: int) -> Optional[Cliente]: ...
    def obtener_por_dni(self, dni: str) -> Optional[Cliente]: ...
    def listar_todos(self, incluir_inactivos: bool = False) -> List[Cliente]: ...
    def actualizar(self, cliente: Cliente) -> Cliente: ...
    def eliminar(self, id: int) -> bool: ...


class ClienteRepository:
    """
    Repositorio para operaciones CRUD de Cliente.
    Cumple con SRP: responsable solo del acceso a datos de clientes.
    """

    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, model: ClienteModel) -> Cliente:
        """Convierte modelo ORM a entidad de dominio"""
        return Cliente(
            id=model.id,
            nombre=model.nombre,
            dni=model.dni,
            telefono=model.telefono,
            email=model.email,
            direccion=model.direccion,
            notas=model.notas,
            activo=model.activo,
            fecha_registro=model.fecha_registro
        )

    def _to_model(self, cliente: Cliente) -> ClienteModel:
        """Convierte entidad de dominio a modelo ORM"""
        return ClienteModel(
            id=cliente.id,
            nombre=cliente.nombre,
            dni=cliente.dni,
            telefono=cliente.telefono,
            email=cliente.email,
            direccion=cliente.direccion,
            notas=cliente.notas,
            activo=cliente.activo,
            fecha_registro=cliente.fecha_registro
        )

    def crear(self, cliente: Cliente) -> Cliente:
        """Crea un nuevo cliente en la base de datos"""
        cliente.validar()
        db_cliente = self._to_model(cliente)
        self.db.add(db_cliente)
        self.db.commit()
        self.db.refresh(db_cliente)
        return self._to_domain(db_cliente)

    def obtener_por_id(self, id: int) -> Optional[Cliente]:
        """Obtiene un cliente por su ID"""
        db_cliente = self.db.query(ClienteModel).filter(ClienteModel.id == id).first()
        return self._to_domain(db_cliente) if db_cliente else None

    def obtener_por_dni(self, dni: str) -> Optional[Cliente]:
        """Obtiene un cliente por su DNI"""
        db_cliente = self.db.query(ClienteModel).filter(ClienteModel.dni == dni).first()
        return self._to_domain(db_cliente) if db_cliente else None

    def listar_todos(self, incluir_inactivos: bool = False) -> List[Cliente]:
        """Lista todos los clientes, opcionalmente incluyendo inactivos"""
        query = self.db.query(ClienteModel)
        if not incluir_inactivos:
            query = query.filter(ClienteModel.activo == True)
        return [self._to_domain(c) for c in query.all()]

    def buscar(self, termino: str) -> List[Cliente]:
        """Busca clientes por nombre, DNI o email"""
        termino_like = f"%{termino}%"
        query = self.db.query(ClienteModel).filter(
            or_(
                ClienteModel.nombre.ilike(termino_like),
                ClienteModel.dni.ilike(termino_like),
                ClienteModel.email.ilike(termino_like)
            )
        )
        return [self._to_domain(c) for c in query.all()]

    def actualizar(self, cliente: Cliente) -> Cliente:
        """Actualiza un cliente existente"""
        cliente.validar()
        db_cliente = self.db.query(ClienteModel).filter(ClienteModel.id == cliente.id).first()
        if not db_cliente:
            raise ValueError(f"Cliente con ID {cliente.id} no encontrado")

        db_cliente.nombre = cliente.nombre
        db_cliente.telefono = cliente.telefono
        db_cliente.email = cliente.email
        db_cliente.direccion = cliente.direccion
        db_cliente.notas = cliente.notas
        db_cliente.activo = cliente.activo

        self.db.commit()
        self.db.refresh(db_cliente)
        return self._to_domain(db_cliente)

    def eliminar(self, id: int) -> bool:
        """Realiza baja lógica de un cliente"""
        db_cliente = self.db.query(ClienteModel).filter(ClienteModel.id == id).first()
        if not db_cliente:
            return False

        db_cliente.activo = False
        self.db.commit()
        return True


class MascotaRepository:
    """
    Repositorio para operaciones CRUD de Mascota.
    Cumple con SRP: responsable solo del acceso a datos de mascotas.
    """

    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, model: MascotaModel) -> Mascota:
        """Convierte modelo ORM a entidad de dominio"""
        return Mascota(
            id=model.id,
            nombre=model.nombre,
            especie=Especie(model.especie),
            raza=model.raza,
            fecha_nacimiento=model.fecha_nacimiento,
            cliente_id=model.cliente_id,
            sexo=model.sexo,
            color=model.color,
            peso=model.peso,
            microchip=model.microchip,
            observaciones=model.observaciones,
            activo=model.activo,
            fecha_registro=model.fecha_registro
        )

    def _to_model(self, mascota: Mascota) -> MascotaModel:
        """Convierte entidad de dominio a modelo ORM"""
        return MascotaModel(
            id=mascota.id,
            nombre=mascota.nombre,
            especie=mascota.especie.value,
            raza=mascota.raza,
            fecha_nacimiento=mascota.fecha_nacimiento,
            cliente_id=mascota.cliente_id,
            sexo=mascota.sexo,
            color=mascota.color,
            peso=mascota.peso,
            microchip=mascota.microchip,
            observaciones=mascota.observaciones,
            activo=mascota.activo,
            fecha_registro=mascota.fecha_registro
        )

    def crear(self, mascota: Mascota) -> Mascota:
        """Crea una nueva mascota en la base de datos"""
        mascota.validar()
        db_mascota = self._to_model(mascota)
        self.db.add(db_mascota)
        self.db.commit()
        self.db.refresh(db_mascota)
        return self._to_domain(db_mascota)

    def obtener_por_id(self, id: int) -> Optional[Mascota]:
        """Obtiene una mascota por su ID"""
        db_mascota = self.db.query(MascotaModel).filter(MascotaModel.id == id).first()
        return self._to_domain(db_mascota) if db_mascota else None

    def listar_por_cliente(self, cliente_id: int, incluir_inactivos: bool = False) -> List[Mascota]:
        """Lista todas las mascotas de un cliente"""
        query = self.db.query(MascotaModel).filter(MascotaModel.cliente_id == cliente_id)
        if not incluir_inactivos:
            query = query.filter(MascotaModel.activo == True)
        return [self._to_domain(m) for m in query.all()]

    def listar_todas(self, incluir_inactivos: bool = False) -> List[Mascota]:
        """Lista todas las mascotas"""
        query = self.db.query(MascotaModel)
        if not incluir_inactivos:
            query = query.filter(MascotaModel.activo == True)
        return [self._to_domain(m) for m in query.all()]

    def buscar(self, termino: str) -> List[Mascota]:
        """Busca mascotas por nombre o microchip"""
        termino_like = f"%{termino}%"
        query = self.db.query(MascotaModel).filter(
            or_(
                MascotaModel.nombre.ilike(termino_like),
                MascotaModel.microchip.ilike(termino_like)
            )
        )
        return [self._to_domain(m) for m in query.all()]

    def actualizar(self, mascota: Mascota) -> Mascota:
        """Actualiza una mascota existente"""
        mascota.validar()
        db_mascota = self.db.query(MascotaModel).filter(MascotaModel.id == mascota.id).first()
        if not db_mascota:
            raise ValueError(f"Mascota con ID {mascota.id} no encontrada")

        db_mascota.nombre = mascota.nombre
        db_mascota.raza = mascota.raza
        db_mascota.peso = mascota.peso
        db_mascota.color = mascota.color
        db_mascota.observaciones = mascota.observaciones
        db_mascota.microchip = mascota.microchip
        db_mascota.activo = mascota.activo

        self.db.commit()
        self.db.refresh(db_mascota)
        return self._to_domain(db_mascota)

    def eliminar(self, id: int) -> bool:
        """Realiza baja lógica de una mascota"""
        db_mascota = self.db.query(MascotaModel).filter(MascotaModel.id == id).first()
        if not db_mascota:
            return False

        db_mascota.activo = False
        self.db.commit()
        return True


class CitaRepository:
    """
    Repositorio para operaciones CRUD de Cita.
    Cumple con SRP: responsable solo del acceso a datos de citas.
    """

    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, model: CitaModel) -> Cita:
        """Convierte modelo ORM a entidad de dominio"""
        return Cita(
            id=model.id,
            cliente_id=model.cliente_id,
            mascota_id=model.mascota_id,
            veterinario_nombre=model.veterinario_nombre,
            fecha_hora=model.fecha_hora,
            duracion_minutos=model.duracion_minutos,
            motivo=model.motivo,
            estado=EstadoCita(model.estado),
            observaciones=model.observaciones,
            diagnostico=model.diagnostico,
            tratamiento=model.tratamiento,
            motivo_cancelacion=model.motivo_cancelacion,
            fecha_creacion=model.fecha_creacion,
            fecha_modificacion=model.fecha_modificacion
        )

    def _to_model(self, cita: Cita) -> CitaModel:
        """Convierte entidad de dominio a modelo ORM"""
        return CitaModel(
            id=cita.id,
            cliente_id=cita.cliente_id,
            mascota_id=cita.mascota_id,
            veterinario_nombre=cita.veterinario_nombre,
            fecha_hora=cita.fecha_hora,
            duracion_minutos=cita.duracion_minutos,
            motivo=cita.motivo,
            estado=cita.estado.value,
            observaciones=cita.observaciones,
            diagnostico=cita.diagnostico,
            tratamiento=cita.tratamiento,
            motivo_cancelacion=cita.motivo_cancelacion,
            fecha_creacion=cita.fecha_creacion,
            fecha_modificacion=cita.fecha_modificacion
        )

    def crear(self, cita: Cita) -> Cita:
        """Crea una nueva cita en la base de datos"""
        cita.validar()
        db_cita = self._to_model(cita)
        self.db.add(db_cita)
        self.db.commit()
        self.db.refresh(db_cita)
        return self._to_domain(db_cita)

    def obtener_por_id(self, id: int) -> Optional[Cita]:
        """Obtiene una cita por su ID"""
        db_cita = self.db.query(CitaModel).filter(CitaModel.id == id).first()
        return self._to_domain(db_cita) if db_cita else None

    def listar_todas(self) -> List[Cita]:
        """Lista todas las citas"""
        return [self._to_domain(c) for c in self.db.query(CitaModel).all()]

    def listar_por_fecha(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Cita]:
        """Lista citas en un rango de fechas"""
        query = self.db.query(CitaModel).filter(
            and_(
                CitaModel.fecha_hora >= fecha_inicio,
                CitaModel.fecha_hora <= fecha_fin
            )
        )
        return [self._to_domain(c) for c in query.all()]

    def listar_por_veterinario(self, veterinario_nombre: str, fecha: date) -> List[Cita]:
        """Lista citas de un veterinario en una fecha específica"""
        fecha_inicio = datetime.combine(fecha, datetime.min.time())
        fecha_fin = datetime.combine(fecha, datetime.max.time())

        query = self.db.query(CitaModel).filter(
            and_(
                CitaModel.veterinario_nombre == veterinario_nombre,
                CitaModel.fecha_hora >= fecha_inicio,
                CitaModel.fecha_hora <= fecha_fin
            )
        )
        return [self._to_domain(c) for c in query.all()]

    def listar_por_estado(self, estado: EstadoCita) -> List[Cita]:
        """Lista citas por estado"""
        query = self.db.query(CitaModel).filter(CitaModel.estado == estado.value)
        return [self._to_domain(c) for c in query.all()]

    def actualizar(self, cita: Cita) -> Cita:
        """Actualiza una cita existente"""
        cita.validar()
        db_cita = self.db.query(CitaModel).filter(CitaModel.id == cita.id).first()
        if not db_cita:
            raise ValueError(f"Cita con ID {cita.id} no encontrada")

        db_cita.fecha_hora = cita.fecha_hora
        db_cita.duracion_minutos = cita.duracion_minutos
        db_cita.motivo = cita.motivo
        db_cita.estado = cita.estado.value
        db_cita.observaciones = cita.observaciones
        db_cita.diagnostico = cita.diagnostico
        db_cita.tratamiento = cita.tratamiento
        db_cita.motivo_cancelacion = cita.motivo_cancelacion
        db_cita.fecha_modificacion = cita.fecha_modificacion

        self.db.commit()
        self.db.refresh(db_cita)
        return self._to_domain(db_cita)

    def eliminar(self, id: int) -> bool:
        """Elimina una cita"""
        db_cita = self.db.query(CitaModel).filter(CitaModel.id == id).first()
        if not db_cita:
            return False

        self.db.delete(db_cita)
        self.db.commit()
        return True


class FacturaRepository:
    """
    Repositorio para operaciones CRUD de Factura.
    Cumple con SRP: responsable solo del acceso a datos de facturas.
    """

    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, model: FacturaModel) -> Factura:
        """Convierte modelo ORM a entidad de dominio"""
        lineas = [
            LineaFactura(
                id=linea.id,
                factura_id=linea.factura_id,
                concepto=linea.concepto,
                cantidad=linea.cantidad,
                precio_unitario=Decimal(str(linea.precio_unitario)),
                iva_porcentaje=Decimal(str(linea.iva_porcentaje))
            )
            for linea in model.lineas
        ]

        return Factura(
            id=model.id,
            numero_factura=model.numero_factura,
            cita_id=model.cita_id,
            cliente_id=model.cliente_id,
            fecha_emision=model.fecha_emision,
            lineas=lineas,
            pagada=model.pagada,
            fecha_pago=model.fecha_pago,
            metodo_pago=model.metodo_pago,
            observaciones=model.observaciones
        )

    def crear(self, factura: Factura) -> Factura:
        """Crea una nueva factura con sus líneas"""
        factura.validar()

        db_factura = FacturaModel(
            numero_factura=factura.numero_factura,
            cita_id=factura.cita_id,
            cliente_id=factura.cliente_id,
            fecha_emision=factura.fecha_emision,
            pagada=factura.pagada,
            fecha_pago=factura.fecha_pago,
            metodo_pago=factura.metodo_pago,
            observaciones=factura.observaciones
        )

        self.db.add(db_factura)
        self.db.flush()  # Para obtener el ID de la factura

        # Agregar líneas
        for linea in factura.lineas:
            db_linea = LineaFacturaModel(
                factura_id=db_factura.id,
                concepto=linea.concepto,
                cantidad=linea.cantidad,
                precio_unitario=float(linea.precio_unitario),
                iva_porcentaje=float(linea.iva_porcentaje)
            )
            self.db.add(db_linea)

        self.db.commit()
        self.db.refresh(db_factura)
        return self._to_domain(db_factura)

    def obtener_por_id(self, id: int) -> Optional[Factura]:
        """Obtiene una factura por su ID"""
        db_factura = self.db.query(FacturaModel).filter(FacturaModel.id == id).first()
        return self._to_domain(db_factura) if db_factura else None

    def obtener_por_numero(self, numero_factura: str) -> Optional[Factura]:
        """Obtiene una factura por su número"""
        db_factura = self.db.query(FacturaModel).filter(
            FacturaModel.numero_factura == numero_factura
        ).first()
        return self._to_domain(db_factura) if db_factura else None

    def listar_todas(self) -> List[Factura]:
        """Lista todas las facturas"""
        return [self._to_domain(f) for f in self.db.query(FacturaModel).all()]

    def listar_por_cliente(self, cliente_id: int) -> List[Factura]:
        """Lista facturas de un cliente"""
        query = self.db.query(FacturaModel).filter(FacturaModel.cliente_id == cliente_id)
        return [self._to_domain(f) for f in query.all()]

    def actualizar(self, factura: Factura) -> Factura:
        """Actualiza una factura existente"""
        factura.validar()
        db_factura = self.db.query(FacturaModel).filter(FacturaModel.id == factura.id).first()
        if not db_factura:
            raise ValueError(f"Factura con ID {factura.id} no encontrada")

        db_factura.pagada = factura.pagada
        db_factura.fecha_pago = factura.fecha_pago
        db_factura.metodo_pago = factura.metodo_pago
        db_factura.observaciones = factura.observaciones

        self.db.commit()
        self.db.refresh(db_factura)
        return self._to_domain(db_factura)

    def generar_numero_factura(self) -> str:
        """Genera un número de factura único e incremental"""
        ultimo = self.db.query(FacturaModel).order_by(FacturaModel.id.desc()).first()
        if not ultimo:
            return "F-2025-00001"

        # Extraer número del último
        try:
            partes = ultimo.numero_factura.split('-')
            numero = int(partes[-1])
            return f"F-2025-{str(numero + 1).zfill(5)}"
        except:
            return f"F-2025-{str(ultimo.id + 1).zfill(5)}"
