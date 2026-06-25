import pandas as pd


def construir_contexto_ia(pregunta, df_analisis):
    """
    Construye el contexto que utilizará el asistente
    con base en ANALISIS_COMENTARIOS.
    """

    pregunta = pregunta.lower()

    if df_analisis.empty:
        return pd.DataFrame()

    # Buscar coincidencias por tema
    if "TEMA" in df_analisis.columns:
        contexto = df_analisis[
            df_analisis["TEMA"].astype(str).str.lower().str.contains(
                pregunta,
                na=False
            )
        ]

        if not contexto.empty:
            return contexto

    # Buscar coincidencias por sinónimo
    if "SINONIMO" in df_analisis.columns:
        contexto = df_analisis[
            df_analisis["SINONIMO"].astype(str).str.lower().str.contains(
                pregunta,
                na=False
            )
        ]

        if not contexto.empty:
            return contexto

    # Buscar en comentario
    if "COMENTARIO" in df_analisis.columns:
        contexto = df_analisis[
            df_analisis["COMENTARIO"].astype(str).str.lower().str.contains(
                pregunta,
                na=False
            )
        ]

        if not contexto.empty:
            return contexto

    return pd.DataFrame()


def generar_respuesta_simulada(pregunta, contexto):

    pregunta = pregunta.lower()

    if contexto.empty:
        return (
            "No encontré información relacionada con esa consulta "
            "utilizando los filtros actuales."
        )

    total = len(contexto)

    if "fortaleza" in pregunta:
        return (
            f"Se localizaron {total} registros relacionados. "
            "Predominan comentarios positivos. "
            "Posteriormente esta respuesta será generada por IA."
        )

    if "oportunidad" in pregunta:
        return (
            f"Se localizaron {total} registros relacionados. "
            "Existen áreas susceptibles de mejora. "
            "Posteriormente esta respuesta será generada por IA."
        )

    if "problema" in pregunta:
        return (
            f"Se encontraron {total} evidencias relacionadas con el tema consultado."
        )

    if "comentario" in pregunta:
        return (
            f"Se localizaron {total} comentarios asociados al tema."
        )

    if "resumen" in pregunta:
        return (
            f"Se encontraron {total} registros para elaborar el resumen."
        )

    return (
        f"Se encontraron {total} registros relacionados con la consulta."
    )
