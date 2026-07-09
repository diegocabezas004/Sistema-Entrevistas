"""Prompt de generación de preguntas (CLAUDE.md §6a).

Versionado y documentado para el `catalogo_prompts.md` y para el criterio
"Calidad del prompting" (8%). El `BASE_SYSTEM_PROMPT` del ai_client ya añade las
restricciones éticas y la obligación de responder en JSON; aquí se describe la
tarea concreta y la forma exacta del JSON esperado.
"""

from __future__ import annotations

from app.validation import InterviewConfig

# Versión del prompt (para trazabilidad y catálogo). Subir si cambia el diseño.
PROMPT_PREGUNTA_VERSION = "1.0"

# Campos que el JSON de la IA DEBE traer (los valida ai_client y luego validation).
CAMPOS_PREGUNTA = ["pregunta", "dificultad", "criterios_evaluados", "tema"]

# Instrucciones específicas de la tarea (se combinan con BASE_SYSTEM_PROMPT).
SYSTEM_PROMPT_PREGUNTA = (
    "Tu tarea es generar UNA sola pregunta de entrevista técnica, nueva y "
    "contextualizada al rol, tecnología, nivel y tipo indicados. "
    "La pregunta debe ser distinta a las ya realizadas en la sesión (evita "
    "repetir tema o enunciado). "
    "El campo 'dificultad' debe coincidir exactamente con el nivel configurado. "
    "Devuelve EXCLUSIVAMENTE un objeto JSON con esta forma:\n"
    "{\n"
    '  "pregunta": "texto de la pregunta",\n'
    '  "dificultad": "junior|intermedio|senior",\n'
    '  "criterios_evaluados": ["criterio1", "criterio2"],\n'
    '  "tema": "tema principal de la pregunta"\n'
    "}"
)

# Mapa de idioma canónico → instrucción para la IA.
_IDIOMA_INSTRUCCION = {
    "es": "Redacta la pregunta en español.",
    "en": "Write the question in English.",
}

# Mapa de tipo → matiz de la pregunta, para guiar a la IA (RF-01/RF-02).
_TIPO_INSTRUCCION = {
    "tecnica": "Enfócate en conocimiento técnico aplicado.",
    "conceptual": "Enfócate en conceptos y fundamentos teóricos.",
    "practica": "Plantea un problema práctico o de resolución de código.",
    "situacional": "Plantea una situación real de trabajo a resolver.",
    "arquitectura": "Plantea una pregunta de diseño o arquitectura básica.",
    "mixta": "Puedes combinar teoría, práctica y diseño.",
}


def construir_prompt_pregunta(
    config: InterviewConfig, preguntas_previas: list[str] | None = None
) -> str:
    """Arma el user prompt para generar una pregunta.

    Incluye las preguntas ya hechas en la sesión para que la IA no las repita
    (RF-02: dos entrevistas con la misma config no deben dar el mismo set).
    """
    previas = preguntas_previas or []
    if previas:
        lista = "\n".join(f"- {p}" for p in previas)
        bloque_previas = (
            "Preguntas YA realizadas en esta sesión (NO las repitas ni hagas "
            f"variaciones cercanas):\n{lista}"
        )
    else:
        bloque_previas = "Aún no se ha realizado ninguna pregunta en esta sesión."

    idioma_instr = _IDIOMA_INSTRUCCION.get(config.idioma, _IDIOMA_INSTRUCCION["es"])
    tipo_instr = _TIPO_INSTRUCCION.get(config.tipo, _TIPO_INSTRUCCION["mixta"])

    return (
        f"Rol: {config.rol}\n"
        f"Tecnología: {config.tecnologia}\n"
        f"Nivel: {config.nivel}\n"
        f"Tipo de entrevista: {config.tipo}\n"
        f"{tipo_instr}\n"
        f"{idioma_instr}\n\n"
        f"{bloque_previas}\n\n"
        "Genera ahora la siguiente pregunta como un único objeto JSON."
    )
