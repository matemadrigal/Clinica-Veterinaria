"""
Página de gestión de facturas.
"""
import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime
from decimal import Decimal

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.infrastructure.database import get_db
from src.services.factura_service import FacturaService
from src.services.cita_service import CitaService
from src.services.cliente_service import ClienteService
from src.services.mascota_service import MascotaService
from src.domain.cita import EstadoCita

st.set_page_config(page_title="Facturación", page_icon="💰", layout="wide")

st.title("💰 Facturación")

tab_listar, tab_crear, tab_gestionar = st.tabs(["📋 Facturas", "➕ Nueva Factura", "💳 Gestionar Pago"])

db = next(get_db())
servicio_factura = FacturaService(db)
servicio_cita = CitaService(db)
servicio_cliente = ClienteService(db)
servicio_mascota = MascotaService(db)

# TAB: Listar Facturas
with tab_listar:
    st.header("Lista de Facturas")

    col1, col2 = st.columns([3, 1])
    with col1:
        buscar_num = st.text_input("🔍 Buscar por número de factura")
    with col2:
        filtro_pago = st.selectbox("Estado", ["Todas", "Pagadas", "Pendientes"])

    try:
        facturas = servicio_factura.listar_facturas()

        if buscar_num:
            facturas = [f for f in facturas if buscar_num.lower() in f.numero_factura.lower()]

        if filtro_pago == "Pagadas":
            facturas = [f for f in facturas if f.pagada]
        elif filtro_pago == "Pendientes":
            facturas = [f for f in facturas if not f.pagada]

        if facturas:
            data = []
            for factura in facturas:
                cliente = servicio_cliente.obtener_cliente(factura.cliente_id)
                data.append({
                    "Número": factura.numero_factura,
                    "Cliente": cliente.nombre if cliente else "N/A",
                    "Fecha": factura.fecha_emision.strftime("%Y-%m-%d"),
                    "Total": f"{float(factura.calcular_total()):.2f}€",
                    "Estado": "✅ Pagada" if factura.pagada else "⏳ Pendiente",
                    "Método": factura.metodo_pago if factura.metodo_pago else "-"
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            total_facturado = sum(float(f.calcular_total()) for f in facturas)
            total_pagado = sum(float(f.calcular_total()) for f in facturas if f.pagada)

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Facturas", len(facturas))
            col2.metric("Total Facturado", f"{total_facturado:.2f}€")
            col3.metric("Total Pagado", f"{total_pagado:.2f}€")
        else:
            st.info("No se encontraron facturas.")

    except Exception as e:
        st.error(f"Error: {str(e)}")

# TAB: Crear Factura
with tab_crear:
    st.header("Generar Nueva Factura")

    try:
        # Obtener citas completadas sin factura
        todas_citas = servicio_cita.listar_citas()
        citas_completadas = [c for c in todas_citas if c.estado == EstadoCita.COMPLETADA]

        # Filtrar las que ya tienen factura
        todas_facturas = servicio_factura.listar_facturas()
        citas_con_factura = {f.cita_id for f in todas_facturas}
        citas_sin_factura = [c for c in citas_completadas if c.id not in citas_con_factura]

        if not citas_sin_factura:
            st.warning("⚠️ No hay citas completadas sin factura.")
        else:
            opciones_citas = {}
            for c in citas_sin_factura:
                cliente = servicio_cliente.obtener_cliente(c.cliente_id)
                mascota = servicio_mascota.obtener_mascota(c.mascota_id)
                opciones_citas[
                    f"ID:{c.id} - {c.fecha_hora.strftime('%Y-%m-%d')} - "
                    f"{cliente.nombre} / {mascota.nombre}"
                ] = c.id

            cita_seleccionada = st.selectbox("Seleccione una cita", options=list(opciones_citas.keys()))

            if cita_seleccionada:
                cita_id = opciones_citas[cita_seleccionada]
                cita = servicio_cita.obtener_cita(cita_id)

                st.info(f"**Cita:** {cita.fecha_hora.strftime('%Y-%m-%d %H:%M')}\n\n**Diagnóstico:** {cita.diagnostico}")

                st.subheader("Líneas de Factura")

                # Gestionar líneas dinámicamente
                if 'lineas_factura' not in st.session_state:
                    st.session_state.lineas_factura = [
                        {"concepto": "Consulta veterinaria", "cantidad": 1, "precio": 50.0, "iva": 21.0}
                    ]

                for idx, linea in enumerate(st.session_state.lineas_factura):
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

                    with col1:
                        linea['concepto'] = st.text_input(f"Concepto", value=linea['concepto'], key=f"concepto_{idx}")
                    with col2:
                        linea['cantidad'] = st.number_input("Cant.", min_value=1, value=linea['cantidad'], key=f"cant_{idx}")
                    with col3:
                        linea['precio'] = st.number_input("Precio", min_value=0.0, value=linea['precio'], key=f"precio_{idx}")
                    with col4:
                        linea['iva'] = st.number_input("IVA%", min_value=0.0, max_value=100.0, value=linea['iva'], key=f"iva_{idx}")
                    with col5:
                        subtotal = linea['cantidad'] * linea['precio']
                        st.metric("Subtotal", f"{subtotal:.2f}€")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("➕ Añadir Línea"):
                        st.session_state.lineas_factura.append(
                            {"concepto": "", "cantidad": 1, "precio": 0.0, "iva": 21.0}
                        )
                        st.rerun()

                with col2:
                    if len(st.session_state.lineas_factura) > 1 and st.button("➖ Eliminar Última"):
                        st.session_state.lineas_factura.pop()
                        st.rerun()

                observaciones = st.text_area("Observaciones")

                # Calcular totales
                subtotal_total = sum(l['cantidad'] * l['precio'] for l in st.session_state.lineas_factura)
                iva_total = sum(l['cantidad'] * l['precio'] * l['iva'] / 100 for l in st.session_state.lineas_factura)
                total = subtotal_total + iva_total

                col1, col2, col3 = st.columns(3)
                col1.metric("Subtotal", f"{subtotal_total:.2f}€")
                col2.metric("IVA", f"{iva_total:.2f}€")
                col3.metric("TOTAL", f"{total:.2f}€")

                if st.button("✅ Generar Factura", type="primary", use_container_width=True):
                    try:
                        lineas_data = [
                            {
                                'concepto': l['concepto'],
                                'cantidad': l['cantidad'],
                                'precio_unitario': l['precio'],
                                'iva_porcentaje': l['iva']
                            }
                            for l in st.session_state.lineas_factura
                            if l['concepto'].strip()
                        ]

                        if not lineas_data:
                            st.error("Debe agregar al menos una línea válida")
                        else:
                            factura = servicio_factura.crear_factura_desde_cita(
                                cita_id=cita_id,
                                lineas_data=lineas_data,
                                observaciones=observaciones.strip() if observaciones else None
                            )
                            st.success(f"✅ Factura {factura.numero_factura} generada correctamente")
                            st.session_state.lineas_factura = [
                                {"concepto": "Consulta veterinaria", "cantidad": 1, "precio": 50.0, "iva": 21.0}
                            ]
                            st.balloons()
                            st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    except Exception as e:
        st.error(f"Error: {str(e)}")

# TAB: Gestionar Pago
with tab_gestionar:
    st.header("Gestionar Pagos")

    try:
        facturas_pendientes = [f for f in servicio_factura.listar_facturas() if not f.pagada]

        if not facturas_pendientes:
            st.info("✅ No hay facturas pendientes de pago.")
        else:
            opciones_facturas = {}
            for f in facturas_pendientes:
                cliente = servicio_cliente.obtener_cliente(f.cliente_id)
                opciones_facturas[
                    f"{f.numero_factura} - {cliente.nombre} - {float(f.calcular_total()):.2f}€"
                ] = f.id

            factura_seleccionada = st.selectbox("Seleccione una factura", options=list(opciones_facturas.keys()))

            if factura_seleccionada:
                factura_id = opciones_facturas[factura_seleccionada]
                factura = servicio_factura.obtener_factura(factura_id)

                if factura:
                    st.info(f"""
                    **Número:** {factura.numero_factura}
                    **Total:** {float(factura.calcular_total()):.2f}€
                    **Fecha Emisión:** {factura.fecha_emision.strftime('%Y-%m-%d')}
                    """)

                    with st.form("form_pagar"):
                        metodo_pago = st.selectbox("Método de pago", ["Efectivo", "Tarjeta", "Transferencia"])
                        fecha_pago = st.date_input("Fecha de pago", value=datetime.now().date())

                        if st.form_submit_button("💳 Registrar Pago", use_container_width=True):
                            try:
                                fecha_pago_dt = datetime.combine(fecha_pago, datetime.min.time())
                                servicio_factura.marcar_como_pagada(factura_id, metodo_pago, fecha_pago_dt)
                                st.success("✅ Pago registrado correctamente")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")

    except Exception as e:
        st.error(f"Error: {str(e)}")
