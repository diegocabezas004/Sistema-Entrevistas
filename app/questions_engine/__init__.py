"""Motor de generación de preguntas (RF-02).

Genera preguntas de entrevista llamando a la IA a través de ai_client y
validando la salida con validation.
"""

from app.questions_engine.engine import (
    GeneratedQuestion,
    QuestionsEngine,
    questions_engine,
)
from app.questions_engine.prompts import (
    CAMPOS_PREGUNTA,
    PROMPT_PREGUNTA_VERSION,
    SYSTEM_PROMPT_PREGUNTA,
    construir_prompt_pregunta,
)

__all__ = [
    "GeneratedQuestion",
    "QuestionsEngine",
    "questions_engine",
    "construir_prompt_pregunta",
    "CAMPOS_PREGUNTA",
    "PROMPT_PREGUNTA_VERSION",
    "SYSTEM_PROMPT_PREGUNTA",
]
