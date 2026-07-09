"""Capa de acceso a la IA (Anthropic/Claude).

Único módulo autorizado a hablar con la API de Anthropic (CLAUDE.md §3).
El resto del sistema importa desde aquí:

    from app.ai_client import ai_client, AICallResult, AIResponseError
"""

from app.ai_client.client import AIClient, AICallResult, ai_client, BASE_SYSTEM_PROMPT
from app.ai_client.errors import AIClientError, AIConfigError, AIResponseError

__all__ = [
    "AIClient",
    "AICallResult",
    "ai_client",
    "BASE_SYSTEM_PROMPT",
    "AIClientError",
    "AIConfigError",
    "AIResponseError",
]
