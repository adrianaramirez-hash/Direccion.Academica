import re
import pandas as pd

from encuesta_calidad.intenciones import Intencion, detectar_intencion


SINONIMOS_TEMAS = {
    "Sanitarios": [
        "sanitario", "sanitarios", "baño", "baños", "wc", "papel",
        "papel higiénico", "jabón", "agua", "limpieza", "sucio",
        "sucios", "olor", "higiene", "mantenimiento"
    ],
    "Wifi": [
        "wifi", "internet", "red", "conexión", "conectividad",
        "señal", "lento", "velocidad", "falla", "fallas", "desconecta"
    ],
    "SEAC": [
        "seac", "plataforma", "sistema", "portal", "app", "aplicación",
        "calificaciones", "horario", "inscripción", "reinscripción",
        "trámite", "trámites", "aulas virtuales"
    ],
    "Docentes": [
        "profesor", "profesores", "docente", "docentes", "maestro",
        "maestros", "asesor", "asesores", "clase", "clases",
        "enseñanza", "explicación", "puntualidad"
    ],
    "Instalaciones": [
        "instalaciones", "salón", "salones", "aula", "aulas",
        "mobiliario", "ventilación", "iluminación", "clima",
        "aire acondicionado"
    ],
    "Biblioteca": ["biblioteca", "libros", "préstamo", "acervo"],
    "Cafetería": ["cafetería", "cafeteria", "comida", "alimentos", "menú", "precios"],
    "Seguridad": ["seguridad", "vigilancia", "guardia", "acceso", "entrada"],
    "Atención Administrativa": [
        "servicios escolares", "administrativo", "administración",
        "caja", "pagos", "becas", "admisiones", "cobranzas",
        "titulación", "trámite", "atención"
    ],
    "Ambiente Escolar": [
        "ambiente", "convivencia", "respeto", "compañerismo",
        "compañeros", "conflicto", "problema con compañero"
    ],
}


def normalizar_texto(texto):
    texto = str(texto or "").lower().strip()
    reemplazos = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ü": "u", "ñ": "n"
    }

    for original, limpio in reemplazos.items():
        texto = texto.replace(original, limpio)

    texto = re.sub(r"\s+", " ", texto)
    return texto


def detectar_tema(pregunta, df_analisis):
    pregunta_limpia = normalizar_texto(pregunta)

    for tema, sinonimos in SINONIMOS_TEMAS.items():
        for sinonimo in sinonimos:
            if normalizar_texto(sinonimo) in pregunta_limpia:
                return tema

    if not df_analisis.empty and "TEMA" in df_analisis.columns:
        for tema in df_analisis["TEMA"].dropna().astype(str).unique():
            if normalizar_texto(tema) in pregunta_limpia:
                return tema

    return None


def construir_contexto_ia(pregunta, df_analisis):
    if df_analisis.empty:
        return pd.DataFrame()

    contexto = df_analisis.copy()
    tema = detectar_tema(pregunta, contexto)

    if tema and "TEMA" in contexto.columns:
        contexto = contexto[
            contexto["TEMA"].astype(str).str.lower() == tema.lower()
        ]

    if "TOTAL_COMENTARIOS" in contexto.columns:
        contexto["TOTAL_COMENTARIOS"] = pd.to_numeric(
            contexto["TOTAL_COMENTARIOS"],
            errors="coerce"
        )
        contexto = contexto.sort_values("TOTAL_COMENTARIOS", ascending=False)

    return contexto


def _tabla_hallazgos(contexto, limite=6):
    if contexto.empty:
        return "No se encontraron hallazgos con los filtros actuales."

    lineas = []

    for _, row in contexto.head(limite).iterrows():
        tema = row.get("TEMA", "")
        subtema = row.get("SUBTEMA", "")
        total = row.get("TOTAL_COMENTARIOS", "")
        prioridad = row.get("PRIORIDAD", "")
        evidencia = row.get("EVIDENCIA_1", "")

        lineas.append(
            f"- **{tema} / {subtema}**: {total} comentarios. "
            f"Prioridad: **{prioridad}**. Evidencia: _{evidencia}_"
        )

    return "\n".join(lineas)


