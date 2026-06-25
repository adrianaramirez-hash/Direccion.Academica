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


@st.cache_data(ttl=300)
def cargar_analisis_comentarios():
    return cargar_hoja("ANALISIS_COMENTARIOS")


def formatear_promedio(valor):
    if pd.isna(valor):
        return "0.0"
    return f"{valor:.1f}"


def render_card(valor, titulo, subtitulo=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{valor}</div>
        <div class="metric-title">{titulo}</div>
        <div class="metric-subtitle">{subtitulo}</div>
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


def construir_contexto_ia(
    anio,
    modalidad,
    carrera,
    promedio_general,
    recomendacion,
    focos_rojos,
    total_comentarios,
    df_alertas,
    df_fortalezas,
    df_analisis_filtrado
):
    alertas_txt = "Sin focos rojos relevantes."
    if not df_alertas.empty:
        alertas_txt = "\n".join([
            f"- {row.get('SECCION', '')} | {row.get('PREGUNTA_LIMPIA', '')}: {row.get('PROMEDIO', '')}"
            for _, row in df_alertas.head(5).iterrows()
        ])

    fortalezas_txt = "Sin fortalezas identificadas."
    if not df_fortalezas.empty:
        fortalezas_txt = "\n".join([
            f"- {row.get('SECCION', '')} | {row.get('PREGUNTA_LIMPIA', '')}: {row.get('PROMEDIO', '')}"
            for _, row in df_fortalezas.head(5).iterrows()
        ])

    analisis_txt = "Sin análisis de comentarios disponible."
    if not df_analisis_filtrado.empty:
        temp = df_analisis_filtrado.copy()
        if "TOTAL_COMENTARIOS" in temp.columns:
            temp["TOTAL_COMENTARIOS"] = pd.to_numeric(temp["TOTAL_COMENTARIOS"], errors="coerce")
            temp = temp.sort_values("TOTAL_COMENTARIOS", ascending=False)

        analisis_txt = "\n".join([
            f"- {row.get('TEMA', '')} / {row.get('SUBTEMA', '')}: {row.get('TOTAL_COMENTARIOS', '')} comentarios. Prioridad: {row.get('PRIORIDAD', '')}. Evidencia: {row.get('EVIDENCIA_1', '')}"
            for _, row in temp.head(8).iterrows()
        ])

    return f"""
Contexto de análisis:
Año escolar: {anio}
Modalidad: {modalidad}
Carrera / Programa: {carrera}

Indicadores:
Promedio general: {formatear_promedio(promedio_general)}
Recomendación: {formatear_promedio(recomendacion)}
Focos rojos: {focos_rojos}
Comentarios abiertos filtrados: {total_comentarios}

Principales focos rojos o áreas de atención:
{alertas_txt}

Principales fortalezas:
{fortalezas_txt}

Análisis temático de comentarios:
{analisis_txt}
"""


def generar_respuesta_simulada(pregunta, contexto, df_analisis_filtrado):
    pregunta_lower = pregunta.lower()

    tema_detectado = None
    if not df_analisis_filtrado.empty and "TEMA" in df_analisis_filtrado.columns:
        for tema in df_analisis_filtrado["TEMA"].dropna().astype(str).unique():
            if tema.lower() in pregunta_lower:
                tema_detectado = tema
                break

    if tema_detectado:
        df_tema = df_analisis_filtrado[df_analisis_filtrado["TEMA"] == tema_detectado].copy()
        if "TOTAL_COMENTARIOS" in df_tema.columns:
            df_tema["TOTAL_COMENTARIOS"] = pd.to_numeric(df_tema["TOTAL_COMENTARIOS"], errors="coerce")
            df_tema = df_tema.sort_values("TOTAL_COMENTARIOS", ascending=False)

        evidencias = []
        for _, row in df_tema.head(5).iterrows():
            evidencias.append(
                f"- **{row.get('SUBTEMA', '')}**: {row.get('TOTAL_COMENTARIOS', '')} comentarios. "
                f"Prioridad: {row.get('PRIORIDAD', '')}. "
                f"Evidencia: {row.get('EVIDENCIA_1', '')}"
            )

        return f"""
### 🧠 Resumen sobre {tema_detectado}

Se encontraron hallazgos relacionados con **{tema_detectado}** dentro del análisis de comentarios.

{chr(10).join(evidencias)}

**Lectura ejecutiva:**  
Este tema debe revisarse considerando la frecuencia de comentarios, la prioridad asignada y su relación con los indicadores cuantitativos de la encuesta.

**Siguiente acción sugerida:**  
Validar los comentarios con el área responsable y convertirlos en acciones específicas con fecha de seguimiento.
"""

    if "plan" in pregunta_lower or "30" in pregunta_lower or "60" in pregunta_lower or "90" in pregunta_lower:
        return f"""
### 📑 Plan de acción preliminar 30-60-90 días

**Contexto utilizado:**

{contexto}

**30 días**
- Revisar los focos rojos con responsables de área.
- Validar los temas con mayor número de comentarios.
- Definir responsables y evidencias de seguimiento.

**60 días**
- Implementar acciones correctivas.
- Documentar avances.
- Comunicar mejoras a estudiantes.

**90 días**
- Medir impacto.
- Presentar reporte ejecutivo.
- Definir acciones permanentes.
"""

    if "foco" in pregunta_lower or "problema" in pregunta_lower or "riesgo" in pregunta_lower or "oportunidad" in pregunta_lower:
        return f"""
### ⚠️ Áreas de oportunidad principales

**Contexto utilizado:**

{contexto}

**Lectura ejecutiva:**  
Las áreas de oportunidad deben priorizarse por bajo promedio, distancia contra meta y recurrencia en comentarios abiertos.

**Recomendación:**  
Atender primero los hallazgos con prioridad **ALTA**, después los de prioridad **MEDIA**.
"""

    if "fortaleza" in pregunta_lower:
        return f"""
### 📈 Fortalezas principales

**Contexto utilizado:**

{contexto}

**Lectura ejecutiva:**  
Las fortalezas deben documentarse como buenas prácticas y replicarse en programas o servicios con menor desempeño.
"""

    return f"""
### 📋 Resumen ejecutivo preliminar

**Contexto utilizado:**

{contexto}

**Conclusión ejecutiva:**  
El análisis combina KPIs cuantitativos con hallazgos temáticos de comentarios. La prioridad debe centrarse en temas con mayor volumen de comentarios, focos rojos y evidencias recurrentes.
"""


st.markdown("""
<style>
    .main { background-color: #f7f9fc; }
    .block-container { padding-top: 1.3rem; padding-bottom: 2rem; max-width: 1400px; }
    .hero {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 2.4rem; border-radius: 22px; border: 1px solid #e5e7eb;
        text-align: center; margin-bottom: 1.5rem; box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
    }
    .hero h1 { font-size: 3rem; margin-bottom: 0.25rem; color: #111827; font-weight: 800; letter-spacing: -0.03em; }
    .hero h3 { font-size: 1.25rem; color: #4b5563; font-weight: 500; margin-bottom: 0.3rem; }
    .hero p { color: #6b7280; font-size: 1.05rem; margin: 0; }
    .section-header {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.1rem 1.4rem; border-radius: 18px; border: 1px solid #e5e7eb;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06); margin-bottom: 1rem;
    }
    .section-header h1 { margin: 0; color: #111827; font-size: 2.15rem; font-weight: 800; letter-spacing: -0.02em; }
    .section-header p { margin-top: 0.25rem; color: #4b5563; font-size: 1rem; }
    .metric-card {
        background: #ffffff; padding: 1rem 0.8rem; border-radius: 16px; border: 1px solid #e5e7eb;
        text-align: center; box-shadow: 0 8px 18px rgba(15, 23, 42, 0.07);
        min-height: 92px; display: flex; flex-direction: column; justify-content: center;
    }
    .metric-value { color: #111827; font-size: 2rem; font-weight: 800; line-height: 1.1; }
    .metric-title { color: #1f2937; font-size: 0.95rem; font-weight: 700; margin-top: 0.25rem; }
    .metric-subtitle { color: #6b7280; font-size: 0.78rem; margin-top: 0.1rem; font-weight: 500; }
    .module-card {
        background: white; padding: 1.2rem; border-radius: 16px; border: 1px solid #e5e7eb;
        margin-bottom: 0.8rem; box-shadow: 0 6px 16px rgba(0,0,0,0.04);
    }
    .status-active { color: #15803d; font-weight: 700; }
    .status-soon { color: #92400e; font-weight: 700; }
    div[data-testid="stTabs"] button { font-size: 0.95rem; font-weight: 700; }
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
        render_card("31", "Programas académicos", "Licenciaturas y posgrados")
    with col2:
        render_card("400+", "Docentes", "Comunidad académica")
    with col3:
        render_card("9", "Módulos proyectados", "Ecosistema institucional")
    with col4:
        render_card("1", "Módulo activo", "Encuesta de Calidad")


elif menu == "📊 Encuesta de Calidad":
    st.markdown("""
    <div class="section-header">
        <h1>📊 Encuesta de Calidad</h1>
        <p>Resultados cuantitativos, comparativo por carrera, análisis por sección y comentarios abiertos.</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        df_kpis = cargar_kpis()
        df_comentarios = cargar_comentarios()
        df_analisis = cargar_analisis_comentarios()
    except Exception as e:
        st.exception(e)
        df_kpis = pd.DataFrame()
        df_comentarios = pd.DataFrame()
        df_analisis = pd.DataFrame()

    if not df_kpis.empty:
        for df in [df_kpis, df_comentarios, df_analisis]:
            if not df.empty:
                for col in df.columns:
                    if df[col].dtype == "object":
                        df[col] = df[col].astype(str).str.strip()

        if "PROMEDIO" in df_kpis.columns:
            df_kpis["PROMEDIO"] = pd.to_numeric(df_kpis["PROMEDIO"], errors="coerce")

        if "TOTAL_COMENTARIOS" in df_analisis.columns:
            df_analisis["TOTAL_COMENTARIOS"] = pd.to_numeric(df_analisis["TOTAL_COMENTARIOS"], errors="coerce")

        anios = ["Todas"] + sorted(df_kpis["ANIO_ESCOLAR"].dropna().astype(str).unique().tolist())
        modalidades = ["Todas"] + sorted([x for x in df_kpis["MODALIDAD"].dropna().astype(str).unique().tolist() if x not in ["TODOS", ""]])
        carreras = ["Todas"] + sorted([x for x in df_kpis["SERVICIO_PROCEDENCIA"].dropna().astype(str).unique().tolist() if x not in ["TODOS", ""]])

        colf1, colf2, colf3 = st.columns(3)
        with colf1:
            anio = st.selectbox("Año escolar", anios, index=1 if len(anios) > 1 else 0)
        with colf2:
            modalidad = st.selectbox("Modalidad", modalidades)
        with colf3:
            carrera = st.selectbox("Carrera / Programa", carreras)

        df_filtrado = filtrar_dataframe(df_kpis, anio, modalidad, carrera)
        df_com_filtrado = filtrar_dataframe(df_comentarios, anio, modalidad, carrera) if not df_comentarios.empty else pd.DataFrame()
        df_analisis_filtrado = filtrar_dataframe(df_analisis, anio, modalidad, carrera) if not df_analisis.empty else pd.DataFrame()

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
        focos_rojos = len(df_filtrado[df_filtrado["ESTATUS"] == "FOCO_ROJO"]) if "ESTATUS" in df_filtrado.columns else 0
        total_comentarios = len(df_com_filtrado)

        df_alertas_ia = df_detalle.copy()
        if not df_alertas_ia.empty and "PROMEDIO" in df_alertas_ia.columns:
            df_alertas_ia = df_alertas_ia.sort_values("PROMEDIO", ascending=True)
        if "ESTATUS" in df_alertas_ia.columns:
            df_alertas_ia = df_alertas_ia[df_alertas_ia["ESTATUS"].isin(["FOCO_ROJO", "ATENCION"])]

        df_fortalezas_ia = df_detalle.copy()
        if not df_fortalezas_ia.empty and "PROMEDIO" in df_fortalezas_ia.columns:
            df_fortalezas_ia = df_fortalezas_ia.sort_values("PROMEDIO", ascending=False).head(5)

        contexto_ia = construir_contexto_ia(
            anio, modalidad, carrera, promedio_general, recomendacion, focos_rojos,
            total_comentarios, df_alertas_ia, df_fortalezas_ia, df_analisis_filtrado
        )

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_card(formatear_promedio(promedio_general), "Promedio general", "Escala 0 a 100")
        with k2:
            render_card(formatear_promedio(recomendacion), "Recomendación", "Promedio de recomendación")
        with k3:
            render_card(f"{focos_rojos:,}", "Focos rojos", "Indicadores críticos")
        with k4:
            render_card(f"{total_comentarios:,}", "Comentarios", "Respuestas abiertas")

        tab_resumen, tab_comparativo, tab_secciones, tab_focos, tab_comentarios, tab_analisis = st.tabs([
            "📌 Resumen",
            "🏆 Comparativo por carrera",
            "📊 Secciones",
            "⚠️ Focos rojos",
            "🗣️ Comentarios",
            "🧠 Análisis de comentarios"
        ])

        with tab_resumen:
            col_grafica, col_ia = st.columns([1.45, 0.85])

            with col_grafica:
                st.markdown("### Promedio por sección")
                if not df_resumen.empty and "SECCION" in df_resumen.columns:
                    df_seccion_resumen = (
                        df_resumen.groupby("SECCION", as_index=False)
                        .agg(PROMEDIO=("PROMEDIO", "mean"))
                        .sort_values("PROMEDIO", ascending=True)
                    )
                    fig_resumen = px.bar(
                        df_seccion_resumen,
                        x="PROMEDIO",
                        y="SECCION",
                        orientation="h",
                        text="PROMEDIO"
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
                st.markdown("### 🤖 Asistente IA")
                st.caption("Versión preliminar: ahora usa KPIs + ANALISIS_COMENTARIOS.")

                b1, b2 = st.columns(2)
                b3, b4 = st.columns(2)

                if b1.button("📋 Resumen ejecutivo"):
                    st.session_state["pregunta_ia"] = "Dame un resumen ejecutivo"
                if b2.button("⚠️ Problemas"):
                    st.session_state["pregunta_ia"] = "Cuáles son las áreas de oportunidad"
                if b3.button("📈 Fortalezas"):
                    st.session_state["pregunta_ia"] = "Cuáles son las fortalezas"
                if b4.button("📑 Plan 30-60-90"):
                    st.session_state["pregunta_ia"] = "Genera un plan de acción 30-60-90 días"

                pregunta_ia = st.text_input(
                    "Pregunta al asistente",
                    value=st.session_state.get("pregunta_ia", ""),
                    placeholder="Ej. ¿Qué dicen de Sanitarios?"
                )

                if pregunta_ia:
                    respuesta = generar_respuesta_simulada(pregunta_ia, contexto_ia, df_analisis_filtrado)
                    st.markdown(respuesta)

                with st.expander("Ver contexto usado por la IA"):
                    st.text(contexto_ia)

        with tab_comparativo:
            st.markdown("### Ranking comparativo por carrera")
            df_comp_base = df_filtrado.copy()

            if "SERVICIO_PROCEDENCIA" in df_comp_base.columns:
                df_comp_base = df_comp_base[
                    (df_comp_base["NIVEL_ANALISIS"] == "SECCION_CARRERA") &
                    (df_comp_base["SERVICIO_PROCEDENCIA"] != "TODOS")
                ]

                secciones_disponibles = ["Todas"] + sorted([
                    x for x in df_comp_base["SECCION"].dropna().astype(str).unique().tolist()
                    if x not in ["", "nan"]
                ])

                seccion_ranking = st.selectbox("Selecciona la sección a comparar", secciones_disponibles)
                df_comp_vista = df_comp_base.copy()

                if seccion_ranking != "Todas":
                    df_comp_vista = df_comp_vista[df_comp_vista["SECCION"] == seccion_ranking]

                if not df_comp_vista.empty:
                    df_ranking = (
                        df_comp_vista.groupby("SERVICIO_PROCEDENCIA", as_index=False)
                        .agg(PROMEDIO=("PROMEDIO", "mean"))
                        .sort_values("PROMEDIO", ascending=True)
                    )
                    fig_rank = px.bar(
                        df_ranking,
                        x="PROMEDIO",
                        y="SERVICIO_PROCEDENCIA",
                        orientation="h",
                        text="PROMEDIO",
                        title=f"Comparativo por carrera - {seccion_ranking}"
                    )
                    fig_rank.update_traces(texttemplate="%{text:.1f}", textposition="outside")
                    fig_rank.update_layout(
                        xaxis_range=[0, 100],
                        xaxis_title="Promedio",
                        yaxis_title="",
                        height=max(520, len(df_ranking) * 28),
                        margin=dict(l=20, r=30, t=50, b=20)
                    )
                    st.plotly_chart(fig_rank, use_container_width=True)
                    st.dataframe(df_ranking.sort_values("PROMEDIO", ascending=False), use_container_width=True, hide_index=True)
                else:
                    st.info("No hay datos comparativos con los filtros seleccionados.")

        with tab_secciones:
            st.markdown("### Resultados por sección")
            if not df_resumen.empty and "SECCION" in df_resumen.columns:
                df_seccion = (
                    df_resumen.groupby("SECCION", as_index=False)
                    .agg(PROMEDIO=("PROMEDIO", "mean"), RESPUESTAS_VALIDAS=("RESPUESTAS_VALIDAS", "sum"))
                    .sort_values("PROMEDIO", ascending=False)
                )
                st.dataframe(df_seccion, use_container_width=True, hide_index=True)
            else:
                st.info("No hay datos de sección con los filtros seleccionados.")

        with tab_focos:
            st.markdown("### Focos rojos y áreas de atención")
            columnas_alertas = [
                col for col in [
                    "SERVICIO_PROCEDENCIA", "SECCION", "PREGUNTA_LIMPIA",
                    "PROMEDIO", "META", "ESTATUS", "SEMAFORO"
                ] if col in df_alertas_ia.columns
            ]
            if not df_alertas_ia.empty:
                st.dataframe(df_alertas_ia[columnas_alertas].head(30), use_container_width=True, hide_index=True)
            else:
                st.success("No se detectan focos rojos con los filtros seleccionados.")

        with tab_comentarios:
            st.markdown("### Comentarios abiertos")
            if not df_com_filtrado.empty:
                colb1, colb2 = st.columns([1, 1])
                with colb1:
                    palabra = st.text_input("Buscar en comentarios", placeholder="Ej. baños, wifi, profesores, SEAC")
                with colb2:
                    secciones_com = ["Todas"] + sorted(df_com_filtrado["SECCION"].dropna().astype(str).unique().tolist()) if "SECCION" in df_com_filtrado.columns else ["Todas"]
                    seccion_com = st.selectbox("Filtrar por sección", secciones_com)

                comentarios_vista = df_com_filtrado.copy()

                if seccion_com != "Todas" and "SECCION" in comentarios_vista.columns:
                    comentarios_vista = comentarios_vista[comentarios_vista["SECCION"].astype(str) == seccion_com]

                if palabra and "COMENTARIO" in comentarios_vista.columns:
                    comentarios_vista = comentarios_vista[
                        comentarios_vista["COMENTARIO"].astype(str).str.contains(palabra, case=False, na=False)
                    ]

                columnas_comentarios = [
                    col for col in ["SERVICIO_PROCEDENCIA", "SECCION", "PREGUNTA_LIMPIA", "COMENTARIO"]
                    if col in comentarios_vista.columns
                ]

                st.caption(f"Comentarios encontrados: {len(comentarios_vista)}")
                st.dataframe(comentarios_vista[columnas_comentarios].head(100), use_container_width=True, hide_index=True)
            else:
                st.info("No hay comentarios abiertos disponibles con los filtros seleccionados.")

        with tab_analisis:
            st.markdown("### 🧠 Análisis temático de comentarios")

            if not df_analisis_filtrado.empty:
                col_a, col_b = st.columns([1, 1])

                with col_a:
                    temas = ["Todos"] + sorted(df_analisis_filtrado["TEMA"].dropna().astype(str).unique().tolist()) if "TEMA" in df_analisis_filtrado.columns else ["Todos"]
                    tema_sel = st.selectbox("Tema", temas)

                with col_b:
                    prioridades = ["Todas"] + sorted(df_analisis_filtrado["PRIORIDAD"].dropna().astype(str).unique().tolist()) if "PRIORIDAD" in df_analisis_filtrado.columns else ["Todas"]
                    prioridad_sel = st.selectbox("Prioridad", prioridades)

                analisis_vista = df_analisis_filtrado.copy()

                if tema_sel != "Todos" and "TEMA" in analisis_vista.columns:
                    analisis_vista = analisis_vista[analisis_vista["TEMA"] == tema_sel]

                if prioridad_sel != "Todas" and "PRIORIDAD" in analisis_vista.columns:
                    analisis_vista = analisis_vista[analisis_vista["PRIORIDAD"] == prioridad_sel]

                if "TOTAL_COMENTARIOS" in analisis_vista.columns:
                    analisis_vista = analisis_vista.sort_values("TOTAL_COMENTARIOS", ascending=False)

                columnas_analisis = [
                    col for col in [
                        "SERVICIO_PROCEDENCIA", "SECCION", "TEMA", "SUBTEMA",
                        "TOTAL_COMENTARIOS", "PRIORIDAD", "EVIDENCIA_1", "EVIDENCIA_2", "EVIDENCIA_3"
                    ] if col in analisis_vista.columns
                ]

                st.caption(f"Hallazgos encontrados: {len(analisis_vista)}")
                st.dataframe(analisis_vista[columnas_analisis].head(100), use_container_width=True, hide_index=True)

                if "TEMA" in analisis_vista.columns and "TOTAL_COMENTARIOS" in analisis_vista.columns:
                    resumen_temas = (
                        analisis_vista.groupby("TEMA", as_index=False)
                        .agg(TOTAL_COMENTARIOS=("TOTAL_COMENTARIOS", "sum"))
                        .sort_values("TOTAL_COMENTARIOS", ascending=True)
                    )
                    fig_temas = px.bar(
                        resumen_temas,
                        x="TOTAL_COMENTARIOS",
                        y="TEMA",
                        orientation="h",
                        text="TOTAL_COMENTARIOS",
                        title="Temas más mencionados"
                    )
                    fig_temas.update_traces(textposition="outside")
                    fig_temas.update_layout(xaxis_title="Comentarios", yaxis_title="", height=450)
                    st.plotly_chart(fig_temas, use_container_width=True)

            else:
                st.info("No hay análisis de comentarios disponible con los filtros seleccionados.")

    else:
        st.warning("No se pudieron cargar datos de KPIS.")


else:
    st.markdown(f"## {menu}")
    st.info("Este módulo se integrará en las siguientes fases del Ecosistema Digital.")
