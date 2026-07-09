"""Capa única de acceso a la API de Anthropic (Claude).

REGLA DURA (CLAUDE.md §3): ningún otro módulo del proyecto debe importar el SDK
de Anthropic ni llamar a la API directamente. Todo pasa por aquí. Esto permite:
  - cambiar de modelo/proveedor sin tocar el resto del código,
  - centralizar manejo de errores, reintentos y trazabilidad (RF-10, RF-12),
  - validar el JSON devuelto antes de entregarlo a otras capas (RF-11, RNF-04).

El método principal es `generate_json`: envía un system prompt + user prompt,
fuerza salida JSON, la parsea y valida los campos esperados. Si falla, reintenta
una vez; si vuelve a fallar, lanza un error controlado (AIResponseError).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Sequence

import anthropic

from app.config import Settings, settings as default_settings
from app.ai_client.errors import AIConfigError, AIResponseError

# System prompt base que se antepone a TODOS los prompts del sistema.
# Cubre las restricciones obligatorias del CLAUDE.md §6 y §12:
#  - nunca prometer contratación ni aprobación de una entrevista real,
#  - dejar claro que es una herramienta de práctica, no una certificación,
#  - responder SIEMPRE en JSON válido, sin texto adicional.
BASE_SYSTEM_PROMPT = (
    "Eres un asistente de práctica para entrevistas técnicas. "
    "Tu evaluación es una herramienta de estudio y práctica, NO una certificación "
    "oficial ni una garantía de resultado. "
    "NUNCA afirmes que la persona aprobará una entrevista real, será contratada, "
    "ni des garantías sobre procesos de reclutamiento reales. "
    "Respondes SIEMPRE con un único objeto JSON válido, sin texto antes ni después, "
    "sin comentarios y sin bloques de código Markdown."
)


@dataclass
class AICallResult:
    """Resultado de una llamada a la IA, con todo lo necesario para trazabilidad.

    Los campos crudos (prompt, system_prompt, raw_response, model, timestamp,
    criterios) son los que el módulo `storage` persiste para cumplir RF-10/RNF-05.
    """

    data: dict[str, Any]              # JSON ya parseado y validado
    raw_response: str                 # respuesta cruda tal cual la devolvió la IA
    system_prompt: str                # system prompt exacto usado
    user_prompt: str                  # user prompt exacto usado
    model: str                        # modelo usado (para trazabilidad)
    criterios: list[str] = field(default_factory=list)  # criterios de evaluación
    intentos: int = 1                 # cuántos intentos hicieron falta
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class AIClient:
    """Único punto de contacto con la API de Anthropic."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or default_settings
        self._client: anthropic.Anthropic | None = None

    # -- Cliente perezoso: no exige API key hasta que se hace una llamada real. --
    def _get_client(self) -> anthropic.Anthropic:
        if not self._settings.anthropic_api_key:
            raise AIConfigError(
                "Falta ANTHROPIC_API_KEY. Configúrala en el archivo .env "
                "(ver .env.example). Nunca la escribas en el código."
            )
        if self._client is None:
            self._client = anthropic.Anthropic(
                api_key=self._settings.anthropic_api_key
            )
        return self._client

    def generate_json(
        self,
        user_prompt: str,
        required_fields: Sequence[str],
        system_prompt: str = "",
        criterios: Sequence[str] | None = None,
    ) -> AICallResult:
        """Llama a la IA y devuelve un JSON validado.

        Args:
            user_prompt: contenido de la petición (contexto de la tarea).
            required_fields: campos que el JSON DEBE contener (RF-11/RNF-04).
            system_prompt: instrucciones específicas de la tarea; se combinan
                con BASE_SYSTEM_PROMPT.
            criterios: criterios de evaluación, solo para trazabilidad.

        Returns:
            AICallResult con el JSON parseado + datos de trazabilidad.

        Raises:
            AIConfigError: si falta la API key.
            AIResponseError: si tras un reintento el JSON sigue siendo inválido
                o faltan campos, o si la API falla.
        """
        full_system = BASE_SYSTEM_PROMPT
        if system_prompt:
            full_system = f"{BASE_SYSTEM_PROMPT}\n\n{system_prompt}"

        criterios_list = list(criterios or [])
        max_intentos = 1 + max(0, self._settings.ai_max_retries)
        last_raw = ""
        last_error = ""

        for intento in range(1, max_intentos + 1):
            raw = self._call_api(full_system, user_prompt)
            last_raw = raw
            try:
                data = self._parse_and_validate(raw, required_fields)
            except AIResponseError as exc:
                last_error = str(exc)
                continue  # reintentar (RNF-06)
            return AICallResult(
                data=data,
                raw_response=raw,
                system_prompt=full_system,
                user_prompt=user_prompt,
                model=self._settings.anthropic_model,
                criterios=criterios_list,
                intentos=intento,
            )

        # Se agotaron los intentos: error controlado con la respuesta cruda.
        raise AIResponseError(
            f"La IA no devolvió un JSON válido tras {max_intentos} intento(s). "
            f"Último problema: {last_error}",
            raw_response=last_raw,
        )

    # ------------------------------------------------------------------ #
    # Internos
    # ------------------------------------------------------------------ #
    def _call_api(self, system_prompt: str, user_prompt: str) -> str:
        """Hace la llamada real a Anthropic y devuelve el texto de la respuesta.

        Traduce errores del SDK a AIResponseError para no filtrar detalles del
        proveedor al resto del sistema (RF-12).
        """
        client = self._get_client()
        try:
            response = client.messages.create(
                model=self._settings.anthropic_model,
                max_tokens=self._settings.anthropic_max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
        except anthropic.APIError as exc:  # cubre red, rate limit, 4xx/5xx
            raise AIResponseError(f"Fallo al llamar a la IA: {exc}") from exc

        # Concatena los bloques de texto de la respuesta.
        partes = [b.text for b in response.content if getattr(b, "type", "") == "text"]
        return "".join(partes).strip()

    @staticmethod
    def _parse_and_validate(
        raw: str, required_fields: Sequence[str]
    ) -> dict[str, Any]:
        """Extrae el JSON del texto crudo y valida los campos esperados."""
        texto = AIClient._extract_json(raw)
        try:
            data = json.loads(texto)
        except json.JSONDecodeError as exc:
            raise AIResponseError(
                f"La respuesta no es JSON válido: {exc}", raw_response=raw
            ) from exc

        if not isinstance(data, dict):
            raise AIResponseError(
                "El JSON de la IA no es un objeto.", raw_response=raw
            )

        faltantes = [c for c in required_fields if c not in data]
        if faltantes:
            raise AIResponseError(
                f"Al JSON le faltan campos obligatorios: {', '.join(faltantes)}",
                raw_response=raw,
            )
        return data

    @staticmethod
    def _extract_json(raw: str) -> str:
        """Limpia la respuesta: quita fences ```json ... ``` si los hubiera y
        recorta al primer objeto JSON encontrado."""
        texto = raw.strip()
        # Quitar bloques de código Markdown si el modelo los añadió pese al prompt.
        fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", texto, re.DOTALL)
        if fence:
            texto = fence.group(1).strip()
        # Recortar desde la primera { hasta la última } (tolerante a texto extra).
        inicio = texto.find("{")
        fin = texto.rfind("}")
        if inicio != -1 and fin != -1 and fin > inicio:
            return texto[inicio : fin + 1]
        return texto


# Instancia compartida lista para usar por el resto del sistema.
ai_client = AIClient()
