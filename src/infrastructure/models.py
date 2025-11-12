"""
Modelos ORM de SQLAlchemy para persistencia
Mapean las entidades del dominio a tablas de base de datos
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.infrastructure.database import Base


class ClienteModel(Base):
    """Modelo ORM para la entidad Cliente"""
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    dni = Column(String(20), unique=True, nullable=False, index=True)
    telefono = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    direccion = Column(String(300), nullable=True)
    notas = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.now, nullable=False)

    # Relaciones
    mascotas = relationship("MascotaModel", back_populates="cliente")
    citas = relationship("CitaModel", back_populates="cliente")
    facturas = relationship("FacturaModel", back_populates="cliente")

    def __repr__(self):
        return f"<ClienteModel(id={self.id}, dni='{self.dni}', nombre='{self.nombre}')>"


class MascotaModel(Base):
    """Modelo ORM para la entidad Mascota"""
    __tablename__ = "mascotas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    especie = Column(String(50), nullable=False)
    raza = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    sexo = Column(String(1), nullable=True)
    color = Column(String(50), nullable=True)
    peso = Column(Float, nullable=True)
    microchip = Column(String(50), nullable=True, unique=True)
    observaciones = Column(Text, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.now, nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    # Relaciones
    cliente = relationship("ClienteModel", back_populates="mascotas")
    citas = relationship("CitaModel", back_populates="mascota")

    def __repr__(self):
        return f"<MascotaModel(id={self.id}, nombre='{self.nombre}', especie='{self.especie}')>"


class CitaModel(Base):
    """Modelo ORM para la entidad Cita"""
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    mascota_id = Column(Integer, ForeignKey("mascotas.id"), nullable=False)
    veterinario_nombre = Column(String(200), nullable=False, index=True)
    fecha_hora = Column(DateTime, nullable=False, index=True)
    duracion_minutos = Column(Integer, default=30, nullable=False)
    motivo = Column(String(500), nullable=False)
    estado = Column(String(20), nullable=False, default="Programada", index=True)
    observaciones = Column(Text, nullable=True)
    diagnostico = Column(Text, nullable=True)
    tratamiento = Column(Text, nullable=True)
    motivo_cancelacion = Column(String(500), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_modificacion = Column(DateTime, nullable=True)

    # Relaciones
    cliente = relationship("ClienteModel", back_populates="citas")
    mascota = relationship("MascotaModel", back_populates="citas")
    facturas = relationship("FacturaModel", back_populates="cita")

    def __repr__(self):
        return f"<CitaModel(id={self.id}, fecha='{self.fecha_hora}', veterinario='{self.veterinario_nombre}')>"


class FacturaModel(Base):
    """Modelo ORM para la entidad Factura"""
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)
    numero_factura = Column(String(50), unique=True, nullable=False, index=True)
    cita_id = Column(Integer, ForeignKey("citas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    fecha_emision = Column(DateTime, nullable=False)
    pagada = Column(Boolean, default=False, nullable=False)
    fecha_pago = Column(DateTime, nullable=True)
    metodo_pago = Column(String(50), nullable=True)
    observaciones = Column(Text, nullable=True)

    # Relaciones
    cita = relationship("CitaModel", back_populates="facturas")
    cliente = relationship("ClienteModel", back_populates="facturas")
    lineas = relationship("LineaFacturaModel", back_populates="factura", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FacturaModel(id={self.id}, numero='{self.numero_factura}', pagada={self.pagada})>"


class LineaFacturaModel(Base):
    """Modelo ORM para la entidad LineaFactura"""
    __tablename__ = "lineas_factura"

    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id"), nullable=False)
    concepto = Column(String(300), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    iva_porcentaje = Column(Numeric(5, 2), nullable=False)

    # Relaciones
    factura = relationship("FacturaModel", back_populates="lineas")

    def __repr__(self):
        return f"<LineaFacturaModel(id={self.id}, concepto='{self.concepto}', cantidad={self.cantidad})>"
