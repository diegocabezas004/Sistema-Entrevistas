"""Errores controlados de la capa de IA.

Estas excepciones permiten que el resto del sistema (evaluation_engine,
questions_engine, api) distinga un fallo de IA de un error de programación y
muestre mensajes claros al usuario (RF-12 / RNF-06), sin que el flujo se rompa.
"""

from __future__ import annotations


class AIClientError(Exception):
    """Error base de la capa de IA."""


class AIConfigError(AIClientError):
    """Falta configuración obligatoria (por ejemplo, la API key)."""


class AIResponseError(AIClientError):
    """La API respondió, pero la respuesta no se pudo usar.

    Cubre: JSON inválido, faltan campos esperados o la llamada falló tras
    agotar los reintentos. Lleva el texto crudo para trazabilidad (RF-10).
    """

    def __init__(self, message: str, raw_response: str | None = None) -> None:
        super().__init__(message)
        self.raw_response = raw_response
