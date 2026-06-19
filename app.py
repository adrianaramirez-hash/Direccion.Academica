import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials

# ---------- CONFIGURACIÓN ----------
st.set_page_config(
    page_title="Dirección Académica | UDL",
    page_icon="🎓",
    layout="wide"
)

SHEET_ID = "1e-Zr56_EzGqNOdl1msgidEtpL_DZhJrzMKwwiyz6Bnk"

# ---------- CONEXIÓN GOOGLE ----------
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


@st.cache_data(ttl=300)
def cargar_hoja(nombre_hoja):
    gc = conectar_google()
    archivo = gc.open_by_key(SHEET_ID)
    hoja = archivo.worksheet(nombre_hoja)
    datos = hoja.get_all_records()
    return pd.DataFrame(datos)


@st.cache_data(ttl=300)
def cargar_kpis():
    return cargar_hoja("KPIS")


@st.cache_data(ttl=300)
def cargar_comentarios():
    return cargar_hoja("COMENTARIOS_ABIERTOS")


# ---------- UTILIDADES ----------
def limpiar_texto(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip()


def formatear_promedio(valor):
    if pd.isna(valor):
        return "0.0"
    return f"{valor:.1f}"


def render_card(valor, titulo):
    st.markdown(f"""
    <div class="metric-card">
        <h2>{valor}</h2>
        <p>{titulo}</p>
    </div>
    """, unsafe_allow_html=True)


def filtrar_dataframe(df, anio, modalidad, carrera):
    df_filtrado = df.copy()

    if "ANIO_ESCOLAR" in df_filtrado.columns and anio != "Todas":
        df_filtrado = df_filtrado[df_filtrado["ANIO_ESCOLAR"].astype(str) == anio]

    if "MODALIDAD" in df_filtrado.columns and modalidad != "Todas":
        df_filtrado = df_filtrado[df_filtrado["MODALIDAD"].astype(str).str.upper() == modalidad.upper()]

    if "SERVICIO_PROCEDENCIA" in df_filtrado.columns and carrera != "Todas":
        df_filtrado = df_filtrado[df_filtrado["SERVICIO_PROCEDENCIA"].astype(str) == carrera]

    return df_filtrado


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
        min-height: 120px;
    }

    .metric-card h2 {
        color: #1f2937;
        margin-bottom: 0.1rem;
        font-size: 2.2rem;
    }

    .metric-card p {
        color: #6b7280;
        margin: 0;
        font-size: 1rem;
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
        conectar_google()
        st.success("✅ Conexión con Google Sheets exitosa")
    except Exception as e:
        st.exception(e)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_card("31", "Programas académicos")

    with col2:
        render_card("400+", "Docentes")

    with col3:
        render_card("9", "Módulos proyectados")

    with col4:
        render_card("1", "Módulo activo")

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

    with st.expander("ℹ️ ¿Cómo se calculan los resultados?"):
        st.markdown("""
        ### Escala de evaluación

        Las respuestas de la encuesta se convierten a una escala de **0 a 100** para facilitar la lectura institucional:

        | Respuesta | Valor |
        |---|---:|
        | Excelente / Totalmente satisfecho / Muy satisfecho | 100 |
        | Bueno / Satisfecho / De acuerdo | 80 |
        | Regular / Neutral / Ni uno ni otro | 60 |
        | Malo / Poco satisfecho / En desacuerdo | 40 |
        | Muy malo / Nada satisfecho / Totalmente en desacuerdo | 20 |
        | Sí | 100 |
        | No | 0 |

        Las respuestas **“No lo utilizo”** y **“No sé”** no se incluyen en el promedio.

        ### Metas institucionales

        | Sección | Meta |
        |---|---:|
        | Satisfacción general | 90 |
        | Recomendación | 90 |
        | Servicios | 85 |
        | Académico | 85 |
        | Dirección / Coordinación | 85 |
        | Instalaciones | 80 |
        | Ambiente escolar | 85 |
        | Virtual: aprendizaje, SEAC, soporte y comunicación | 85 |

        ### Semáforo de interpretación

        | Rango | Estatus |
        |---|---|
        | 90 a 100 | 🟢 Sobresaliente |
        | Igual o superior a la meta | 🔵 Adecuado |
        | 70 a debajo de la meta | 🟡 Atención |
        | Menor a 70 | 🔴 Foco rojo |

        Los promedios se calculan a partir de las respuestas válidas registradas en **BASE_GENERAL** y resumidas en la hoja **KPIS**.
        """)
    try:
        df_kpis = cargar_kpis()
        df_comentarios = cargar_comentarios()

        st.success(f"✅ KPIS cargados: {len(df_kpis)} registros")

        with st.expander("Ver muestra de KPIS"):
            st.dataframe(df_kpis.head(10), use_container_width=True)

    except Exception as e:
        st.exception(e)
        df_kpis = pd.DataFrame()
        df_comentarios = pd.DataFrame()

    st.markdown("---")

    if not df_kpis.empty:
        # Normalización básica
        for col in ["ANIO_ESCOLAR", "MODALIDAD", "SERVICIO_PROCEDENCIA", "NIVEL_ANALISIS", "SECCION", "ESTATUS", "SEMAFORO"]:
            if col in df_kpis.columns:
                df_kpis[col] = df_kpis[col].astype(str).str.strip()

        if "PROMEDIO" in df_kpis.columns:
            df_kpis["PROMEDIO"] = pd.to_numeric(df_kpis["PROMEDIO"], errors="coerce")

        # Filtros dinámicos
        anios = ["Todas"] + sorted(df_kpis["ANIO_ESCOLAR"].dropna().astype(str).unique().tolist())
        modalidades = ["Todas"] + sorted([
            x for x in df_kpis["MODALIDAD"].dropna().astype(str).unique().tolist()
            if x not in ["TODOS", ""]
        ])
        carreras = ["Todas"] + sorted([
            x for x in df_kpis["SERVICIO_PROCEDENCIA"].dropna().astype(str).unique().tolist()
            if x not in ["TODOS", ""]
        ])

        colf1, colf2, colf3 = st.columns(3)

        with colf1:
            anio = st.selectbox("Año escolar", anios, index=1 if len(anios) > 1 else 0)

        with colf2:
            modalidad = st.selectbox("Modalidad", modalidades)

        with colf3:
            carrera = st.selectbox("Carrera / Programa", carreras)

        df_filtrado = filtrar_dataframe(df_kpis, anio, modalidad, carrera)

        # Capa de resumen según el filtro
        if carrera != "Todas":
            df_resumen = df_filtrado[df_filtrado["NIVEL_ANALISIS"].isin(["SECCION_CARRERA"])]
            df_detalle = df_filtrado[df_filtrado["NIVEL_ANALISIS"].isin(["CARRERA"])]
        else:
            df_resumen = df_filtrado[df_filtrado["NIVEL_ANALISIS"].isin(["SECCION_INSTITUCIONAL"])]
            df_detalle = df_filtrado[df_filtrado["NIVEL_ANALISIS"].isin(["INSTITUCIONAL"])]

        if df_resumen.empty:
            df_resumen = df_filtrado.copy()

        promedio_general = df_resumen["PROMEDIO"].mean() if "PROMEDIO" in df_resumen.columns else 0

        df_recomendacion = df_resumen[df_resumen["SECCION"] == "RECOMENDACION"]
        recomendacion = df_recomendacion["PROMEDIO"].mean() if not df_recomendacion.empty else 0

        total_kpis = len(df_filtrado)

        if "ESTATUS" in df_filtrado.columns:
            focos_rojos = len(df_filtrado[df_filtrado["ESTATUS"] == "FOCO_ROJO"])
        else:
            focos_rojos = 0

        if not df_comentarios.empty:
            df_com_filtrado = df_comentarios.copy()

            if "ANIO_ESCOLAR" in df_com_filtrado.columns and anio != "Todas":
                df_com_filtrado = df_com_filtrado[df_com_filtrado["ANIO_ESCOLAR"].astype(str) == anio]

            if "MODALIDAD" in df_com_filtrado.columns and modalidad != "Todas":
                df_com_filtrado = df_com_filtrado[df_com_filtrado["MODALIDAD"].astype(str).str.upper() == modalidad.upper()]

            if "SERVICIO_PROCEDENCIA" in df_com_filtrado.columns and carrera != "Todas":
                df_com_filtrado = df_com_filtrado[df_com_filtrado["SERVICIO_PROCEDENCIA"].astype(str) == carrera]

            total_comentarios = len(df_com_filtrado)
        else:
            total_comentarios = 0

        st.markdown("### Resumen ejecutivo")

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            render_card(formatear_promedio(promedio_general), "Promedio general")

        with k2:
            render_card(formatear_promedio(recomendacion), "Recomendación")

        with k3:
            render_card(f"{total_kpis:,}", "Indicadores filtrados")

        with k4:
            render_card(f"{focos_rojos:,}", "Focos rojos")

        st.markdown("### Resultados por sección")

        if not df_resumen.empty and "SECCION" in df_resumen.columns:
            df_seccion = (
                df_resumen
                .groupby("SECCION", as_index=False)
                .agg(
                    PROMEDIO=("PROMEDIO", "mean"),
                    RESPUESTAS_VALIDAS=("RESPUESTAS_VALIDAS", "sum")
                )
                .sort_values("PROMEDIO", ascending=False)
            )

            fig = px.bar(
                df_seccion,
                x="SECCION",
                y="PROMEDIO",
                text="PROMEDIO",
                title="Promedio por sección"
            )
            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            fig.update_layout(yaxis_range=[0, 100], xaxis_title="", yaxis_title="Promedio")

            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                df_seccion,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("### Focos rojos y áreas de atención")

        if not df_detalle.empty:
            df_alertas = df_detalle.copy()

            if "PROMEDIO" in df_alertas.columns:
                df_alertas = df_alertas.sort_values("PROMEDIO", ascending=True)

            if "ESTATUS" in df_alertas.columns:
                df_alertas = df_alertas[df_alertas["ESTATUS"].isin(["FOCO_ROJO", "ATENCION"])]

            columnas_alertas = [
                col for col in [
                    "SERVICIO_PROCEDENCIA",
                    "SECCION",
                    "SUBSECCION",
                    "PREGUNTA_LIMPIA",
                    "PROMEDIO",
                    "META",
                    "ESTATUS",
                    "SEMAFORO"
                ] if col in df_alertas.columns
            ]

            if not df_alertas.empty:
                st.dataframe(
                    df_alertas[columnas_alertas].head(25),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("No se detectan focos rojos con los filtros seleccionados.")
        st.markdown("### 🗣️ Comentarios abiertos")

        if not df_comentarios.empty:
            comentarios_vista = df_com_filtrado.copy()

            palabra = st.text_input(
                "Buscar en comentarios",
                placeholder="Ej. baños, wifi, profesores, SEAC, biblioteca"
            )

            if palabra:
                comentarios_vista = comentarios_vista[
                    comentarios_vista["COMENTARIO"]
                    .astype(str)
                    .str.contains(palabra, case=False, na=False)
                ]

            columnas_comentarios = [
                col for col in [
                    "SERVICIO_PROCEDENCIA",
                    "SECCION",
                    "SUBSECCION",
                    "PREGUNTA_LIMPIA",
                    "COMENTARIO"
                ] if col in comentarios_vista.columns
            ]

            st.caption(f"Comentarios encontrados: {len(comentarios_vista)}")

            st.dataframe(
                comentarios_vista[columnas_comentarios].head(100),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay comentarios abiertos disponibles con los filtros seleccionados.")

        st.markdown("### Asistente IA de Encuesta")

        pregunta_ia = st.text_input(
            "Pregunta al asistente sobre la encuesta",
            placeholder="Ej. Dame el reporte ejecutivo de Psicología"
        )

        if pregunta_ia:
            st.info("Aquí se conectará el asistente IA para responder con base en KPIS y COMENTARIOS_ABIERTOS.")

    else:
        st.warning("No se pudieron cargar datos de KPIS.")


# ---------- PLACEHOLDERS ----------
else:
    st.markdown(f"## {menu}")
    st.info("Este módulo se integrará en las siguientes fases del Ecosistema Digital.")
