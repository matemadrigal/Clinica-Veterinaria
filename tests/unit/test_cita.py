"""
Tests unitarios para la entidad Cita.
"""
import pytest
from datetime import datetime, timedelta
from src.domain.cita import Cita, EstadoCita


class TestCita:
    """Test suite para la entidad Cita"""

    def test_crear_cita_valida(self):
        """Test: crear una cita con datos válidos"""
        fecha_futura = datetime.now() + timedelta(days=1)

        cita = Cita(
            cliente_id=1,
            mascota_id=1,
            veterinario_nombre="Dr. García",
            fecha_hora=fecha_futura,
            motivo="Revisión anual"
        )

        assert cita.cliente_id == 1
        assert cita.mascota_id == 1
        assert cita.estado == EstadoCita.PROGRAMADA
        assert cita.duracion_minutos == 30

    def test_crear_cita_fecha_pasada_sin_id(self):
        """Test: crear cita nueva con fecha pasada debe fallar"""
        fecha_pasada = datetime.now() - timedelta(days=1)

        with pytest.raises(ValueError, match="fecha y hora deben ser futuras"):
            Cita(
                cliente_id=1,
                mascota_id=1,
                veterinario_nombre="Dr. García",
                fecha_hora=fecha_pasada,
                motivo="Revisión"
            )

    def test_crear_cita_motivo_corto(self):
        """Test: crear cita con motivo muy corto debe fallar"""
        fecha_futura = datetime.now() + timedelta(days=1)

        with pytest.raises(ValueError, match="motivo debe tener al menos 3 caracteres"):
            Cita(
                cliente_id=1,
                mascota_id=1,
                veterinario_nombre="Dr. García",
                fecha_hora=fecha_futura,
                motivo="AB"
            )

    def test_completar_cita(self):
        """Test: completar una cita"""
        fecha_futura = datetime.now() + timedelta(days=1)

        cita = Cita(
            cliente_id=1,
            mascota_id=1,
            veterinario_nombre="Dr. García",
            fecha_hora=fecha_futura,
            motivo="Revisión anual"
        )

        cita.completar(
            diagnostico="Mascota en buen estado de salud",
            tratamiento="Vacunación antirrábica aplicada"
        )

        assert cita.estado == EstadoCita.COMPLETADA
        assert cita.diagnostico == "Mascota en buen estado de salud"
        assert cita.tratamiento == "Vacunación antirrábica aplicada"

    def test_completar_cita_sin_diagnostico(self):
        """Test: completar cita sin diagnóstico debe fallar"""
        fecha_futura = datetime.now() + timedelta(days=1)

        cita = Cita(
            cliente_id=1,
            mascota_id=1,
            veterinario_nombre="Dr. García",
            fecha_hora=fecha_futura,
            motivo="Revisión"
        )

        with pytest.raises(ValueError, match="diagnóstico es obligatorio"):
            cita.completar(diagnostico="")

    def test_cancelar_cita(self):
        """Test: cancelar una cita"""
        fecha_futura = datetime.now() + timedelta(days=1)

        cita = Cita(
            cliente_id=1,
            mascota_id=1,
            veterinario_nombre="Dr. García",
            fecha_hora=fecha_futura,
            motivo="Revisión"
        )

        cita.cancelar("Cliente no puede asistir")

        assert cita.estado == EstadoCita.CANCELADA
        assert cita.motivo_cancelacion == "Cliente no puede asistir"

    def test_cancelar_cita_completada(self):
        """Test: cancelar cita completada debe fallar"""
        fecha_futura = datetime.now() + timedelta(days=1)

        cita = Cita(
            cliente_id=1,
            mascota_id=1,
            veterinario_nombre="Dr. García",
            fecha_hora=fecha_futura,
            motivo="Revisión"
        )

        cita.completar("Mascota sana")

        with pytest.raises(ValueError, match="No se puede cancelar una cita completada"):
            cita.cancelar("Motivo")

    def test_reprogramar_cita(self):
        """Test: reprogramar una cita"""
        fecha_futura = datetime.now() + timedelta(days=1)
        nueva_fecha = datetime.now() + timedelta(days=2)

        cita = Cita(
            cliente_id=1,
            mascota_id=1,
            veterinario_nombre="Dr. García",
            fecha_hora=fecha_futura,
            motivo="Revisión"
        )

        cita.reprogramar(nueva_fecha)

        assert cita.fecha_hora == nueva_fecha
        assert cita.estado == EstadoCita.PROGRAMADA

    def test_iniciar_cita(self):
        """Test: iniciar una cita"""
        fecha_futura = datetime.now() + timedelta(days=1)

        cita = Cita(
            cliente_id=1,
            mascota_id=1,
            veterinario_nombre="Dr. García",
            fecha_hora=fecha_futura,
            motivo="Revisión"
        )

        cita.iniciar()

        assert cita.estado == EstadoCita.EN_CURSO

    def test_obtener_hora_fin(self):
        """Test: calcular hora de fin de cita"""
        fecha_futura = datetime.now() + timedelta(days=1)

        cita = Cita(
            cliente_id=1,
            mascota_id=1,
            veterinario_nombre="Dr. García",
            fecha_hora=fecha_futura,
            motivo="Revisión",
            duracion_minutos=45
        )

        hora_fin = cita.obtener_hora_fin()

        assert hora_fin == fecha_futura + timedelta(minutes=45)

    def test_solapa_con_otra_cita(self):
        """Test: detectar solape entre citas"""
        fecha_base = datetime.now() + timedelta(days=1)

        cita1 = Cita(
            id=1,
            cliente_id=1,
            mascota_id=1,
            veterinario_nombre="Dr. García",
            fecha_hora=fecha_base,
            motivo="Revisión",
            duracion_minutos=30
        )

        # Cita que se solapa (mismo veterinario, 15 minutos después)
        cita2 = Cita(
            id=2,
            cliente_id=2,
            mascota_id=2,
            veterinario_nombre="Dr. García",
            fecha_hora=fecha_base + timedelta(minutes=15),
            motivo="Vacunación",
            duracion_minutos=30
        )

        assert cita1.solapa_con(cita2) is True

        # Cita que no se solapa (distinto veterinario)
        cita3 = Cita(
            id=3,
            cliente_id=3,
            mascota_id=3,
            veterinario_nombre="Dra. Martínez",
            fecha_hora=fecha_base,
            motivo="Consulta",
            duracion_minutos=30
        )

        assert cita1.solapa_con(cita3) is False

        # Cita que no se solapa (mismo veterinario pero después)
        cita4 = Cita(
            id=4,
            cliente_id=4,
            mascota_id=4,
            veterinario_nombre="Dr. García",
            fecha_hora=fecha_base + timedelta(minutes=30),
            motivo="Consulta",
            duracion_minutos=30
        )

        assert cita1.solapa_con(cita4) is False
