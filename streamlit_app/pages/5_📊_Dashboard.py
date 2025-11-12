"""
Dashboard con métricas y estadísticas de la clínica.
"""
import streamlit as st
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.infrastructure.database import get_db
from src.services.factura_service import FacturaService
from src.services.cita_service import CitaService
from src.services.cliente_service import ClienteService
from src.services.mascota_service import MascotaService
from src.domain.cita import EstadoCita

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard - Métricas de la Clínica")

db = next(get_db())
servicio_factura = FacturaService(db)
servicio_cita = CitaService(db)
servicio_cliente = ClienteService(db)
servicio_mascota = MascotaService(db)

# Filtros de fecha
col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.date_input("Desde", value=date.today() - timedelta(days=30))
with col2:
    fecha_fin = st.date_input("Hasta", value=date.today())

st.markdown("---")

try:
    # MÉTRICAS GENERALES
    st.header("📈 Métricas Generales")

    clientes = servicio_cliente.listar_clientes()
    mascotas = servicio_mascota.listar_todas_mascotas()
    todas_citas = servicio_cita.listar_citas()
    todas_facturas = servicio_factura.listar_facturas()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👥 Clientes Activos", len([c for c in clientes if c.activo]))

    with col2:
        st.metric("🐕 Mascotas Registradas", len([m for m in mascotas if m.activo]))

    with col3:
        citas_periodo = [
            c for c in todas_citas
            if fecha_inicio <= c.fecha_hora.date() <= fecha_fin
        ]
        st.metric("📅 Citas en Período", len(citas_periodo))

    with col4:
        ingresos = servicio_factura.calcular_ingresos_periodo(
            datetime.combine(fecha_inicio, datetime.min.time()),
            datetime.combine(fecha_fin, datetime.max.time())
        )
        st.metric("💰 Ingresos Período", f"{ingresos['total_facturado']:.2f}€")

    st.markdown("---")

    # INGRESOS Y FACTURACIÓN
    st.header("💰 Facturación")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Facturas Emitidas", ingresos['num_facturas'])

    with col2:
        st.metric("Facturas Pagadas", ingresos['num_pagadas'])

    with col3:
        st.metric("Total Pagado", f"{ingresos['total_pagado']:.2f}€")

    with col4:
        st.metric("Pendiente de Cobro", f"{ingresos['total_pendiente']:.2f}€")

    # Gráfico de ingresos por mes
    if todas_facturas:
        st.subheader("📊 Ingresos Mensuales")

        facturas_con_fecha = [(f.fecha_emision, float(f.calcular_total())) for f in todas_facturas]
        df_ingresos = pd.DataFrame(facturas_con_fecha, columns=['Fecha', 'Total'])
        df_ingresos['Mes'] = df_ingresos['Fecha'].dt.to_period('M').astype(str)

        ingresos_mensuales = df_ingresos.groupby('Mes')['Total'].sum().reset_index()

        fig_ingresos = px.bar(
            ingresos_mensuales,
            x='Mes',
            y='Total',
            title="Ingresos por Mes",
            labels={'Total': 'Ingresos (€)', 'Mes': 'Mes'}
        )
        st.plotly_chart(fig_ingresos, use_container_width=True)

    st.markdown("---")

    # CITAS
    st.header("📅 Estadísticas de Citas")

    # Estados de citas
    col1, col2 = st.columns(2)

    with col1:
        if todas_citas:
            estados_count = Counter([c.estado.value for c in todas_citas])

            fig_estados = go.Figure(data=[go.Pie(
                labels=list(estados_count.keys()),
                values=list(estados_count.values()),
                hole=.3
            )])
            fig_estados.update_layout(title="Distribución de Estados de Citas")
            st.plotly_chart(fig_estados, use_container_width=True)

    with col2:
        if citas_periodo:
            # Citas por veterinario
            veterinarios_count = Counter([c.veterinario_nombre for c in citas_periodo])

            df_vets = pd.DataFrame(
                list(veterinarios_count.items()),
                columns=['Veterinario', 'Citas']
            ).sort_values('Citas', ascending=False)

            fig_vets = px.bar(
                df_vets,
                x='Veterinario',
                y='Citas',
                title="Citas por Veterinario (Período Seleccionado)"
            )
            st.plotly_chart(fig_vets, use_container_width=True)

    # Citas por día
    if citas_periodo:
        st.subheader("📆 Citas por Día")

        citas_por_dia = Counter([c.fecha_hora.date() for c in citas_periodo])
        df_dias = pd.DataFrame(
            [(fecha, count) for fecha, count in sorted(citas_por_dia.items())],
            columns=['Fecha', 'Número de Citas']
        )

        fig_dias = px.line(
            df_dias,
            x='Fecha',
            y='Número de Citas',
            title="Evolución de Citas Diarias",
            markers=True
        )
        st.plotly_chart(fig_dias, use_container_width=True)

    st.markdown("---")

    # TOP CLIENTES
    st.header("🏆 Top Clientes")

    top_clientes = servicio_factura.obtener_top_clientes(limite=10)

    if top_clientes:
        datos_top = []
        for item in top_clientes:
            cliente = servicio_cliente.obtener_cliente(item['cliente_id'])
            if cliente:
                datos_top.append({
                    'Cliente': cliente.nombre,
                    'DNI': cliente.dni,
                    'Total Facturado': f"{item['total']:.2f}€"
                })

        df_top = pd.DataFrame(datos_top)
        st.dataframe(df_top, use_container_width=True, hide_index=True)

    st.markdown("---")

    # MASCOTAS
    st.header("🐾 Estadísticas de Mascotas")

    if mascotas:
        col1, col2 = st.columns(2)

        with col1:
            # Por especie
            especies_count = Counter([m.especie.value for m in mascotas])

            fig_especies = go.Figure(data=[go.Pie(
                labels=list(especies_count.keys()),
                values=list(especies_count.values())
            )])
            fig_especies.update_layout(title="Mascotas por Especie")
            st.plotly_chart(fig_especies, use_container_width=True)

        with col2:
            # Top razas
            razas_count = Counter([m.raza for m in mascotas])
            top_razas = razas_count.most_common(10)

            df_razas = pd.DataFrame(top_razas, columns=['Raza', 'Cantidad'])

            fig_razas = px.bar(
                df_razas,
                x='Raza',
                y='Cantidad',
                title="Top 10 Razas"
            )
            st.plotly_chart(fig_razas, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar métricas: {str(e)}")

# Footer
st.markdown("---")
st.info("💡 **Tip:** Ajuste el rango de fechas arriba para filtrar las métricas del período deseado.")
