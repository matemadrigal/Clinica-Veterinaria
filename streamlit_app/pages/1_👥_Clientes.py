"""
Página de gestión de clientes.
"""
import streamlit as st
from pathlib import Path
import sys
import pandas as pd

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.infrastructure.database import get_db
from src.services.cliente_service import ClienteService
from src.domain.cliente import Cliente

st.set_page_config(page_title="Gestión de Clientes", page_icon="👥", layout="wide")

st.title("👥 Gestión de Clientes")

# Crear pestañas
tab_listar, tab_crear, tab_editar = st.tabs(["📋 Listar Clientes", "➕ Nuevo Cliente", "✏️ Editar Cliente"])

# Obtener servicio
db = next(get_db())
servicio = ClienteService(db)

# TAB: Listar Clientes
with tab_listar:
    st.header("Lista de Clientes")

    col1, col2 = st.columns([3, 1])

    with col1:
        buscar = st.text_input("🔍 Buscar por nombre, DNI o email", key="buscar_cliente")

    with col2:
        incluir_inactivos = st.checkbox("Incluir inactivos", value=False)

    try:
        if buscar and len(buscar) >= 2:
            clientes = servicio.buscar_clientes(buscar)
        else:
            clientes = servicio.listar_clientes(incluir_inactivos=incluir_inactivos)

        if clientes:
            # Crear DataFrame
            data = []
            for cliente in clientes:
                data.append({
                    "ID": cliente.id,
                    "DNI": cliente.dni,
                    "Nombre": cliente.nombre,
                    "Teléfono": cliente.telefono,
                    "Email": cliente.email,
                    "Activo": "✅" if cliente.activo else "❌",
                    "Fecha Registro": cliente.fecha_registro.strftime("%Y-%m-%d")
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.metric("Total de clientes", len(clientes))
        else:
            st.info("No se encontraron clientes.")

    except Exception as e:
        st.error(f"Error al cargar clientes: {str(e)}")

# TAB: Crear Cliente
with tab_crear:
    st.header("Registrar Nuevo Cliente")

    with st.form("form_crear_cliente"):
        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Nombre completo *", max_chars=200)
            dni = st.text_input("DNI/NIF *", max_chars=20, help="Formato: 12345678A")
            telefono = st.text_input("Teléfono *", max_chars=20, help="Ej: 612345678 o +34612345678")

        with col2:
            email = st.text_input("Email *", max_chars=100)
            direccion = st.text_input("Dirección", max_chars=300)

        notas = st.text_area("Notas / Observaciones", max_chars=1000)

        submitted = st.form_submit_button("✅ Registrar Cliente", use_container_width=True)

        if submitted:
            if not all([nombre, dni, telefono, email]):
                st.error("Por favor, complete todos los campos obligatorios (*)")
            else:
                try:
                    nuevo_cliente = servicio.registrar_cliente(
                        nombre=nombre.strip(),
                        dni=dni.strip().upper(),
                        telefono=telefono.strip(),
                        email=email.strip().lower(),
                        direccion=direccion.strip() if direccion else None,
                        notas=notas.strip() if notas else None
                    )
                    st.success(f"✅ Cliente {nuevo_cliente.nombre} registrado correctamente con ID: {nuevo_cliente.id}")
                    st.balloons()
                except ValueError as e:
                    st.error(f"❌ Error de validación: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error al registrar cliente: {str(e)}")

# TAB: Editar Cliente
with tab_editar:
    st.header("Editar Cliente")

    try:
        clientes_activos = servicio.listar_clientes(incluir_inactivos=False)

        if clientes_activos:
            # Selector de cliente
            opciones_clientes = {f"{c.dni} - {c.nombre}": c.id for c in clientes_activos}
            cliente_seleccionado = st.selectbox(
                "Seleccione un cliente",
                options=list(opciones_clientes.keys())
            )

            if cliente_seleccionado:
                cliente_id = opciones_clientes[cliente_seleccionado]
                cliente = servicio.obtener_cliente(cliente_id)

                if cliente:
                    with st.form("form_editar_cliente"):
                        col1, col2 = st.columns(2)

                        with col1:
                            nuevo_nombre = st.text_input("Nombre completo", value=cliente.nombre)
                            nuevo_telefono = st.text_input("Teléfono", value=cliente.telefono)
                            nuevo_email = st.text_input("Email", value=cliente.email)

                        with col2:
                            nueva_direccion = st.text_input(
                                "Dirección",
                                value=cliente.direccion if cliente.direccion else ""
                            )
                            nuevas_notas = st.text_area(
                                "Notas",
                                value=cliente.notas if cliente.notas else ""
                            )

                        col_btn1, col_btn2 = st.columns(2)

                        with col_btn1:
                            actualizar = st.form_submit_button("💾 Actualizar", use_container_width=True)

                        with col_btn2:
                            dar_de_baja = st.form_submit_button("🗑️ Dar de Baja", use_container_width=True)

                        if actualizar:
                            try:
                                servicio.actualizar_cliente(
                                    cliente_id,
                                    nombre=nuevo_nombre.strip(),
                                    telefono=nuevo_telefono.strip(),
                                    email=nuevo_email.strip().lower(),
                                    direccion=nueva_direccion.strip() if nueva_direccion else None,
                                    notas=nuevas_notas.strip() if nuevas_notas else None
                                )
                                st.success("✅ Cliente actualizado correctamente")
                                st.rerun()
                            except ValueError as e:
                                st.error(f"❌ Error de validación: {str(e)}")
                            except Exception as e:
                                st.error(f"❌ Error al actualizar: {str(e)}")

                        if dar_de_baja:
                            if st.session_state.get('confirmar_baja'):
                                try:
                                    servicio.dar_de_baja(cliente_id)
                                    st.success("✅ Cliente dado de baja correctamente")
                                    st.session_state['confirmar_baja'] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error al dar de baja: {str(e)}")
                            else:
                                st.warning("⚠️ Haga clic nuevamente para confirmar la baja")
                                st.session_state['confirmar_baja'] = True
        else:
            st.info("No hay clientes registrados.")

    except Exception as e:
        st.error(f"Error: {str(e)}")
