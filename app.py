import streamlit as st

st.set_page_config(
    page_title="Dirección Académica | UDL",
    page_icon="🎓",
    layout="wide"
)

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

# ---------- PLACEHOLDERS ----------
else:
    st.markdown(f"## {menu}")
    st.info("Este módulo se integrará en las siguientes fases del Ecosistema Digital.")
