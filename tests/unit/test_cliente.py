"""
Tests unitarios para la entidad Cliente.
"""
import pytest
from datetime import datetime
from src.domain.cliente import Cliente


class TestCliente:
    """Test suite para la entidad Cliente"""

    def test_crear_cliente_valido(self):
        """Test: crear un cliente con datos válidos"""
        cliente = Cliente(
            nombre="Juan Pérez",
            dni="12345678Z",
            telefono="612345678",
            email="juan@example.com"
        )

        assert cliente.nombre == "Juan Pérez"
        assert cliente.dni == "12345678Z"
        assert cliente.activo is True

    def test_validar_dni_correcto(self):
        """Test: validación de DNI correcto"""
        assert Cliente.validar_dni("12345678Z") is True
        assert Cliente.validar_dni("87654321X") is True

    def test_validar_dni_incorrecto(self):
        """Test: validación de DNI incorrecto"""
        assert Cliente.validar_dni("12345678A") is False  # Letra incorrecta
        assert Cliente.validar_dni("1234567Z") is False   # Pocos dígitos
        assert Cliente.validar_dni("123456789Z") is False # Muchos dígitos
        assert Cliente.validar_dni("") is False
        assert Cliente.validar_dni("ABCD1234Z") is False

    def test_validar_email_correcto(self):
        """Test: validación de email correcto"""
        assert Cliente.validar_email("test@example.com") is True
        assert Cliente.validar_email("user.name@domain.co.uk") is True

    def test_validar_email_incorrecto(self):
        """Test: validación de email incorrecto"""
        assert Cliente.validar_email("invalido") is False
        assert Cliente.validar_email("@example.com") is False
        assert Cliente.validar_email("test@") is False
        assert Cliente.validar_email("") is False

    def test_validar_telefono_correcto(self):
        """Test: validación de teléfono correcto"""
        assert Cliente.validar_telefono("612345678") is True
        assert Cliente.validar_telefono("+34612345678") is True
        assert Cliente.validar_telefono("912345678") is True
        assert Cliente.validar_telefono("612 345 678") is True

    def test_validar_telefono_incorrecto(self):
        """Test: validación de teléfono incorrecto"""
        assert Cliente.validar_telefono("512345678") is False  # No empieza con 6-9
        assert Cliente.validar_telefono("12345") is False      # Muy corto
        assert Cliente.validar_telefono("") is False

    def test_crear_cliente_dni_invalido(self):
        """Test: crear cliente con DNI inválido debe fallar"""
        with pytest.raises(ValueError, match="DNI/NIF inválido"):
            Cliente(
                nombre="Juan Pérez",
                dni="00000000A",
                telefono="612345678",
                email="juan@example.com"
            )

    def test_crear_cliente_email_invalido(self):
        """Test: crear cliente con email inválido debe fallar"""
        with pytest.raises(ValueError, match="Email inválido"):
            Cliente(
                nombre="Juan Pérez",
                dni="12345678Z",
                telefono="612345678",
                email="email_invalido"
            )

    def test_crear_cliente_nombre_vacio(self):
        """Test: crear cliente con nombre vacío debe fallar"""
        with pytest.raises(ValueError, match="nombre debe tener al menos 2 caracteres"):
            Cliente(
                nombre="",
                dni="12345678Z",
                telefono="612345678",
                email="juan@example.com"
            )

    def test_desactivar_cliente(self):
        """Test: desactivar cliente"""
        cliente = Cliente(
            nombre="Juan Pérez",
            dni="12345678Z",
            telefono="612345678",
            email="juan@example.com"
        )

        assert cliente.activo is True
        cliente.desactivar()
        assert cliente.activo is False

    def test_activar_cliente(self):
        """Test: activar cliente desactivado"""
        cliente = Cliente(
            nombre="Juan Pérez",
            dni="12345678Z",
            telefono="612345678",
            email="juan@example.com"
        )

        cliente.desactivar()
        assert cliente.activo is False

        cliente.activar()
        assert cliente.activo is True

    def test_actualizar_datos_cliente(self):
        """Test: actualizar datos de cliente"""
        cliente = Cliente(
            nombre="Juan Pérez",
            dni="12345678Z",
            telefono="612345678",
            email="juan@example.com"
        )

        cliente.actualizar_datos(
            nombre="Juan Pérez García",
            telefono="698765432",
            email="juan.perez@example.com"
        )

        assert cliente.nombre == "Juan Pérez García"
        assert cliente.telefono == "698765432"
        assert cliente.email == "juan.perez@example.com"

    def test_actualizar_datos_invalidos(self):
        """Test: actualizar con datos inválidos debe fallar"""
        cliente = Cliente(
            nombre="Juan Pérez",
            dni="12345678Z",
            telefono="612345678",
            email="juan@example.com"
        )

        with pytest.raises(ValueError):
            cliente.actualizar_datos(email="email_invalido")
