"""
Tests unitarios para la entidad Mascota.
"""
import pytest
from datetime import date
from src.domain.mascota import Mascota, Especie


class TestMascota:
    """Test suite para la entidad Mascota"""

    def test_crear_mascota_valida(self):
        """Test: crear una mascota con datos válidos"""
        mascota = Mascota(
            nombre="Max",
            especie=Especie.PERRO,
            raza="Labrador",
            fecha_nacimiento=date(2020, 1, 15),
            cliente_id=1
        )

        assert mascota.nombre == "Max"
        assert mascota.especie == Especie.PERRO
        assert mascota.raza == "Labrador"
        assert mascota.activo is True

    def test_crear_mascota_nombre_vacio(self):
        """Test: crear mascota con nombre vacío debe fallar"""
        with pytest.raises(ValueError, match="nombre es obligatorio"):
            Mascota(
                nombre="",
                especie=Especie.PERRO,
                raza="Labrador",
                fecha_nacimiento=date(2020, 1, 15),
                cliente_id=1
            )

    def test_crear_mascota_fecha_futura(self):
        """Test: crear mascota con fecha futura debe fallar"""
        with pytest.raises(ValueError, match="fecha de nacimiento no puede ser futura"):
            from datetime import timedelta
            fecha_futura = date.today() + timedelta(days=1)
            Mascota(
                nombre="Max",
                especie=Especie.PERRO,
                raza="Labrador",
                fecha_nacimiento=fecha_futura,
                cliente_id=1
            )

    def test_crear_mascota_sin_cliente(self):
        """Test: crear mascota sin cliente debe fallar"""
        with pytest.raises(ValueError, match="asociarse a un cliente válido"):
            Mascota(
                nombre="Max",
                especie=Especie.PERRO,
                raza="Labrador",
                fecha_nacimiento=date(2020, 1, 15),
                cliente_id=0
            )

    def test_calcular_edad(self):
        """Test: calcular edad de mascota"""
        # Mascota de aproximadamente 3 años
        fecha_nac = date(2021, 1, 1)
        mascota = Mascota(
            nombre="Max",
            especie=Especie.PERRO,
            raza="Labrador",
            fecha_nacimiento=fecha_nac,
            cliente_id=1
        )

        edad = mascota.calcular_edad()
        assert isinstance(edad, dict)
        assert 'años' in edad
        assert 'meses' in edad
        assert edad['años'] >= 0
        assert edad['meses'] >= 0

    def test_edad_en_texto(self):
        """Test: edad en formato texto"""
        mascota = Mascota(
            nombre="Max",
            especie=Especie.PERRO,
            raza="Labrador",
            fecha_nacimiento=date(2021, 1, 1),
            cliente_id=1
        )

        edad_texto = mascota.edad_en_texto()
        assert isinstance(edad_texto, str)
        assert len(edad_texto) > 0

    def test_desactivar_mascota(self):
        """Test: desactivar mascota"""
        mascota = Mascota(
            nombre="Max",
            especie=Especie.PERRO,
            raza="Labrador",
            fecha_nacimiento=date(2020, 1, 15),
            cliente_id=1
        )

        assert mascota.activo is True
        mascota.desactivar()
        assert mascota.activo is False

    def test_actualizar_datos_mascota(self):
        """Test: actualizar datos de mascota"""
        mascota = Mascota(
            nombre="Max",
            especie=Especie.PERRO,
            raza="Labrador",
            fecha_nacimiento=date(2020, 1, 15),
            cliente_id=1
        )

        mascota.actualizar_datos(
            nombre="Maximus",
            raza="Golden Retriever",
            peso=30.5,
            color="Dorado"
        )

        assert mascota.nombre == "Maximus"
        assert mascota.raza == "Golden Retriever"
        assert mascota.peso == 30.5
        assert mascota.color == "Dorado"

    def test_sexo_valido(self):
        """Test: sexo válido M o F"""
        mascota_m = Mascota(
            nombre="Max",
            especie=Especie.PERRO,
            raza="Labrador",
            fecha_nacimiento=date(2020, 1, 15),
            cliente_id=1,
            sexo='M'
        )
        assert mascota_m.sexo == 'M'

        mascota_f = Mascota(
            nombre="Luna",
            especie=Especie.GATO,
            raza="Persa",
            fecha_nacimiento=date(2021, 5, 10),
            cliente_id=1,
            sexo='F'
        )
        assert mascota_f.sexo == 'F'

    def test_sexo_invalido(self):
        """Test: sexo inválido debe fallar"""
        with pytest.raises(ValueError, match="sexo debe ser 'M' o 'F'"):
            Mascota(
                nombre="Max",
                especie=Especie.PERRO,
                raza="Labrador",
                fecha_nacimiento=date(2020, 1, 15),
                cliente_id=1,
                sexo='X'
            )

    def test_peso_negativo(self):
        """Test: peso negativo debe fallar"""
        with pytest.raises(ValueError, match="peso debe ser positivo"):
            Mascota(
                nombre="Max",
                especie=Especie.PERRO,
                raza="Labrador",
                fecha_nacimiento=date(2020, 1, 15),
                cliente_id=1,
                peso=-5.0
            )
