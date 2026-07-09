"""Prompt de evaluación de respuestas (CLAUDE.md §6b).

Versionado y documentado para el `catalogo_prompts.md`. El BASE_SYSTEM_PROMPT del
ai_client ya añade las restricciones éticas y la obligación de JSON; aquí se
describe la tarea de evaluación y la forma exacta de la salida.
"""

from __future__ import annotations

from app.validation import InterviewConfig

PROMPT_EVALUACION_VERSION = "1.0"

# Campos que el JSON de evaluación DEBE traer (§6b).
CAMPOS_EVALUACION = [
    "puntaje",
    "fortalezas",
    "errores",
    "omisiones",
    "respuesta_mejorada",
    "coherente_con_configuracion",
]

SYSTEM_PROMPT_EVALUACION = (
    "Tu tarea es evaluar la respuesta de una persona a una pregunta de entrevista "
    "técnica. Evalúa con criterio profesional pero constructivo, considerando: "
    "precisión técnica, claridad, profundidad, estructura y riesgo de conceptos "
    "incorrectos. Ajusta la exigencia al nivel configurado (junior es más "
    "permisivo que senior). "
    "El 'puntaje' es un entero de 0 a 100. "
    "Marca 'coherente_con_configuracion' en false solo si la pregunta o la "
    "respuesta no corresponden al rol/nivel/tecnología configurados. "
    "Nunca afirmes que la persona aprobará una entrevista real ni que será "
    "contratada. Devuelve EXCLUSIVAMENTE un objeto JSON con esta forma:\n"
    "{\n"
    '  "puntaje": 0,\n'
    '  "fortalezas": ["..."],\n'
    '  "errores": ["..."],\n'
    '  "omisiones": ["..."],\n'
    '  "respuesta_mejorada": "...",\n'
    '  "coherente_con_configuracion": true\n'
    "}"
)

_IDIOMA_INSTRUCCION = {
    "es": "Redacta toda la retroalimentación en español.",
    "en": "Write all feedback in English.",
}


def construir_prompt_evaluacion(
    config: InterviewConfig,
    pregunta: str,
    respuesta: str,
    criterios: list[str] | None = None,
) -> str:
    """Arma el user prompt para evaluar una respuesta (§6b).

    Args:
        config: configuración de la entrevista (aporta rol/nivel/tecnología).
        pregunta: enunciado evaluado.
        respuesta: respuesta del usuario a evaluar.
        criterios: criterios de evaluación asociados a la pregunta.
    """
    criterios = criterios or []
    bloque_criterios = (
        "Criterios de evaluación a considerar:\n"
        + "\n".join(f"- {c}" for c in criterios)
        if criterios
        else "No se especificaron criterios; usa tu criterio profesional."
    )
    idioma_instr = _IDIOMA_INSTRUCCION.get(config.idioma, _IDIOMA_INSTRUCCION["es"])

    return (
        f"Rol: {config.rol}\n"
        f"Tecnología: {config.tecnologia}\n"
        f"Nivel configurado: {config.nivel}\n\n"
        f"Pregunta:\n{pregunta}\n\n"
        f"Respuesta de la persona:\n{respuesta}\n\n"
        f"{bloque_criterios}\n\n"
        f"{idioma_instr}\n"
        "Evalúa ahora la respuesta y devuelve un único objeto JSON."
    )
