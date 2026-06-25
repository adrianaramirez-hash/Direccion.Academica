import streamlit as st

from encuesta_calidad.data import conectar_google
from encuesta_calidad.ui import mostrar_encuesta_calidad


st.set_page_config(
    page_title="Dirección Académica | UDL",
    page_icon="🎓",
    layout="wide"
)


st.markdown("""
<style>
    .main { background-color: #f7f9fc; }

    .block-container {
        padding-top: 1.3rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .hero {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 2.4rem;
        border-radius: 22px;
        border: 1px solid #e5e7eb;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
    }

    .hero h1 {
        font-size: 3rem;
        margin-bottom: 0.25rem;
        color: #111827;
        font-weight: 800;
        letter-spacing: -0.03em;
    }

    .hero h3 {
        font-size: 1.25rem;
        color: #4b5563;
        font-weight: 500;
        margin-bottom: 0.3rem;
    }

    .hero p {
        color: #6b7280;
        font-size: 1.05rem;
        margin: 0;
    }

    .section-header {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.1rem 1.4rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }

    .section-header h1 {
        margin: 0;
        color: #111827;
        font-size: 2.15rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .section-header p {
        margin-top: 0.25rem;
        color: #4b5563;
        font-size: 1rem;
    }

    .metric-card {
        background: #ffffff;
        padding: 1rem 0.8rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        text-align: center;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.07);
        min-height: 92px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .metric-value {
        color: #111827;
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .metric-title {
        color: #1f2937;
        font-size: 0.95rem;
        font-weight: 700;
        margin-top: 0.25rem;
    }

    .metric-subtitle {
        color: #6b7280;
        font-size: 0.78rem;
        margin-top: 0.1rem;
        font-weight: 500;
    }

    .module-card {
        background: white;
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        margin-bottom: 0.8rem;
        box-shadow: 0 6px 16px rgba(0,0,0,0.04);
    }

    .status-active {
        color: #15803d;
        font-weight: 700;
    }

    .status-soon {
        color: #92400e;
        font-weight: 700;
    }

    div[data-testid="stTabs"] button {
        font-size: 0.95rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


def render_card(valor, titulo, subtitulo=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{valor}</div>
        <div class="metric-title">{titulo}</div>
        <div class="metric-subtitle">{subtitulo}</div>
    </div>
    """, unsafe_allow_html=True)


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


if menu == "🏠 Inicio":
    st.markdown("""
    <div class="hero">
        <h1>Dirección Académica</h1>
        <h3>Ecosistema Digital para la Gestión Académica</h3>
        <p>Universidad de Londres</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        conectar_google()
        st.success("✅ Conexión con Google Sheets exitosa")
    except Exception as e:
        st.exception(e)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_card("31", "Programas académicos", "Licenciaturas y posgrados")

    with col2:
        render_card("400+", "Docentes", "Comunidad académica")

    with col3:
        render_card("9", "Módulos proyectados", "Ecosistema institucional")

    with col4:
        render_card("1", "Módulo activo", "Encuesta de Calidad")


elif menu == "📊 Encuesta de Calidad":
    mostrar_encuesta_calidad()


else:
    st.markdown(f"## {menu}")
    st.info("Este módulo se integrará en las siguientes fases del Ecosistema Digital.")
