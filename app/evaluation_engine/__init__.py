"""Motor de evaluación de respuestas (RF-04, RF-05).

Evalúa cada respuesta del usuario llamando a la IA a través de ai_client y
validando la salida con validation.
"""

from app.evaluation_engine.engine import (
    Evaluation,
    EvaluationEngine,
    evaluation_engine,
)
from app.evaluation_engine.prompts import (
    CAMPOS_EVALUACION,
    PROMPT_EVALUACION_VERSION,
    SYSTEM_PROMPT_EVALUACION,
    construir_prompt_evaluacion,
)

__all__ = [
    "Evaluation",
    "EvaluationEngine",
    "evaluation_engine",
    "construir_prompt_evaluacion",
    "CAMPOS_EVALUACION",
    "PROMPT_EVALUACION_VERSION",
    "SYSTEM_PROMPT_EVALUACION",
]
