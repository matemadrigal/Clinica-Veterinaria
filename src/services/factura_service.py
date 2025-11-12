"""
Servicio de dominio para Factura.
Contiene la lógica de negocio relacionada con facturación.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from decimal import Decimal

from src.domain.factura import Factura, LineaFactura
from src.domain.cita import EstadoCita
from src.infrastructure.repositories import FacturaRepository, CitaRepository, ClienteRepository


class FacturaService:
    """
    Servicio de dominio para gestión de facturas.
    Implementa reglas de negocio de facturación.
    """

    def __init__(self, db: Session):
        self.repository = FacturaRepository(db)
        self.cita_repository = CitaRepository(db)
        self.cliente_repository = ClienteRepository(db)

    def crear_factura_desde_cita(self, cita_id: int, lineas_data: List[dict],
                                  observaciones: Optional[str] = None) -> Factura:
        """
        Crea una factura desde una cita completada.
        Valida que la cita esté completada y no tenga factura ya.

        lineas_data debe ser una lista de diccionarios con:
        - concepto: str
        - cantidad: int
        - precio_unitario: float/Decimal
        - iva_porcentaje: float/Decimal
        """
        # Verificar que la cita existe
        cita = self.cita_repository.obtener_por_id(cita_id)
        if not cita:
            raise ValueError(f"La cita con ID {cita_id} no existe")

        # Verificar que la cita está completada
        if cita.estado != EstadoCita.COMPLETADA:
            raise ValueError(
                f"No se puede facturar una cita que no está completada. "
                f"Estado actual: {cita.estado.value}"
            )

        # Verificar que no tenga factura ya
        facturas_existentes = self.repository.listar_todas()
        for factura in facturas_existentes:
            if factura.cita_id == cita_id:
                raise ValueError(
                    f"La cita {cita_id} ya tiene una factura asociada: {factura.numero_factura}"
                )

        # Verificar que el cliente existe
        cliente = self.cliente_repository.obtener_por_id(cita.cliente_id)
        if not cliente:
            raise ValueError(f"El cliente con ID {cita.cliente_id} no existe")

        # Generar número de factura
        numero_factura = self.repository.generar_numero_factura()

        # Crear líneas de factura
        lineas = []
        for linea_data in lineas_data:
            linea = LineaFactura(
                concepto=linea_data['concepto'],
                cantidad=linea_data['cantidad'],
                precio_unitario=Decimal(str(linea_data['precio_unitario'])),
                iva_porcentaje=Decimal(str(linea_data['iva_porcentaje']))
            )
            lineas.append(linea)

        if not lineas:
            raise ValueError("La factura debe tener al menos una línea")

        # Crear factura
        factura = Factura(
            numero_factura=numero_factura,
            cita_id=cita_id,
            cliente_id=cita.cliente_id,
            fecha_emision=datetime.now(),
            lineas=lineas,
            observaciones=observaciones
        )

        return self.repository.crear(factura)

    def obtener_factura(self, id: int) -> Optional[Factura]:
        """Obtiene una factura por su ID"""
        return self.repository.obtener_por_id(id)

    def obtener_factura_por_numero(self, numero_factura: str) -> Optional[Factura]:
        """Obtiene una factura por su número"""
        return self.repository.obtener_por_numero(numero_factura)

    def listar_facturas(self) -> List[Factura]:
        """Lista todas las facturas"""
        return self.repository.listar_todas()

    def listar_facturas_cliente(self, cliente_id: int) -> List[Factura]:
        """Lista las facturas de un cliente"""
        return self.repository.listar_por_cliente(cliente_id)

    def marcar_como_pagada(self, id: int, metodo_pago: str,
                          fecha_pago: Optional[datetime] = None) -> Factura:
        """
        Marca una factura como pagada.
        Registra el método y fecha de pago.
        """
        factura = self.repository.obtener_por_id(id)
        if not factura:
            raise ValueError(f"Factura con ID {id} no encontrada")

        factura.marcar_como_pagada(metodo_pago, fecha_pago)
        return self.repository.actualizar(factura)

    def calcular_ingresos_periodo(self, fecha_inicio: datetime, fecha_fin: datetime) -> dict:
        """
        Calcula los ingresos totales en un período.
        Retorna un diccionario con estadísticas.
        """
        facturas = self.repository.listar_todas()

        facturas_periodo = [
            f for f in facturas
            if fecha_inicio <= f.fecha_emision <= fecha_fin
        ]

        total_facturado = sum(
            float(f.calcular_total()) for f in facturas_periodo
        )

        total_pagado = sum(
            float(f.calcular_total()) for f in facturas_periodo if f.pagada
        )

        total_pendiente = total_facturado - total_pagado

        return {
            'num_facturas': len(facturas_periodo),
            'num_pagadas': sum(1 for f in facturas_periodo if f.pagada),
            'num_pendientes': sum(1 for f in facturas_periodo if not f.pagada),
            'total_facturado': total_facturado,
            'total_pagado': total_pagado,
            'total_pendiente': total_pendiente
        }

    def obtener_top_clientes(self, limite: int = 10) -> List[dict]:
        """
        Obtiene los clientes con mayor facturación.
        Retorna lista de diccionarios con cliente_id y total.
        """
        facturas = self.repository.listar_todas()

        # Agrupar por cliente
        ingresos_por_cliente = {}
        for factura in facturas:
            if factura.cliente_id not in ingresos_por_cliente:
                ingresos_por_cliente[factura.cliente_id] = 0
            ingresos_por_cliente[factura.cliente_id] += float(factura.calcular_total())

        # Ordenar y limitar
        top_clientes = sorted(
            [{'cliente_id': k, 'total': v} for k, v in ingresos_por_cliente.items()],
            key=lambda x: x['total'],
            reverse=True
        )[:limite]

        return top_clientes
