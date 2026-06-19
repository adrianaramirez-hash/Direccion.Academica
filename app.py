import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Dirección Académica | UDL",
    page_icon="🎓",
    layout="wide"
)

def conectar_google():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account_json"],
        scopes=scope
    )

    return gspread.authorize(creds)

# ---------- ESTILOS ----------
st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }

    .hero {
        background: white;
        padding: 2rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        font-size: 2.4rem;
        margin-bottom: 0.2rem;
        color: #1f2937;
    }

    .hero h3 {
        font-size: 1.1rem;
        color: #6b7280;
        font-weight: 400;
    }

    .metric-card {
        background: white;
        padding: 1.3rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    .metric-card h2 {
        color: #1f2937;
        margin-bottom: 0.1rem;
    }

    .metric-card p {
        color: #6b7280;
        margin: 0;
    }

    .module-card {
        background: white;
        padding: 1.2rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        margin-bottom: 0.8rem;
    }

    .status-active {
        color: #15803d;
        font-weight: 700;
    }

    .status-soon {
        color: #92400e;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.image("udl_logo.png", use_container_width=True)
    st.markdown("### Dirección Académica")
    st.caption("Universidad de Londres")

    menu = st.radio(
        "Menú principal",
        [
            "🏠 Inicio",
            "📊 Encuesta de Calidad",
            "⭐ Evaluación Docente",
            "👁️ Observación de Clases",
            "🎓 CENEVAL",
            "📝 Exámenes Departamentales",
            "📚 Aulas Virtuales",
            "📈 Índice de Reprobación",
            "🎖️ Titulación",
            "🎓 Capacitaciones",
            "🤖 Asistente IA"
        ]
    )

# ---------- INICIO ----------
if menu == "🏠 Inicio":
    st.markdown("""
    <div class="hero">
        <h1>Dirección Académica</h1>
        <h3>Ecosistema Digital para la Gestión Académica</h3>
        <p>Universidad de Londres</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        gc = conectar_google()
        st.success("✅ Conexión con Google Sheets exitosa")
    except Exception as e:
        st.error(f"❌ Error de conexión con Google Sheets: {e}")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>31</h2>
            <p>Programas académicos</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>400+</h2>
            <p>Docentes</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2>9</h2>
            <p>Módulos proyectados</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="metric-card">
            <h2>1</h2>
            <p>Módulo activo</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## Estado de módulos")

    modules = [
        ("📊 Encuesta de Calidad", "Activo"),
        ("⭐ Evaluación Docente", "Próximamente"),
        ("👁️ Observación de Clases", "Próximamente"),
        ("🎓 CENEVAL", "Próximamente"),
        ("📝 Exámenes Departamentales", "Próximamente"),
        ("📚 Aulas Virtuales", "Próximamente"),
        ("📈 Índice de Reprobación", "Próximamente"),
        ("🎖️ Titulación", "Próximamente"),
        ("🎓 Capacitaciones", "Próximamente"),
    ]

    for module, status in modules:
        status_class = "status-active" if status == "Activo" else "status-soon"
        st.markdown(f"""
        <div class="module-card">
            <strong>{module}</strong><br>
            <span class="{status_class}">{status}</span>
        </div>
        """, unsafe_allow_html=True)

# ---------- ENCUESTA DE CALIDAD ----------
elif menu == "📊 Encuesta de Calidad":
    st.markdown("## 📊 Encuesta de Calidad")
    st.caption("Análisis institucional de satisfacción, servicios, experiencia académica y comentarios abiertos.")

    st.markdown("---")

    colf1, colf2, colf3 = st.columns(3)

    with colf1:
        anio = st.selectbox("Año escolar", ["2025-2026", "2026-2027"])

    with colf2:
        modalidad = st.selectbox("Modalidad", ["Todas", "Escolarizada", "Preparatoria", "Virtual"])

    with colf3:
        carrera = st.selectbox("Carrera / Programa", ["Todas", "Psicología", "Derecho", "Nutrición", "Tecnologías de la Información"])

    st.markdown("### Resumen ejecutivo")

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown("""
        <div class="metric-card">
            <h2>86.4</h2>
            <p>Promedio general</p>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown("""
        <div class="metric-card">
            <h2>92%</h2>
            <p>Recomendación</p>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown("""
        <div class="metric-card">
            <h2>1,904</h2>
            <p>Indicadores calculados</p>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown("""
        <div class="metric-card">
            <h2>9,924</h2>
            <p>Comentarios abiertos</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Resultados por sección")

    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        st.markdown("""
        <div class="module-card">
            <h4>Promedio por sección</h4>
            <p>Servicios: 84.2 🔵</p>
            <p>Académico: 89.1 🔵</p>
            <p>Instalaciones: 76.4 🟡</p>
            <p>Ambiente escolar: 88.5 🔵</p>
            <p>Dirección / Coordinación: 91.2 🟢</p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="module-card">
            <h4>Lectura ejecutiva</h4>
            <p>La encuesta muestra resultados favorables en dirección, ambiente escolar y área académica.</p>
            <p>Las principales áreas de atención se concentran en instalaciones, conectividad y algunos servicios administrativos.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Focos rojos preliminares")

    st.dataframe(
        {
            "Sección": ["Instalaciones", "Servicios", "Plataforma SEAC"],
            "Pregunta": ["Sanitarios", "Wifi para estudiantes", "SEAC trámites administrativos"],
            "Promedio": [68.2, 72.5, 74.1],
            "Estatus": ["FOCO_ROJO", "ATENCION", "ATENCION"]
        },
        use_container_width=True
    )

    st.markdown("### Asistente IA de Encuesta")

    pregunta_ia = st.text_input(
        "Pregunta al asistente sobre la encuesta",
        placeholder="Ej. Dame el reporte ejecutivo de Psicología"
    )

    if pregunta_ia:
        st.info("Aquí se conectará el asistente IA para responder con base en KPIS y COMENTARIOS_ABIERTOS.")

# ---------- PLACEHOLDERS ----------
else:
    st.markdown(f"## {menu}")
    st.info("Este módulo se integrará en las siguientes fases del Ecosistema Digital.")
