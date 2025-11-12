"""
Página de gestión de mascotas.
"""
import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import date

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.infrastructure.database import get_db
from src.services.mascota_service import MascotaService
from src.services.cliente_service import ClienteService
from src.domain.mascota import Especie

st.set_page_config(page_title="Gestión de Mascotas", page_icon="🐕", layout="wide")

st.title("🐕 Gestión de Mascotas")

# Crear pestañas
tab_listar, tab_crear, tab_editar = st.tabs(["📋 Listar Mascotas", "➕ Nueva Mascota", "✏️ Editar Mascota"])

# Obtener servicios
db = next(get_db())
servicio_mascota = MascotaService(db)
servicio_cliente = ClienteService(db)

# TAB: Listar Mascotas
with tab_listar:
    st.header("Lista de Mascotas")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        buscar = st.text_input("🔍 Buscar por nombre o microchip", key="buscar_mascota")

    with col2:
        # Filtro por cliente
        clientes = servicio_cliente.listar_clientes()
        opciones_filtro = ["Todos"] + [f"{c.dni} - {c.nombre}" for c in clientes]
        filtro_cliente = st.selectbox("Filtrar por cliente", opciones_filtro)

    with col3:
        incluir_inactivos = st.checkbox("Incluir inactivos", value=False)

    try:
        if buscar and len(buscar) >= 2:
            mascotas = servicio_mascota.buscar_mascotas(buscar)
        elif filtro_cliente != "Todos":
            cliente_id = int(filtro_cliente.split(" - ")[0])
            # Buscar cliente por DNI
            cliente = servicio_cliente.obtener_cliente_por_dni(filtro_cliente.split(" - ")[0])
            if cliente:
                mascotas = servicio_mascota.listar_mascotas_por_cliente(cliente.id, incluir_inactivos)
            else:
                mascotas = []
        else:
            mascotas = servicio_mascota.listar_todas_mascotas(incluir_inactivos)

        if mascotas:
            data = []
            for mascota in mascotas:
                # Obtener info del cliente
                cliente = servicio_cliente.obtener_cliente(mascota.cliente_id)

                data.append({
                    "ID": mascota.id,
                    "Nombre": mascota.nombre,
                    "Especie": mascota.especie.value,
                    "Raza": mascota.raza,
                    "Edad": mascota.edad_en_texto(),
                    "Dueño": cliente.nombre if cliente else "N/A",
                    "Microchip": mascota.microchip if mascota.microchip else "-",
                    "Activo": "✅" if mascota.activo else "❌"
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.metric("Total de mascotas", len(mascotas))
        else:
            st.info("No se encontraron mascotas.")

    except Exception as e:
        st.error(f"Error al cargar mascotas: {str(e)}")

# TAB: Crear Mascota
with tab_crear:
    st.header("Registrar Nueva Mascota")

    try:
        clientes_activos = servicio_cliente.listar_clientes(incluir_inactivos=False)

        if not clientes_activos:
            st.warning("⚠️ No hay clientes activos. Debe registrar un cliente primero.")
        else:
            with st.form("form_crear_mascota"):
                # Selector de cliente
                opciones_clientes = {f"{c.dni} - {c.nombre}": c.id for c in clientes_activos}
                cliente_seleccionado = st.selectbox(
                    "Cliente (Dueño) *",
                    options=list(opciones_clientes.keys())
                )

                col1, col2 = st.columns(2)

                with col1:
                    nombre = st.text_input("Nombre de la mascota *", max_chars=100)
                    especie = st.selectbox(
                        "Especie *",
                        options=[e.value for e in Especie]
                    )
                    raza = st.text_input("Raza *", max_chars=100)
                    fecha_nacimiento = st.date_input(
                        "Fecha de nacimiento *",
                        max_value=date.today(),
                        value=date.today()
                    )

                with col2:
                    sexo = st.selectbox("Sexo", options=["", "M", "F"])
                    color = st.text_input("Color", max_chars=50)
                    peso = st.number_input("Peso (kg)", min_value=0.0, max_value=500.0, value=0.0, step=0.1)
                    microchip = st.text_input("Microchip", max_chars=50)

                observaciones = st.text_area("Observaciones", max_chars=1000)

                submitted = st.form_submit_button("✅ Registrar Mascota", use_container_width=True)

                if submitted:
                    if not all([nombre, especie, raza, fecha_nacimiento]):
                        st.error("Por favor, complete todos los campos obligatorios (*)")
                    else:
                        try:
                            cliente_id = opciones_clientes[cliente_seleccionado]

                            nueva_mascota = servicio_mascota.registrar_mascota(
                                nombre=nombre.strip(),
                                especie=Especie(especie),
                                raza=raza.strip(),
                                fecha_nacimiento=fecha_nacimiento,
                                cliente_id=cliente_id,
                                sexo=sexo if sexo else None,
                                color=color.strip() if color else None,
                                peso=peso if peso > 0 else None,
                                microchip=microchip.strip() if microchip else None,
                                observaciones=observaciones.strip() if observaciones else None
                            )
                            st.success(f"✅ Mascota {nueva_mascota.nombre} registrada correctamente con ID: {nueva_mascota.id}")
                            st.balloons()
                        except ValueError as e:
                            st.error(f"❌ Error de validación: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Error al registrar mascota: {str(e)}")

    except Exception as e:
        st.error(f"Error: {str(e)}")

# TAB: Editar Mascota
with tab_editar:
    st.header("Editar Mascota")

    try:
        mascotas_activas = servicio_mascota.listar_todas_mascotas(incluir_inactivos=False)

        if mascotas_activas:
            # Selector de mascota con info del dueño
            opciones_mascotas = {}
            for m in mascotas_activas:
                cliente = servicio_cliente.obtener_cliente(m.cliente_id)
                opciones_mascotas[f"{m.nombre} ({m.especie.value}) - Dueño: {cliente.nombre}"] = m.id

            mascota_seleccionada = st.selectbox(
                "Seleccione una mascota",
                options=list(opciones_mascotas.keys())
            )

            if mascota_seleccionada:
                mascota_id = opciones_mascotas[mascota_seleccionada]
                mascota = servicio_mascota.obtener_mascota(mascota_id)

                if mascota:
                    with st.form("form_editar_mascota"):
                        st.info(f"Editando: **{mascota.nombre}** ({mascota.especie.value})")

                        col1, col2 = st.columns(2)

                        with col1:
                            nuevo_nombre = st.text_input("Nombre", value=mascota.nombre)
                            nueva_raza = st.text_input("Raza", value=mascota.raza)
                            nuevo_color = st.text_input(
                                "Color",
                                value=mascota.color if mascota.color else ""
                            )

                        with col2:
                            nuevo_peso = st.number_input(
                                "Peso (kg)",
                                min_value=0.0,
                                max_value=500.0,
                                value=float(mascota.peso) if mascota.peso else 0.0,
                                step=0.1
                            )
                            nuevo_microchip = st.text_input(
                                "Microchip",
                                value=mascota.microchip if mascota.microchip else ""
                            )

                        nuevas_observaciones = st.text_area(
                            "Observaciones",
                            value=mascota.observaciones if mascota.observaciones else ""
                        )

                        col_btn1, col_btn2 = st.columns(2)

                        with col_btn1:
                            actualizar = st.form_submit_button("💾 Actualizar", use_container_width=True)

                        with col_btn2:
                            dar_de_baja = st.form_submit_button("🗑️ Dar de Baja", use_container_width=True)

                        if actualizar:
                            try:
                                servicio_mascota.actualizar_mascota(
                                    mascota_id,
                                    nombre=nuevo_nombre.strip(),
                                    raza=nueva_raza.strip(),
                                    color=nuevo_color.strip() if nuevo_color else None,
                                    peso=nuevo_peso if nuevo_peso > 0 else None,
                                    microchip=nuevo_microchip.strip() if nuevo_microchip else None,
                                    observaciones=nuevas_observaciones.strip() if nuevas_observaciones else None
                                )
                                st.success("✅ Mascota actualizada correctamente")
                                st.rerun()
                            except ValueError as e:
                                st.error(f"❌ Error de validación: {str(e)}")
                            except Exception as e:
                                st.error(f"❌ Error al actualizar: {str(e)}")

                        if dar_de_baja:
                            if st.session_state.get('confirmar_baja_mascota'):
                                try:
                                    servicio_mascota.dar_de_baja(mascota_id)
                                    st.success("✅ Mascota dada de baja correctamente")
                                    st.session_state['confirmar_baja_mascota'] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error al dar de baja: {str(e)}")
                            else:
                                st.warning("⚠️ Haga clic nuevamente para confirmar la baja")
                                st.session_state['confirmar_baja_mascota'] = True
        else:
            st.info("No hay mascotas registradas.")

    except Exception as e:
        st.error(f"Error: {str(e)}")
