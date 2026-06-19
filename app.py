import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Dirección Académica | UDL",
    page_icon="🎓",
    layout="wide"
)

SHEET_ID = "1e-Zr56_EzGqNOdl1msgidEtpL_DZhJrzMKwwiyz6Bnk"


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


def formatear_promedio(valor):
    if pd.isna(valor):
        return "0.0"
    return f"{valor:.1f}"


def render_card(valor, titulo, subtitulo=""):
    st.markdown(f"""
    <div class="metric-card">
        <h2>{valor}</h2>
        <p>{titulo}</p>
        <span>{subtitulo}</span>
    </div>
    """, unsafe_allow_html=True)


def filtrar_dataframe(df, anio, modalidad, carrera):
    df_filtrado = df.copy()

    if "ANIO_ESCOLAR" in df_filtrado.columns and anio != "Todas":
        df_filtrado = df_filtrado[df_filtrado["ANIO_ESCOLAR"].astype(str) == anio]

    if "MODALIDAD" in df_filtrado.columns and modalidad != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["MODALIDAD"].astype(str).str.upper() == modalidad.upper()
        ]

    if "SERVICIO_PROCEDENCIA" in df_filtrado.columns and carrera != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["SERVICIO_PROCEDENCIA"].astype(str) == carrera
        ]

    return df_filtrado