def generar_respuesta_simulada(pregunta, contexto):
    pregunta_limpia = normalizar_texto(pregunta)
    intencion = detectar_intencion(pregunta)

    if contexto.empty:
        return """
### Sin información suficiente

No encontré hallazgos relacionados con esa consulta usando los filtros actuales.

Puedes intentar con otro tema, por ejemplo: **sanitarios**, **wifi**, **SEAC**, **docentes**, **cafetería**, **biblioteca** o **servicios administrativos**.
"""

    total_hallazgos = len(contexto)

    total_comentarios = 0
    if "TOTAL_COMENTARIOS" in contexto.columns:
        total_comentarios = pd.to_numeric(
            contexto["TOTAL_COMENTARIOS"],
            errors="coerce"
        ).fillna(0).sum()

    tema_principal = ""
    if "TEMA" in contexto.columns and not contexto["TEMA"].dropna().empty:
        tema_principal = contexto["TEMA"].dropna().astype(str).iloc[0]

    hallazgos = _tabla_hallazgos(contexto)

    if intencion == Intencion.FORTALEZAS:
        return f"""
### 📈 Fortalezas detectadas

Con los filtros actuales se identificaron **{total_hallazgos} hallazgos temáticos** asociados a comentarios y evidencias.

{hallazgos}

**Lectura ejecutiva:**  
Las fortalezas deben utilizarse como evidencia de buenas prácticas. Conviene revisar qué áreas, servicios o programas concentran comentarios favorables para replicar esas prácticas en otros servicios.

**Siguiente acción sugerida:**  
Documentar qué proceso, responsable o práctica explica estos resultados y convertirlo en estándar institucional.
"""

    if intencion == Intencion.AREAS_OPORTUNIDAD:
        return f"""
### ⚠️ Áreas de oportunidad

Se encontraron **{total_hallazgos} hallazgos** que agrupan aproximadamente **{int(total_comentarios)} comentarios clasificados**.

{hallazgos}

**Lectura ejecutiva:**  
Las áreas de oportunidad deben priorizarse por frecuencia de comentarios, prioridad asignada y relación con indicadores cuantitativos bajos.

**Recomendación inicial:**  
Atender primero los hallazgos con prioridad **ALTA**, asignar responsable, fecha de seguimiento y evidencia esperada.
"""

    if intencion == Intencion.PLAN_ACCION:
        return f"""
### 📑 Plan de acción 30-60-90 días

**Base del análisis:** {total_hallazgos} hallazgos y aproximadamente **{int(total_comentarios)} comentarios clasificados**.

{hallazgos}

**30 días**
- Validar los hallazgos con el área responsable.
- Revisar evidencias y comentarios asociados.
- Definir responsables, fechas y acciones inmediatas.

**60 días**
- Implementar acciones correctivas en temas de prioridad alta.
- Documentar avances y evidencias.
- Comunicar mejoras o ajustes a estudiantes.

**90 días**
- Medir si los indicadores relacionados mejoraron.
- Comparar contra metas institucionales.
- Integrar resultados en seguimiento de Dirección Académica.
"""

    if intencion in [
        Intencion.COMENTARIOS_TEMA,
        Intencion.RESUMEN_EJECUTIVO,
        Intencion.RECOMENDACIONES
    ]:
        titulo = f" sobre {tema_principal}" if tema_principal else ""
        return f"""
### 🗣️ Resumen de comentarios{titulo}

Se identificaron **{total_hallazgos} hallazgos** que agrupan aproximadamente **{int(total_comentarios)} comentarios clasificados**.

{hallazgos}

**Resumen ejecutivo:**  
Los comentarios muestran patrones recurrentes que permiten explicar la percepción estudiantil sobre este tema. La revisión debe centrarse en los subtemas con mayor volumen de comentarios y prioridad más alta.

**Acción sugerida:**  
Convertir los hallazgos más frecuentes en compromisos de mejora con responsable, fecha y evidencia.
"""

    return f"""
### 📋 Resumen ejecutivo

Con los filtros actuales se identificaron **{total_hallazgos} hallazgos temáticos** y aproximadamente **{int(total_comentarios)} comentarios clasificados**.

{hallazgos}

**Conclusión ejecutiva:**  
El análisis combina comentarios abiertos clasificados por tema con prioridades operativas. Esto permite pasar de una lectura general de comentarios a un diagnóstico accionable.

**Siguiente paso sugerido:**  
Revisar los temas de mayor frecuencia y prioridad para convertirlos en acciones de seguimiento institucional.
"""
