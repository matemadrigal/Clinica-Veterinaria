# Sistema de Gestión de Clínica Veterinaria

Sistema completo de gestión para clínicas veterinarias desarrollado con Python, Streamlit y SQLAlchemy.

## Características Principales

### Módulos Funcionales

- **👥 Gestión de Clientes**: Registro completo de clientes con validación de DNI español, email y teléfono
- **🐕 Gestión de Mascotas**: Control de mascotas asociadas a clientes con historial médico
- **📅 Agenda de Citas**: Sistema de agendamiento con validación de solapes por veterinario
- **💰 Facturación**: Generación y gestión de facturas con líneas detalladas e IVA
- **📊 Dashboard**: Métricas y estadísticas interactivas con gráficos en tiempo real

### Arquitectura y Diseño

El proyecto sigue principios **SOLID** y está organizado en capas:

- **Capa de Dominio** (`src/domain/`): Entidades con lógica de negocio
- **Capa de Infraestructura** (`src/infrastructure/`): Repositorios y acceso a datos
- **Capa de Servicios** (`src/services/`): Lógica de negocio compleja
- **Capa de Presentación** (`streamlit_app/`): Interfaz web con Streamlit

### Tecnologías Utilizadas

- **Python 3.9+**
- **Streamlit**: Framework para interfaz web
- **SQLAlchemy**: ORM para base de datos
- **SQLite**: Base de datos (configurable a PostgreSQL)
- **Pandas**: Análisis de datos
- **Plotly**: Visualizaciones interactivas
- **Pytest**: Testing unitario y de integración

## Instalación y Configuración

### Requisitos Previos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/usuario/Clinica-Veterinaria-1.git
cd Clinica-Veterinaria-1
```

2. **Crear entorno virtual**

```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno (opcional)**

```bash
cp config/.env.example .env
# Editar .env según necesidades
```

5. **Ejecutar la aplicación**

```bash
streamlit run streamlit_app/app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## Estructura del Proyecto

```
Clinica-Veterinaria-1/
├── src/
│   ├── domain/              # Entidades del dominio
│   │   ├── cliente.py
│   │   ├── mascota.py
│   │   ├── cita.py
│   │   └── factura.py
│   ├── infrastructure/      # Repositorios y DB
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repositories.py
│   ├── services/           # Servicios de dominio
│   │   ├── cliente_service.py
│   │   ├── mascota_service.py
│   │   ├── cita_service.py
│   │   └── factura_service.py
│   └── utils/              # Utilidades
│       ├── validators.py
│       ├── logger.py
│       └── exceptions.py
├── streamlit_app/
│   ├── app.py             # Aplicación principal
│   └── pages/             # Páginas de Streamlit
│       ├── 1_👥_Clientes.py
│       ├── 2_🐕_Mascotas.py
│       ├── 3_📅_Citas.py
│       ├── 4_💰_Facturación.py
│       └── 5_📊_Dashboard.py
├── tests/
│   ├── unit/              # Tests unitarios
│   │   ├── test_cliente.py
│   │   ├── test_mascota.py
│   │   └── test_cita.py
│   └── integration/       # Tests de integración
├── config/
│   └── .env.example       # Ejemplo de configuración
├── requirements.txt       # Dependencias
└── README.md
```

## Uso del Sistema

### Módulo de Clientes

1. Acceder a la página "Clientes" desde el menú lateral
2. Registrar nuevos clientes con DNI, teléfono y email validados
3. Buscar, editar o dar de baja clientes existentes

### Módulo de Mascotas

1. Acceder a "Mascotas" en el menú
2. Seleccionar un cliente propietario
3. Registrar mascota con datos completos (especie, raza, fecha de nacimiento)
4. El sistema valida duplicados por nombre y fecha de nacimiento

### Módulo de Citas

1. Ir a "Citas" y seleccionar "Nueva Cita"
2. Elegir cliente y mascota
3. Seleccionar veterinario, fecha, hora y motivo
4. **El sistema previene automáticamente solapes de horario por veterinario**
5. Gestionar citas: iniciar, completar, reprogramar o cancelar

### Módulo de Facturación

1. Acceder a "Facturación"
2. Seleccionar una cita completada sin factura
3. Agregar líneas de factura (concepto, cantidad, precio, IVA)
4. El sistema calcula automáticamente los totales
5. Registrar pagos con método (Efectivo, Tarjeta, Transferencia)

### Dashboard

- Visualiza métricas en tiempo real
- Filtra por rango de fechas
- Analiza ingresos mensuales
- Revisa estadísticas de citas por veterinario
- Consulta top clientes por facturación
- Observa distribución de mascotas por especie

## Testing

Ejecutar tests unitarios:

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/unit/test_cliente.py
```

Los reportes de cobertura se generan en `htmlcov/index.html`

## Requisitos Funcionales Implementados

- [x] CRUD completo de Clientes con validaciones
- [x] CRUD completo de Mascotas con asociación a clientes
- [x] Gestión de Citas con prevención de solapes
- [x] Estados de citas (Programada, En Curso, Completada, Cancelada)
- [x] Facturación desde citas completadas
- [x] Cálculo automático de totales con IVA
- [x] Dashboard con métricas e KPIs
- [x] Gráficos interactivos de análisis

## Requisitos No Funcionales Implementados

- [x] Persistencia con SQLAlchemy y SQLite
- [x] Arquitectura en capas con separación de responsabilidades
- [x] Principios SOLID aplicados
- [x] Tests unitarios con >80% cobertura en dominio
- [x] Validación de entradas y sanitización
- [x] Manejo de excepciones y logging
- [x] Interfaz web responsiva con Streamlit

## Mejoras Futuras

- [ ] API REST con FastAPI
- [ ] Autenticación y autorización de usuarios
- [ ] Exportación de facturas a PDF
- [ ] Sistema de notificaciones por email/SMS
- [ ] Historial médico detallado por mascota
- [ ] Gestión de inventario de medicamentos
- [ ] Integración con sistemas de pago online
- [ ] App móvil para clientes
- [ ] Sistema de recordatorios de citas

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Metodología de Desarrollo

- **XP/Scrum**: Iteraciones cortas y entregas incrementales
- **TDD**: Test-Driven Development con ciclo Red-Green-Refactor
- **Clean Code**: Código limpio y mantenible
- **SOLID**: Principios de diseño orientado a objetos

## Licencia

Este proyecto fue desarrollado como parte de un trabajo académico para el curso de Programación II.

## Autor

**Mateo Madrigal**
Estudiante de Business Analytics

---

**Nota**: Este es un proyecto educativo desarrollado con fines académicos.