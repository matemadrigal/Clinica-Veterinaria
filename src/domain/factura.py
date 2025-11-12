"""
Módulo del dominio: Factura y Línea de Factura
Representa la facturación de servicios veterinarios
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


@dataclass
class LineaFactura:
    """
    Representa una línea de factura.
    Cumple con SRP: responsable únicamente de la lógica de una línea.
    """
    concepto: str
    cantidad: int
    precio_unitario: Decimal
    iva_porcentaje: Decimal
    id: Optional[int] = None
    factura_id: Optional[int] = None

    def __post_init__(self):
        """Validaciones y conversiones"""
        # Convertir a Decimal si se recibe float
        if isinstance(self.precio_unitario, (int, float)):
            self.precio_unitario = Decimal(str(self.precio_unitario))
        if isinstance(self.iva_porcentaje, (int, float)):
            self.iva_porcentaje = Decimal(str(self.iva_porcentaje))
        self.validar()

    def validar(self) -> None:
        """
        Valida los datos de la línea de factura.
        Lanza ValueError si algún campo no es válido.
        """
        if not self.concepto or len(self.concepto.strip()) < 3:
            raise ValueError("El concepto debe tener al menos 3 caracteres")

        if self.cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva")

        if self.precio_unitario < 0:
            raise ValueError("El precio unitario no puede ser negativo")

        if self.iva_porcentaje < 0 or self.iva_porcentaje > 100:
            raise ValueError("El IVA debe estar entre 0 y 100")

    def calcular_subtotal(self) -> Decimal:
        """Calcula el subtotal (cantidad × precio unitario)"""
        return Decimal(str(self.cantidad)) * self.precio_unitario

    def calcular_iva(self) -> Decimal:
        """Calcula el importe del IVA"""
        subtotal = self.calcular_subtotal()
        return subtotal * (self.iva_porcentaje / Decimal('100'))

    def calcular_total(self) -> Decimal:
        """Calcula el total con IVA incluido"""
        return self.calcular_subtotal() + self.calcular_iva()

    def __str__(self) -> str:
        return f"Línea({self.concepto} - {self.cantidad}x{self.precio_unitario}€)"

    def __repr__(self) -> str:
        return (f"LineaFactura(id={self.id}, concepto='{self.concepto}', "
                f"cantidad={self.cantidad}, precio={self.precio_unitario})")


@dataclass
class Factura:
    """
    Entidad Factura - representa una factura de servicios.
    Cumple con SRP: responsable únicamente de la lógica de facturación.
    """
    numero_factura: str
    cita_id: int
    cliente_id: int
    fecha_emision: datetime
    id: Optional[int] = None
    lineas: List[LineaFactura] = field(default_factory=list)
    pagada: bool = False
    fecha_pago: Optional[datetime] = None
    metodo_pago: Optional[str] = None  # 'Efectivo', 'Tarjeta', 'Transferencia'
    observaciones: Optional[str] = None

    def __post_init__(self):
        """Validaciones en la creación de la factura"""
        self.validar()

    def validar(self) -> None:
        """
        Valida los datos de la factura según las reglas de negocio.
        Lanza ValueError si algún campo no es válido.
        """
        if not self.numero_factura or len(self.numero_factura.strip()) < 1:
            raise ValueError("El número de factura es obligatorio")

        if self.cita_id is None or self.cita_id <= 0:
            raise ValueError("Debe asociarse a una cita válida")

        if self.cliente_id is None or self.cliente_id <= 0:
            raise ValueError("Debe asociarse a un cliente válido")

        if not self.fecha_emision:
            raise ValueError("La fecha de emisión es obligatoria")

        if self.fecha_emision > datetime.now():
            raise ValueError("La fecha de emisión no puede ser futura")

        if self.pagada and not self.fecha_pago:
            raise ValueError("Si está pagada debe tener fecha de pago")

        if self.fecha_pago and self.fecha_pago < self.fecha_emision:
            raise ValueError("La fecha de pago no puede ser anterior a la emisión")

        if self.metodo_pago and self.metodo_pago not in ['Efectivo', 'Tarjeta', 'Transferencia']:
            raise ValueError("Método de pago inválido")

    def agregar_linea(self, linea: LineaFactura) -> None:
        """
        Agrega una línea a la factura.
        Valida que la factura no esté pagada antes de agregar.
        """
        if self.pagada:
            raise ValueError("No se pueden agregar líneas a una factura pagada")

        linea.validar()
        self.lineas.append(linea)

    def eliminar_linea(self, linea: LineaFactura) -> None:
        """
        Elimina una línea de la factura.
        Valida que la factura no esté pagada antes de eliminar.
        """
        if self.pagada:
            raise ValueError("No se pueden eliminar líneas de una factura pagada")

        if linea in self.lineas:
            self.lineas.remove(linea)
        else:
            raise ValueError("La línea no existe en esta factura")

    def calcular_subtotal(self) -> Decimal:
        """Calcula el subtotal de todas las líneas (sin IVA)"""
        return sum((linea.calcular_subtotal() for linea in self.lineas), Decimal('0'))

    def calcular_total_iva(self) -> Decimal:
        """Calcula el total de IVA de todas las líneas"""
        return sum((linea.calcular_iva() for linea in self.lineas), Decimal('0'))

    def calcular_total(self) -> Decimal:
        """Calcula el total de la factura (con IVA incluido)"""
        return sum((linea.calcular_total() for linea in self.lineas), Decimal('0'))

    def marcar_como_pagada(self, metodo_pago: str, fecha_pago: Optional[datetime] = None) -> None:
        """
        Marca la factura como pagada.
        Registra el método de pago y fecha.
        """
        if self.pagada:
            raise ValueError("La factura ya está marcada como pagada")

        if not self.lineas:
            raise ValueError("No se puede marcar como pagada una factura sin líneas")

        if metodo_pago not in ['Efectivo', 'Tarjeta', 'Transferencia']:
            raise ValueError("Método de pago inválido")

        self.pagada = True
        self.metodo_pago = metodo_pago
        self.fecha_pago = fecha_pago or datetime.now()

    def obtener_resumen(self) -> dict:
        """
        Retorna un resumen de la factura con todos los totales.
        """
        subtotal = self.calcular_subtotal()
        total_iva = self.calcular_total_iva()
        total = self.calcular_total()

        return {
            'numero_factura': self.numero_factura,
            'fecha_emision': self.fecha_emision,
            'num_lineas': len(self.lineas),
            'subtotal': float(subtotal),
            'iva': float(total_iva),
            'total': float(total),
            'pagada': self.pagada,
            'metodo_pago': self.metodo_pago,
            'fecha_pago': self.fecha_pago
        }

    def __str__(self) -> str:
        return f"Factura({self.numero_factura} - {self.calcular_total()}€)"

    def __repr__(self) -> str:
        return (f"Factura(id={self.id}, numero='{self.numero_factura}', "
                f"total={self.calcular_total()}€, pagada={self.pagada})")
