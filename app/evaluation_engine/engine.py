"""Motor de evaluación de respuestas (RF-04, RF-05).

Orquesta: validar la respuesta del usuario → construir prompt → llamar a la IA
(vía ai_client) → validar la salida (vía validation) → devolver la evaluación con
su trazabilidad. No importa el SDK de Anthropic directamente (§3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.ai_client import AICallResult, AIClient, ai_client as default_ai_client
from app.evaluation_engine.prompts import (
    CAMPOS_EVALUACION,
    PROMPT_EVALUACION_VERSION,
    SYSTEM_PROMPT_EVALUACION,
    construir_prompt_evaluacion,
)
from app.validation import (
    InterviewConfig,
    validar_respuesta,
    validar_salida_evaluacion,
)


@dataclass
class Evaluation:
    """Evaluación validada de una respuesta, con su rastro de IA (RF-05/RF-10)."""

    puntaje: int
    fortalezas: list[str]
    errores: list[str]
    omisiones: list[str]
    respuesta_mejorada: str
    coherente_con_configuracion: bool
    trace: AICallResult
    prompt_version: str = PROMPT_EVALUACION_VERSION

    def resumen(self) -> dict[str, Any]:
        """Vista simple de la evaluación (sin trazabilidad), para la UI/API."""
        return {
            "puntaje": self.puntaje,
            "fortalezas": self.fortalezas,
            "errores": self.errores,
            "omisiones": self.omisiones,
            "respuesta_mejorada": self.respuesta_mejorada,
            "coherente_con_configuracion": self.coherente_con_configuracion,
        }


class EvaluationEngine:
    """Evalúa las respuestas del usuario con IA de forma estructurada."""

    def __init__(self, client: AIClient | None = None) -> None:
        self._client = client or default_ai_client

    def evaluar_respuesta(
        self,
        config: InterviewConfig,
        pregunta: str,
        respuesta: str,
        criterios: list[str] | None = None,
    ) -> Evaluation:
        """Evalúa una respuesta y devuelve la retroalimentación estructurada.

        Args:
            config: configuración de la entrevista.
            pregunta: enunciado que se respondió.
            respuesta: respuesta del usuario (se valida antes de gastar en IA).
            criterios: criterios de evaluación de la pregunta.

        Returns:
            Evaluation con puntaje, fortalezas, errores, omisiones, respuesta
            mejorada y coherencia, más la trazabilidad de IA.

        Raises:
            ValidationError: si la respuesta está vacía/es inválida (RNF-04) o si
                la salida de la IA no cumple la estructura esperada.
            AIResponseError: si la IA falla o no entrega JSON válido tras reintentos.
        """
        # 1) Validar la respuesta ANTES de llamar a la IA (RNF-04: no gastar en
        #    una llamada si la entrada ya es inválida).
        respuesta_limpia = validar_respuesta(respuesta)

        # 2) Construir prompt y llamar a la IA.
        user_prompt = construir_prompt_evaluacion(
            config, pregunta, respuesta_limpia, criterios
        )
        resultado = self._client.generate_json(
            user_prompt=user_prompt,
            required_fields=CAMPOS_EVALUACION,
            system_prompt=SYSTEM_PROMPT_EVALUACION,
            criterios=criterios,
        )

        # 3) Validar estructura y rangos de la salida (RF-12/RNF-04).
        datos = validar_salida_evaluacion(resultado.data)

        return Evaluation(
            puntaje=datos["puntaje"],
            fortalezas=datos["fortalezas"],
            errores=datos["errores"],
            omisiones=datos["omisiones"],
            respuesta_mejorada=datos["respuesta_mejorada"],
            coherente_con_configuracion=datos["coherente_con_configuracion"],
            trace=resultado,
        )


# Instancia compartida lista para usar.
evaluation_engine = EvaluationEngine()
