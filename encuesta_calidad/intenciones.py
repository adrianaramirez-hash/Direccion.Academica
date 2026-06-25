from enum import Enum


class Intencion(str, Enum):
    RESUMEN_EJECUTIVO = "RESUMEN_EJECUTIVO"
    AREAS_OPORTUNIDAD = "AREAS_OPORTUNIDAD"
    FORTALEZAS = "FORTALEZAS"
    PLAN_ACCION = "PLAN_ACCION"
    COMENTARIOS_TEMA = "COMENTARIOS_TEMA"
    RECOMENDACIONES = "RECOMENDACIONES"
    COMPARATIVO = "COMPARATIVO"
    DESCONOCIDA = "DESCONOCIDA"


PATRONES_INTENCIONES = {
    Intencion.RESUMEN_EJECUTIVO: [
        "resumen",
        "resumen ejecutivo",
        "diagnostico",
        "diagnóstico",
        "reporte",
        "informe",
        "panorama",
        "lectura general",
    ],
    Intencion.AREAS_OPORTUNIDAD: [
        "area de oportunidad",
        "areas de oportunidad",
        "área de oportunidad",
        "áreas de oportunidad",
        "problema",
        "problemas",
        "riesgo",
        "riesgos",
        "foco rojo",
        "focos rojos",
        "que esta mal",
        "qué está mal",
        "que debemos mejorar",
        "qué debemos mejorar",
        "donde estamos fallando",
        "dónde estamos fallando",
        "debilidades",
    ],
    Intencion.FORTALEZAS: [
        "fortaleza",
        "fortalezas",
        "positivo",
        "positivos",
        "mejor evaluado",
        "mejor calificado",
        "que salio bien",
        "qué salió bien",
        "buenas practicas",
        "buenas prácticas",
    ],
    Intencion.PLAN_ACCION: [
        "plan",
        "plan de accion",
        "plan de acción",
        "30",
        "60",
        "90",
        "acciones",
        "accion",
        "acción",
        "seguimiento",
        "mejora",
    ],
    Intencion.COMENTARIOS_TEMA: [
        "comentario",
        "comentarios",
        "que dicen",
        "qué dicen",
        "que opinan",
        "qué opinan",
        "hablan",
        "mencionan",
        "resume los comentarios",
        "resumen de comentarios",
    ],
    Intencion.RECOMENDACIONES: [
        "recomendacion",
        "recomendación",
        "recomendaciones",
        "sugerencia",
        "sugerencias",
        "que recomiendas",
        "qué recomiendas",
        "que hacemos",
        "qué hacemos",
    ],
    Intencion.COMPARATIVO: [
        "comparativo",
        "comparar",
        "ranking",
        "mejor carrera",
        "peor carrera",
        "contra",
        "diferencia",
    ],
}


def normalizar_texto(texto):
    texto = str(texto or "").lower().strip()

    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
        "ñ": "n",
    }

    for original, limpio in reemplazos.items():
        texto = texto.replace(original, limpio)

    return texto


def detectar_intencion(pregunta):
    pregunta_limpia = normalizar_texto(pregunta)

    puntajes = {}

    for intencion, patrones in PATRONES_INTENCIONES.items():
        puntaje = 0

        for patron in patrones:
            patron_limpio = normalizar_texto(patron)

            if patron_limpio in pregunta_limpia:
                puntaje += 1

        if puntaje > 0:
            puntajes[intencion] = puntaje

    if not puntajes:
        return Intencion.DESCONOCIDA

    return max(puntajes, key=puntajes.get)
