"""Prompt de resumen final y plan de mejora (CLAUDE.md §6c).

Tercer prompt obligatorio. Versionado y documentado para el `catalogo_prompts.md`.
Toma todas las evaluaciones de la sesión y produce el resultado general (RF-06) y
un plan de mejora personalizado (RF-07).
"""

from __future__ import annotations

from app.validation import InterviewConfig

PROMPT_RESUMEN_VERSION = "1.0"

# Campos que el JSON del resumen DEBE traer (§6c).
CAMPOS_RESUMEN = [
    "nivel_estimado",
    "puntaje_general",
    "areas_fuertes",
    "areas_mejora",
    "plan_de_estudio",
]

SYSTEM_PROMPT_RESUMEN = (
    "Tu tarea es sintetizar el desempeño global de una persona en una entrevista "
    "técnica de práctica, a partir de las evaluaciones de todas sus respuestas. "
    "Estima un nivel general, un puntaje global de 0 a 100, las áreas fuertes y "
    "las áreas de mejora, y propón un plan de estudio breve y accionable basado "
    "en el desempeño REAL de esta entrevista (no genérico). "
    "El 'nivel_estimado' debe ser junior, intermedio o senior. "
    "Recuerda: esto es práctica, no una certificación oficial; nunca afirmes que "
    "la persona aprobará una entrevista real ni que será contratada. "
    "Devuelve EXCLUSIVAMENTE un objeto JSON con esta forma:\n"
    "{\n"
    '  "nivel_estimado": "junior|intermedio|senior",\n'
    '  "puntaje_general": 0,\n'
    '  "areas_fuertes": ["..."],\n'
    '  "areas_mejora": ["..."],\n'
    '  "plan_de_estudio": ["paso 1", "paso 2"]\n'
    "}"
)

_IDIOMA_INSTRUCCION = {
    "es": "Redacta todo el resumen en español.",
    "en": "Write the entire summary in English.",
}


def construir_prompt_resumen(
    config: InterviewConfig, items: list[dict]
) -> str:
    """Arma el user prompt para el resumen final (§6c).

    Args:
        config: configuración de la entrevista.
        items: lista de evaluaciones por pregunta. Cada dict debe traer:
            pregunta, tema, puntaje, fortalezas, errores, omisiones.
    """
    bloques = []
    for i, it in enumerate(items, start=1):
        bloques.append(
            f"Pregunta {i} (tema: {it.get('tema', 'N/A')}): {it.get('pregunta', '')}\n"
            f"  Puntaje: {it.get('puntaje', 'N/A')}\n"
            f"  Fortalezas: {', '.join(it.get('fortalezas', [])) or 'ninguna'}\n"
            f"  Errores: {', '.join(it.get('errores', [])) or 'ninguno'}\n"
            f"  Omisiones: {', '.join(it.get('omisiones', [])) or 'ninguna'}"
        )
    detalle = "\n\n".join(bloques)
    idioma_instr = _IDIOMA_INSTRUCCION.get(config.idioma, _IDIOMA_INSTRUCCION["es"])

    return (
        f"Rol: {config.rol}\n"
        f"Tecnología: {config.tecnologia}\n"
        f"Nivel configurado: {config.nivel}\n"
        f"Tipo de entrevista: {config.tipo}\n\n"
        f"Evaluaciones de la sesión ({len(items)} respuestas):\n\n{detalle}\n\n"
        f"{idioma_instr}\n"
        "Genera ahora el resumen final y el plan de mejora como un único objeto JSON."
    )
