"""Motor de retroalimentación final y plan de mejora (RF-06, RF-07).

Sintetiza el resultado general de la entrevista y genera un plan de mejora
personalizado llamando a la IA a través de ai_client.
"""

from app.feedback.engine import (
    FeedbackEngine,
    FeedbackSummary,
    feedback_engine,
)
from app.feedback.prompts import (
    CAMPOS_RESUMEN,
    PROMPT_RESUMEN_VERSION,
    SYSTEM_PROMPT_RESUMEN,
    construir_prompt_resumen,
)

__all__ = [
    "FeedbackEngine",
    "FeedbackSummary",
    "feedback_engine",
    "construir_prompt_resumen",
    "CAMPOS_RESUMEN",
    "PROMPT_RESUMEN_VERSION",
    "SYSTEM_PROMPT_RESUMEN",
]
