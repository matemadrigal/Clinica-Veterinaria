"""
Aplicación principal de Streamlit para la Clínica Veterinaria.
Punto de entrada de la interfaz web.
"""
import streamlit as st
from pathlib import Path
import sys

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.infrastructure.database import init_db
from src.utils.logger import setup_logger

# Configurar logger
logger = setup_logger()

# Configuración de la página
st.set_page_config(
    page_title="Clínica Veterinaria",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar base de datos
@st.cache_resource
def initialize_database():
    """Inicializa la base de datos (solo una vez)"""
    try:
        init_db()
        logger.info("Base de datos inicializada correctamente")
        return True
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        return False

# Inicializar
db_initialized = initialize_database()

# Página principal
st.title("🐾 Sistema de Gestión de Clínica Veterinaria")

if not db_initialized:
    st.error("Error al inicializar la base de datos. Por favor, contacte al administrador.")
    st.stop()

st.markdown("""
## Bienvenido al Sistema de Gestión

Este sistema permite gestionar de forma integral todos los aspectos de una clínica veterinaria:

### 📋 Funcionalidades Principales

- **👥 Gestión de Clientes**: Registro y administración de clientes
- **🐕 Gestión de Mascotas**: Control del historial de mascotas
- **📅 Agenda de Citas**: Programación y seguimiento de citas veterinarias
- **💰 Facturación**: Generación y gestión de facturas
- **📊 Dashboard**: Métricas y estadísticas de la clínica

### 🚀 Cómo usar

Utilice el menú lateral para navegar entre las diferentes secciones del sistema.

### 📖 Ayuda

Para obtener ayuda o reportar problemas, contacte con el administrador del sistema.
""")

# Información en el sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### Acerca de")
    st.info("""
    **Sistema de Clínica Veterinaria**

    Versión: 1.0.0

    Desarrollado con:
    - Python
    - Streamlit
    - SQLAlchemy
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        © 2025 Clínica Veterinaria - Sistema de Gestión
    </div>
    """,
    unsafe_allow_html=True
)