st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1380px;
    }

    .hero {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #e5e7eb;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.04);
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

    .section-header {
        background: #ffffff;
        padding: 1rem 1.3rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 6px 16px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
    }

    .section-header h1 {
        margin: 0;
        color: #1f2937;
        font-size: 2rem;
    }

    .section-header p {
        margin-top: 0.25rem;
        color: #6b7280;
        font-size: 0.95rem;
    }

    .metric-card {
        background: white;
        padding: 0.85rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        text-align: center;
        box-shadow: 0 8px 18px rgba(0,0,0,0.05);
        min-height: 90px;
    }

    .metric-card h2 {
        color: #111827;
        margin: 0;
        font-size: 1.6rem;
    }

    .metric-card p {
        color: #4b5563;
        margin: 0.15rem 0 0 0;
        font-size: 0.86rem;
        font-weight: 600;
    }

    .metric-card span {
        color: #9ca3af;
        font-size: 0.74rem;
    }

    .module-card {
        background: white;
        padding: 1.2rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        margin-bottom: 0.8rem;
        box-shadow: 0 6px 16px rgba(0,0,0,0.04);
    }

    .ai-box {
        background: #ffffff;
        padding: 1rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 18px rgba(0,0,0,0.05);
        min-height: 340px;
    }

    .ai-box h4 {
        margin-top: 0;
        color: #111827;
    }

    .ai-box p {
        color: #4b5563;
        font-size: 0.92rem;
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
        font-weight: 600;
    }
</style>
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


elif menu == "📊 Encuesta de Calidad":

    st.markdown("""
    <div class="section-header">
        <h1>📊 Encuesta de Calidad</h1>
        <p>Resultados cuantitativos, comparativo por carrera y comentarios abiertos.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        df_kpis = cargar_kpis()
        df_comentarios = cargar_comentarios()
    except Exception as e:
        st.exception(e)
        df_kpis = pd.DataFrame()
        df_comentarios = pd.DataFrame()

    if not df_kpis.empty:
        for col in [
            "ANIO_ESCOLAR",
            "MODALIDAD",
            "SERVICIO_PROCEDENCIA",
            "NIVEL_ANALISIS",
            "SECCION",
            "ESTATUS",
            "SEMAFORO"
        ]:
            if col in df_kpis.columns:
                df_kpis[col] = df_kpis[col].astype(str).str.strip()

        if "PROMEDIO" in df_kpis.columns:
            df_kpis["PROMEDIO"] = pd.to_numeric(df_kpis["PROMEDIO"], errors="coerce")

        if not df_comentarios.empty:
            for col in [
                "ANIO_ESCOLAR",
                "MODALIDAD",
                "SERVICIO_PROCEDENCIA",
                "SECCION",
                "SUBSECCION",
                "PREGUNTA_LIMPIA",
                "COMENTARIO"
            ]:
                if col in df_comentarios.columns:
                    df_comentarios[col] = df_comentarios[col].astype(str).str.strip()

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

        focos_rojos = 0
        if "ESTATUS" in df_filtrado.columns:
            focos_rojos = len(df_filtrado[df_filtrado["ESTATUS"] == "FOCO_ROJO"])

        if not df_comentarios.empty:
            df_com_filtrado = df_comentarios.copy()

            if "ANIO_ESCOLAR" in df_com_filtrado.columns and anio != "Todas":
                df_com_filtrado = df_com_filtrado[df_com_filtrado["ANIO_ESCOLAR"].astype(str) == anio]

            if "MODALIDAD" in df_com_filtrado.columns and modalidad != "Todas":
                df_com_filtrado = df_com_filtrado[
                    df_com_filtrado["MODALIDAD"].astype(str).str.upper() == modalidad.upper()
                ]

            if "SERVICIO_PROCEDENCIA" in df_com_filtrado.columns and carrera != "Todas":
                df_com_filtrado = df_com_filtrado[
                    df_com_filtrado["SERVICIO_PROCEDENCIA"].astype(str) == carrera
                ]

            total_comentarios = len(df_com_filtrado)
        else:
            df_com_filtrado = pd.DataFrame()
            total_comentarios = 0

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            render_card(formatear_promedio(promedio_general), "Promedio general", "Escala 0 a 100")

        with k2:
            render_card(formatear_promedio(recomendacion), "Recomendación", "Promedio de recomendación")

        with k3:
            render_card(f"{focos_rojos:,}", "Focos rojos", "Indicadores críticos")

        with k4:
            render_card(f"{total_comentarios:,}", "Comentarios", "Respuestas abiertas")

        with st.expander("ℹ️ ¿Cómo se calculan los resultados?"):
            st.markdown("""
            ### Escala de evaluación

            Las respuestas se convierten a una escala de **0 a 100**.

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

            ### Semáforo

            | Rango | Estatus |
            |---|---|
            | 90 a 100 | 🟢 Sobresaliente |
            | Igual o superior a la meta | 🔵 Adecuado |
            | 70 a debajo de la meta | 🟡 Atención |
            | Menor a 70 | 🔴 Foco rojo |
            """)

        tab_resumen, tab_comparativo, tab_secciones, tab_focos, tab_comentarios = st.tabs([
            "📌 Resumen",
            "🏆 Comparativo por carrera",
            "📊 Secciones",
            "⚠️ Focos rojos",
            "🗣️ Comentarios"
        ])

        with tab_resumen:
            col_grafica, col_ia = st.columns([1.45, 0.85])

            with col_grafica:
                st.markdown("### Promedio por sección")

                if not df_resumen.empty and "SECCION" in df_resumen.columns:
                    df_seccion_resumen = (
                        df_resumen
                        .groupby("SECCION", as_index=False)
                        .agg(PROMEDIO=("PROMEDIO", "mean"))
                        .sort_values("PROMEDIO", ascending=True)
                    )

                    fig_resumen = px.bar(
                        df_seccion_resumen,
                        x="PROMEDIO",
                        y="SECCION",
                        orientation="h",
                        text="PROMEDIO",
                        title=None
                    )

                    fig_resumen.update_traces(texttemplate="%{text:.1f}", textposition="outside")
                    fig_resumen.update_layout(
                        xaxis_range=[0, 100],
                        xaxis_title="Promedio",
                        yaxis_title="",
                        height=470,
                        margin=dict(l=20, r=30, t=20, b=20)
                    )

                    st.plotly_chart(fig_resumen, use_container_width=True)

            with col_ia:
                st.markdown("""
                <div class="ai-box">
                    <h4>🤖 Asistente IA</h4>
                    <p>Consulta información de la encuesta, solicita reportes ejecutivos o pregunta por comentarios específicos.</p>
                    <p><strong>Ejemplos:</strong></p>
                    <p>• Dame el reporte de Psicología</p>
                    <p>• ¿Qué dicen sobre baños?</p>
                    <p>• ¿Cuáles son los focos rojos?</p>
                </div>
                """, unsafe_allow_html=True)

                pregunta_ia_resumen = st.text_input(
                    "Pregunta al asistente",
                    placeholder="Ej. Dame el reporte ejecutivo de Psicología"
                )

                if pregunta_ia_resumen:
                    st.info("Aquí se conectará el asistente IA con KPIS y COMENTARIOS_ABIERTOS.")

        with tab_comparativo:
            st.markdown("### Ranking comparativo por carrera")

            df_comp_base = df_filtrado.copy()

            if "SERVICIO_PROCEDENCIA" in df_comp_base.columns:
                df_comp_base = df_comp_base[
                    (df_comp_base["NIVEL_ANALISIS"] == "SECCION_CARRERA") &
                    (df_comp_base["SERVICIO_PROCEDENCIA"] != "TODOS")
                ]

                if not df_comp_base.empty:
                    df_ranking = (
                        df_comp_base
                        .groupby("SERVICIO_PROCEDENCIA", as_index=False)
                        .agg(PROMEDIO=("PROMEDIO", "mean"))
                        .sort_values("PROMEDIO", ascending=True)
                    )

                    fig_rank = px.bar(
                        df_ranking,
                        x="PROMEDIO",
                        y="SERVICIO_PROCEDENCIA",
                        orientation="h",
                        text="PROMEDIO",
                        title="Promedio general por carrera / programa"
                    )

                    fig_rank.update_traces(texttemplate="%{text:.1f}", textposition="outside")
                    fig_rank.update_layout(
                        xaxis_range=[0, 100],
                        xaxis_title="Promedio",
                        yaxis_title="",
                        height=max(520, len(df_ranking) * 26),
                        margin=dict(l=20, r=30, t=50, b=20)
                    )

                    st.plotly_chart(fig_rank, use_container_width=True)

                    st.dataframe(
                        df_ranking.sort_values("PROMEDIO", ascending=False),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No hay datos comparativos con los filtros seleccionados.")
            else:
                st.info("No se encontró la columna SERVICIO_PROCEDENCIA.")

        with tab_secciones:
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

                st.dataframe(
                    df_seccion,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No hay datos de sección con los filtros seleccionados.")

        with tab_focos:
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
                        "PREGUNTA_LIMPIA",
                        "PROMEDIO",
                        "META",
                        "ESTATUS",
                        "SEMAFORO"
                    ] if col in df_alertas.columns
                ]

                if not df_alertas.empty:
                    st.dataframe(
                        df_alertas[columnas_alertas].head(30),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.success("No se detectan focos rojos con los filtros seleccionados.")
            else:
                st.info("No hay detalle disponible con los filtros seleccionados.")

        with tab_comentarios:
            st.markdown("### Comentarios abiertos")

            if not df_com_filtrado.empty:
                colb1, colb2 = st.columns([1, 1])

                with colb1:
                    palabra = st.text_input(
                        "Buscar en comentarios",
                        placeholder="Ej. baños, wifi, profesores, SEAC, biblioteca"
                    )

                with colb2:
                    if "SECCION" in df_com_filtrado.columns:
                        secciones_com = ["Todas"] + sorted([
                            x for x in df_com_filtrado["SECCION"].dropna().astype(str).unique().tolist()
                            if x not in ["", "nan"]
                        ])
                    else:
                        secciones_com = ["Todas"]

                    seccion_com = st.selectbox("Filtrar por sección", secciones_com)

                comentarios_vista = df_com_filtrado.copy()

                if seccion_com != "Todas" and "SECCION" in comentarios_vista.columns:
                    comentarios_vista = comentarios_vista[
                        comentarios_vista["SECCION"].astype(str) == seccion_com
                    ]

                if palabra and "COMENTARIO" in comentarios_vista.columns:
                    comentarios_vista = comentarios_vista[
                        comentarios_vista["COMENTARIO"]
                        .astype(str)
                        .str.contains(palabra, case=False, na=False)
                    ]

                columnas_comentarios = [
                    col for col in [
                        "SERVICIO_PROCEDENCIA",
                        "SECCION",
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

    else:
        st.warning("No se pudieron cargar datos de KPIS.")


else:
    st.markdown(f"## {menu}")
    st.info("Este módulo se integrará en las siguientes fases del Ecosistema Digital.")
