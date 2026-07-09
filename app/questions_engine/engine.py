"""Motor de generación de preguntas (RF-02).

Orquesta: construir prompt → llamar a la IA (vía ai_client) → validar la salida
(vía validation) → devolver una pregunta lista para usar, con su trazabilidad.

No importa el SDK de Anthropic directamente: pasa siempre por `ai_client` (§3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ai_client import AICallResult, AIClient, ai_client as default_ai_client
from app.questions_engine.prompts import (
    CAMPOS_PREGUNTA,
    PROMPT_PREGUNTA_VERSION,
    SYSTEM_PROMPT_PREGUNTA,
    construir_prompt_pregunta,
)
from app.validation import InterviewConfig, validar_salida_pregunta


@dataclass
class GeneratedQuestion:
    """Pregunta generada y validada, con su rastro de IA para persistir (RF-10)."""

    pregunta: str
    dificultad: str
    criterios_evaluados: list[str]
    tema: str
    trace: AICallResult                 # prompt, respuesta cruda, modelo, timestamp
    prompt_version: str = PROMPT_PREGUNTA_VERSION

    def resumen(self) -> dict[str, Any]:
        """Vista simple de la pregunta (sin trazabilidad), para la UI/API."""
        return {
            "pregunta": self.pregunta,
            "dificultad": self.dificultad,
            "criterios_evaluados": self.criterios_evaluados,
            "tema": self.tema,
        }


class QuestionsEngine:
    """Genera preguntas de entrevista contextualizadas."""

    def __init__(self, client: AIClient | None = None) -> None:
        # Inyección de dependencia: facilita las pruebas con un cliente simulado.
        self._client = client or default_ai_client

    def generar_pregunta(
        self,
        config: InterviewConfig,
        preguntas_previas: list[str] | None = None,
    ) -> GeneratedQuestion:
        """Genera una pregunta nueva coherente con la configuración.

        Args:
            config: configuración validada de la entrevista.
            preguntas_previas: enunciados ya usados en la sesión (evita repetición).

        Returns:
            GeneratedQuestion con la pregunta validada y su trazabilidad.

        Raises:
            AIResponseError: si la IA falla o no entrega JSON válido tras reintentos.
            ValidationError: si la pregunta no es coherente con la config (RF-11).
        """
        user_prompt = construir_prompt_pregunta(config, preguntas_previas)

        # 1) Llamada a la IA (ai_client garantiza JSON con los campos base).
        resultado = self._client.generate_json(
            user_prompt=user_prompt,
            required_fields=CAMPOS_PREGUNTA,
            system_prompt=SYSTEM_PROMPT_PREGUNTA,
        )

        # 2) Validación profunda + coherencia con la config (RF-11).
        datos = validar_salida_pregunta(resultado.data, config=config)

        # 3) Empaquetar con su rastro de IA para trazabilidad (RF-10/RNF-05).
        return GeneratedQuestion(
            pregunta=datos["pregunta"],
            dificultad=datos["dificultad"],
            criterios_evaluados=datos["criterios_evaluados"],
            tema=datos["tema"],
            trace=resultado,
        )


# Instancia compartida lista para usar.
questions_engine = QuestionsEngine()
