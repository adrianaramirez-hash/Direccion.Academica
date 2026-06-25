import streamlit as st
import pandas as pd
import plotly.express as px

from encuesta_calidad.data import (
    cargar_kpis,
    cargar_comentarios,
    cargar_analisis_comentarios,
    filtrar_dataframe
)

from encuesta_calidad.ia import (
    construir_contexto_ia,
    generar_respuesta_simulada
)


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


def normalizar_columnas(df):
    if df.empty:
        return df

    df = df.copy()

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    return df


def mostrar_encuesta_calidad():

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
        return

    df_kpis = normalizar_columnas(df_kpis)
    df_comentarios = normalizar_columnas(df_comentarios)
    df_analisis = normalizar_columnas(df_analisis)

    if df_kpis.empty:
        st.warning("No se pudieron cargar datos de KPIS.")
        return

    if "PROMEDIO" in df_kpis.columns:
        df_kpis["PROMEDIO"] = pd.to_numeric(df_kpis["PROMEDIO"], errors="coerce")

    if "TOTAL_COMENTARIOS" in df_analisis.columns:
        df_analisis["TOTAL_COMENTARIOS"] = pd.to_numeric(
            df_analisis["TOTAL_COMENTARIOS"],
            errors="coerce"
        )

    anios = ["Todas"] + sorted(
        df_kpis["ANIO_ESCOLAR"].dropna().astype(str).unique().tolist()
    )

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

    df_com_filtrado = (
        filtrar_dataframe(df_comentarios, anio, modalidad, carrera)
        if not df_comentarios.empty else pd.DataFrame()
    )

    df_analisis_filtrado = (
        filtrar_dataframe(df_analisis, anio, modalidad, carrera)
        if not df_analisis.empty else pd.DataFrame()
    )

    if carrera != "Todas":
        df_resumen = df_filtrado[df_filtrado["NIVEL_ANALISIS"].isin(["SECCION_CARRERA"])]
        df_detalle = df_filtrado[df_filtrado["NIVEL_ANALISIS"].isin(["CARRERA"])]
    else:
        df_resumen = df_filtrado[df_filtrado["NIVEL_ANALISIS"].isin(["SECCION_INSTITUCIONAL"])]
        df_detalle = df_filtrado[df_filtrado["NIVEL_ANALISIS"].isin(["INSTITUCIONAL"])]

    if df_resumen.empty:
        df_resumen = df_filtrado.copy()

    promedio_general = (
        df_resumen["PROMEDIO"].mean()
        if "PROMEDIO" in df_resumen.columns else 0
    )

    df_recomendacion = df_resumen[df_resumen["SECCION"] == "RECOMENDACION"]
    recomendacion = (
        df_recomendacion["PROMEDIO"].mean()
        if not df_recomendacion.empty else 0
    )

    focos_rojos = (
        len(df_filtrado[df_filtrado["ESTATUS"] == "FOCO_ROJO"])
        if "ESTATUS" in df_filtrado.columns else 0
    )

    total_comentarios = len(df_com_filtrado)

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
                    text="PROMEDIO"
                )

                fig_resumen.update_traces(
                    texttemplate="%{text:.1f}",
                    textposition="outside"
                )

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
            st.caption("Versión preliminar: usa ANALISIS_COMENTARIOS como base.")

            b1, b2 = st.columns(2)
            b3, b4 = st.columns(2)

            if b1.button("📋 Resumen ejecutivo"):
                st.session_state["pregunta_ia"] = "resumen"

            if b2.button("⚠️ Problemas"):
                st.session_state["pregunta_ia"] = "problema"

            if b3.button("📈 Fortalezas"):
                st.session_state["pregunta_ia"] = "fortaleza"

            if b4.button("📑 Plan 30-60-90"):
                st.session_state["pregunta_ia"] = "plan 30 60 90"

            pregunta_ia = st.text_input(
                "Pregunta al asistente",
                value=st.session_state.get("pregunta_ia", ""),
                placeholder="Ej. ¿Qué dicen de Sanitarios?"
            )

            if pregunta_ia:
                contexto = construir_contexto_ia(
                    pregunta_ia,
                    df_analisis_filtrado
                )

                respuesta = generar_respuesta_simulada(
                    pregunta_ia,
                    contexto
                )

                st.markdown(respuesta)

                with st.expander("Ver registros usados por la IA"):
                    st.dataframe(contexto, use_container_width=True)

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

            seccion_ranking = st.selectbox(
                "Selecciona la sección a comparar",
                secciones_disponibles
            )

            df_comp_vista = df_comp_base.copy()

            if seccion_ranking != "Todas":
                df_comp_vista = df_comp_vista[df_comp_vista["SECCION"] == seccion_ranking]

            if not df_comp_vista.empty:
                df_ranking = (
                    df_comp_vista
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
                    title=f"Comparativo por carrera - {seccion_ranking}"
                )

                fig_rank.update_traces(
                    texttemplate="%{text:.1f}",
                    textposition="outside"
                )

                fig_rank.update_layout(
                    xaxis_range=[0, 100],
                    xaxis_title="Promedio",
                    yaxis_title="",
                    height=max(520, len(df_ranking) * 28),
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

        df_alertas = df_detalle.copy()

        if not df_alertas.empty and "PROMEDIO" in df_alertas.columns:
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

    with tab_comentarios:
        st.markdown("### Comentarios abiertos")

        if not df_com_filtrado.empty:
            colb1, colb2 = st.columns([1, 1])

            with colb1:
                palabra = st.text_input(
                    "Buscar en comentarios",
                    placeholder="Ej. baños, wifi, profesores, SEAC"
                )

            with colb2:
                secciones_com = (
                    ["Todas"] + sorted(
                        df_com_filtrado["SECCION"].dropna().astype(str).unique().tolist()
                    )
                    if "SECCION" in df_com_filtrado.columns else ["Todas"]
                )

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

    with tab_analisis:
        st.markdown("### 🧠 Análisis temático de comentarios")

        if not df_analisis_filtrado.empty:
            col_a, col_b = st.columns([1, 1])

            with col_a:
                temas = ["Todos"] + sorted(
                    df_analisis_filtrado["TEMA"].dropna().astype(str).unique().tolist()
                ) if "TEMA" in df_analisis_filtrado.columns else ["Todos"]

                tema_sel = st.selectbox("Tema", temas)

            with col_b:
                prioridades = ["Todas"] + sorted(
                    df_analisis_filtrado["PRIORIDAD"].dropna().astype(str).unique().tolist()
                ) if "PRIORIDAD" in df_analisis_filtrado.columns else ["Todas"]

                prioridad_sel = st.selectbox("Prioridad", prioridades)

            analisis_vista = df_analisis_filtrado.copy()

            if tema_sel != "Todos" and "TEMA" in analisis_vista.columns:
                analisis_vista = analisis_vista[analisis_vista["TEMA"] == tema_sel]

            if prioridad_sel != "Todas" and "PRIORIDAD" in analisis_vista.columns:
                analisis_vista = analisis_vista[analisis_vista["PRIORIDAD"] == prioridad_sel]

            if "TOTAL_COMENTARIOS" in analisis_vista.columns:
                analisis_vista = analisis_vista.sort_values(
                    "TOTAL_COMENTARIOS",
                    ascending=False
                )

            columnas_analisis = [
                col for col in [
                    "SERVICIO_PROCEDENCIA",
                    "SECCION",
                    "TEMA",
                    "SUBTEMA",
                    "TOTAL_COMENTARIOS",
                    "PRIORIDAD",
                    "EVIDENCIA_1",
                    "EVIDENCIA_2",
                    "EVIDENCIA_3"
                ] if col in analisis_vista.columns
            ]

            st.caption(f"Hallazgos encontrados: {len(analisis_vista)}")

            st.dataframe(
                analisis_vista[columnas_analisis].head(100),
                use_container_width=True,
                hide_index=True
            )

            resumen_temas = (
                analisis_vista
                .groupby("TEMA", as_index=False)
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

            fig_temas.update_layout(
                xaxis_title="Comentarios",
                yaxis_title="",
                height=450
            )

            st.plotly_chart(fig_temas, use_container_width=True)

        else:
            st.info("No hay análisis de comentarios disponible con los filtros seleccionados.")
