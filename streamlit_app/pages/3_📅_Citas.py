"""
Página de gestión de citas.
"""
import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime, date, time, timedelta

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.infrastructure.database import get_db
from src.services.cita_service import CitaService
from src.services.cliente_service import ClienteService
from src.services.mascota_service import MascotaService
from src.domain.cita import EstadoCita

st.set_page_config(page_title="Gestión de Citas", page_icon="📅", layout="wide")

st.title("📅 Gestión de Citas")

# Crear pestañas
tab_listar, tab_crear, tab_gestionar = st.tabs(["📋 Agenda", "➕ Nueva Cita", "✏️ Gestionar Cita"])

# Obtener servicios
db = next(get_db())
servicio_cita = CitaService(db)
servicio_cliente = ClienteService(db)
servicio_mascota = MascotaService(db)

# TAB: Listar Citas
with tab_listar:
    st.header("Agenda de Citas")

    col1, col2, col3 = st.columns(3)

    with col1:
        fecha_consulta = st.date_input("Fecha", value=date.today())

    with col2:
        veterinarios = ["Todos", "Dr. García", "Dra. Martínez", "Dr. López", "Dra. Fernández"]
        filtro_vet = st.selectbox("Veterinario", veterinarios)

    with col3:
        estados = ["Todos"] + [e.value for e in EstadoCita]
        filtro_estado = st.selectbox("Estado", estados)

    try:
        # Obtener citas del día
        citas = servicio_cita.listar_citas_del_dia(
            fecha_consulta,
            None if filtro_vet == "Todos" else filtro_vet
        )

        # Filtrar por estado
        if filtro_estado != "Todos":
            citas = [c for c in citas if c.estado.value == filtro_estado]

        if citas:
            data = []
            for cita in citas:
                cliente = servicio_cliente.obtener_cliente(cita.cliente_id)
                mascota = servicio_mascota.obtener_mascota(cita.mascota_id)

                data.append({
                    "ID": cita.id,
                    "Hora": cita.fecha_hora.strftime("%H:%M"),
                    "Cliente": cliente.nombre if cliente else "N/A",
                    "Mascota": f"{mascota.nombre} ({mascota.especie.value})" if mascota else "N/A",
                    "Veterinario": cita.veterinario_nombre,
                    "Motivo": cita.motivo[:50] + "..." if len(cita.motivo) > 50 else cita.motivo,
                    "Estado": cita.estado.value,
                    "Duración": f"{cita.duracion_minutos} min"
                })

            df = pd.DataFrame(data)

            # Colorear por estado
            def highlight_estado(row):
                if row['Estado'] == 'Completada':
                    return ['background-color: #d4edda'] * len(row)
                elif row['Estado'] == 'Cancelada':
                    return ['background-color: #f8d7da'] * len(row)
                elif row['Estado'] == 'En curso':
                    return ['background-color: #fff3cd'] * len(row)
                else:
                    return [''] * len(row)

            styled_df = df.style.apply(highlight_estado, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

            st.metric("Total de citas", len(citas))
        else:
            st.info("No hay citas para esta fecha y filtros seleccionados.")

    except Exception as e:
        st.error(f"Error al cargar citas: {str(e)}")

# TAB: Crear Cita
with tab_crear:
    st.header("Agendar Nueva Cita")

    try:
        clientes_activos = servicio_cliente.listar_clientes(incluir_inactivos=False)

        if not clientes_activos:
            st.warning("⚠️ No hay clientes activos. Debe registrar un cliente primero.")
        else:
            with st.form("form_crear_cita"):
                # Selector de cliente
                opciones_clientes = {f"{c.dni} - {c.nombre}": c.id for c in clientes_activos}
                cliente_seleccionado = st.selectbox(
                    "Cliente *",
                    options=list(opciones_clientes.keys())
                )

                cliente_id = opciones_clientes[cliente_seleccionado]

                # Obtener mascotas del cliente
                mascotas_cliente = servicio_mascota.listar_mascotas_por_cliente(cliente_id)

                if not mascotas_cliente:
                    st.warning("⚠️ Este cliente no tiene mascotas registradas.")
                    mascota_id = None
                else:
                    opciones_mascotas = {f"{m.nombre} ({m.especie.value})": m.id for m in mascotas_cliente}
                    mascota_seleccionada = st.selectbox(
                        "Mascota *",
                        options=list(opciones_mascotas.keys())
                    )
                    mascota_id = opciones_mascotas[mascota_seleccionada]

                col1, col2 = st.columns(2)

                with col1:
                    fecha_cita = st.date_input(
                        "Fecha *",
                        min_value=date.today(),
                        value=date.today()
                    )
                    hora_cita = st.time_input("Hora *", value=time(9, 0))

                with col2:
                    veterinario = st.selectbox(
                        "Veterinario *",
                        ["Dr. García", "Dra. Martínez", "Dr. López", "Dra. Fernández"]
                    )
                    duracion = st.number_input("Duración (minutos)", min_value=15, max_value=480, value=30, step=15)

                motivo = st.text_area("Motivo de la consulta *", max_chars=500)
                observaciones = st.text_area("Observaciones", max_chars=1000)

                submitted = st.form_submit_button("✅ Agendar Cita", use_container_width=True)

                if submitted:
                    if not all([mascota_id, fecha_cita, hora_cita, veterinario, motivo]):
                        st.error("Por favor, complete todos los campos obligatorios (*)")
                    else:
                        try:
                            fecha_hora = datetime.combine(fecha_cita, hora_cita)

                            nueva_cita = servicio_cita.agendar_cita(
                                cliente_id=cliente_id,
                                mascota_id=mascota_id,
                                veterinario_nombre=veterinario,
                                fecha_hora=fecha_hora,
                                motivo=motivo.strip(),
                                duracion_minutos=duracion,
                                observaciones=observaciones.strip() if observaciones else None
                            )
                            st.success(f"✅ Cita agendada correctamente con ID: {nueva_cita.id}")
                            st.balloons()
                        except ValueError as e:
                            st.error(f"❌ Error: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Error al agendar cita: {str(e)}")

    except Exception as e:
        st.error(f"Error: {str(e)}")

# TAB: Gestionar Cita
with tab_gestionar:
    st.header("Gestionar Cita")

    try:
        # Obtener citas no canceladas
        todas_citas = servicio_cita.listar_citas()
        citas_gestionables = [c for c in todas_citas if c.estado != EstadoCita.CANCELADA]

        if citas_gestionables:
            # Ordenar por fecha
            citas_gestionables.sort(key=lambda x: x.fecha_hora, reverse=True)

            opciones_citas = {}
            for c in citas_gestionables[:50]:  # Limitar a las últimas 50
                cliente = servicio_cliente.obtener_cliente(c.cliente_id)
                mascota = servicio_mascota.obtener_mascota(c.mascota_id)
                opciones_citas[
                    f"ID:{c.id} - {c.fecha_hora.strftime('%Y-%m-%d %H:%M')} - "
                    f"{cliente.nombre} / {mascota.nombre} - {c.estado.value}"
                ] = c.id

            cita_seleccionada = st.selectbox(
                "Seleccione una cita",
                options=list(opciones_citas.keys())
            )

            if cita_seleccionada:
                cita_id = opciones_citas[cita_seleccionada]
                cita = servicio_cita.obtener_cita(cita_id)

                if cita:
                    # Mostrar info de la cita
                    cliente = servicio_cliente.obtener_cliente(cita.cliente_id)
                    mascota = servicio_mascota.obtener_mascota(cita.mascota_id)

                    st.info(f"""
                    **Cita ID:** {cita.id}
                    **Cliente:** {cliente.nombre}
                    **Mascota:** {mascota.nombre} ({mascota.especie.value})
                    **Fecha y Hora:** {cita.fecha_hora.strftime('%Y-%m-%d %H:%M')}
                    **Veterinario:** {cita.veterinario_nombre}
                    **Estado:** {cita.estado.value}
                    **Motivo:** {cita.motivo}
                    """)

                    # Acciones según estado
                    if cita.estado == EstadoCita.PROGRAMADA:
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            if st.button("▶️ Iniciar Cita", use_container_width=True):
                                try:
                                    servicio_cita.iniciar_cita(cita_id)
                                    st.success("✅ Cita iniciada")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")

                        with col2:
                            with st.form("form_reprogramar"):
                                nueva_fecha = st.date_input("Nueva fecha", min_value=date.today())
                                nueva_hora = st.time_input("Nueva hora")
                                if st.form_submit_button("📅 Reprogramar"):
                                    try:
                                        nueva_fecha_hora = datetime.combine(nueva_fecha, nueva_hora)
                                        servicio_cita.reprogramar_cita(cita_id, nueva_fecha_hora)
                                        st.success("✅ Cita reprogramada")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {str(e)}")

                        with col3:
                            with st.form("form_cancelar"):
                                motivo_cancelacion = st.text_input("Motivo cancelación")
                                if st.form_submit_button("❌ Cancelar"):
                                    if motivo_cancelacion:
                                        try:
                                            servicio_cita.cancelar_cita(cita_id, motivo_cancelacion)
                                            st.success("✅ Cita cancelada")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Error: {str(e)}")
                                    else:
                                        st.error("Debe especificar el motivo")

                    elif cita.estado == EstadoCita.EN_CURSO:
                        with st.form("form_completar"):
                            st.subheader("Completar Cita")
                            diagnostico = st.text_area("Diagnóstico *", max_chars=2000)
                            tratamiento = st.text_area("Tratamiento", max_chars=2000)

                            if st.form_submit_button("✅ Completar Cita", use_container_width=True):
                                if diagnostico:
                                    try:
                                        servicio_cita.completar_cita(
                                            cita_id,
                                            diagnostico.strip(),
                                            tratamiento.strip() if tratamiento else None
                                        )
                                        st.success("✅ Cita completada correctamente")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {str(e)}")
                                else:
                                    st.error("El diagnóstico es obligatorio")

                    elif cita.estado == EstadoCita.COMPLETADA:
                        st.success("✅ Esta cita ya está completada")
                        if cita.diagnostico:
                            st.text_area("Diagnóstico", value=cita.diagnostico, disabled=True)
                        if cita.tratamiento:
                            st.text_area("Tratamiento", value=cita.tratamiento, disabled=True)

        else:
            st.info("No hay citas para gestionar.")

    except Exception as e:
        st.error(f"Error: {str(e)}")
