"""Motor de retroalimentación final y plan de mejora (RF-06, RF-07).

Toma todas las evaluaciones de la sesión y produce el resultado general y un
plan de mejora personalizado. La parte cualitativa (nivel, áreas, plan) la genera
la IA; además se calcula localmente el promedio de puntajes como referencia
objetiva (no se confía ciegamente en la IA para la agregación numérica).

No importa el SDK de Anthropic directamente (§3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ai_client import AICallResult, AIClient, ai_client as default_ai_client
from app.feedback.prompts import (
    CAMPOS_RESUMEN,
    PROMPT_RESUMEN_VERSION,
    SYSTEM_PROMPT_RESUMEN,
    construir_prompt_resumen,
)
from app.validation import InterviewConfig, validar_salida_resumen
from app.validation.errors import ValidationError


@dataclass
class FeedbackSummary:
    """Resumen final validado, con trazabilidad de IA (RF-06/RF-07/RF-10)."""

    nivel_estimado: str
    puntaje_general: int              # puntaje global estimado por la IA
    promedio_calculado: float         # promedio local de puntajes (referencia)
    areas_fuertes: list[str]
    areas_mejora: list[str]
    plan_de_estudio: list[str]
    trace: AICallResult
    prompt_version: str = PROMPT_RESUMEN_VERSION

    def resumen(self) -> dict[str, Any]:
        """Vista simple del resumen (sin trazabilidad), para la UI/API."""
        return {
            "nivel_estimado": self.nivel_estimado,
            "puntaje_general": self.puntaje_general,
            "promedio_calculado": self.promedio_calculado,
            "areas_fuertes": self.areas_fuertes,
            "areas_mejora": self.areas_mejora,
            "plan_de_estudio": self.plan_de_estudio,
        }


class FeedbackEngine:
    """Genera el resultado general y el plan de mejora de una entrevista."""

    def __init__(self, client: AIClient | None = None) -> None:
        self._client = client or default_ai_client

    @staticmethod
    def _promedio(items: list[dict]) -> float:
        """Promedio de los puntajes por pregunta (referencia objetiva)."""
        puntajes = [
            it["puntaje"]
            for it in items
            if isinstance(it.get("puntaje"), (int, float))
        ]
        if not puntajes:
            return 0.0
        return round(sum(puntajes) / len(puntajes), 1)

    def generar_resumen(
        self, config: InterviewConfig, items: list[dict]
    ) -> FeedbackSummary:
        """Genera el resumen final a partir de las evaluaciones de la sesión.

        Args:
            config: configuración de la entrevista.
            items: lista de evaluaciones por pregunta (pregunta, tema, puntaje,
                fortalezas, errores, omisiones).

        Returns:
            FeedbackSummary con nivel estimado, puntaje general, promedio local,
            áreas y plan de estudio, más la trazabilidad de IA.

        Raises:
            ValidationError: si no hay evaluaciones (no se puede resumir vacío,
                RNF-04) o si la salida de la IA no cumple la estructura.
            AIResponseError: si la IA falla o no entrega JSON válido tras reintentos.
        """
        if not items:
            raise ValidationError(
                "No hay respuestas evaluadas: no se puede generar un resumen.",
                campo="items",
            )

        promedio = self._promedio(items)

        user_prompt = construir_prompt_resumen(config, items)
        resultado = self._client.generate_json(
            user_prompt=user_prompt,
            required_fields=CAMPOS_RESUMEN,
            system_prompt=SYSTEM_PROMPT_RESUMEN,
        )

        datos = validar_salida_resumen(resultado.data)

        return FeedbackSummary(
            nivel_estimado=datos["nivel_estimado"],
            puntaje_general=datos["puntaje_general"],
            promedio_calculado=promedio,
            areas_fuertes=datos["areas_fuertes"],
            areas_mejora=datos["areas_mejora"],
            plan_de_estudio=datos["plan_de_estudio"],
            trace=resultado,
        )


# Instancia compartida lista para usar.
feedback_engine = FeedbackEngine()
