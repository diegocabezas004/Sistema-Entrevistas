"""Contratos de entrada/salida de la API (Pydantic).

Definen la forma de las peticiones y respuestas REST. La validación de negocio
(coherencia, rangos, catálogos) la hace el módulo `validation`; aquí Pydantic
solo garantiza tipos y presencia de campos, para dar errores tempranos claros.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# Aviso obligatorio (CLAUDE.md §12): la evaluación es práctica, no certificación.
DISCLAIMER = (
    "Esta es una herramienta de práctica para entrevistas. No es una "
    "certificación oficial ni garantiza resultados en procesos reales."
)


class ConfigRequest(BaseModel):
    """Configuración de entrevista enviada por el usuario (RF-01)."""

    rol: str = Field(..., examples=["Backend Developer"])
    tecnologia: str = Field(..., examples=["Python"])
    nivel: str = Field(..., examples=["junior", "intermedio", "senior"])
    idioma: str = Field("es", examples=["es", "en"])
    cantidad_preguntas: int = Field(..., ge=1, le=20, examples=[3])
    tipo: str = Field(
        ...,
        examples=["tecnica", "conceptual", "practica", "situacional", "arquitectura", "mixta"],
    )


class RespuestaRequest(BaseModel):
    """Respuesta del usuario a una pregunta (RF-03)."""

    respuesta: str = Field(..., examples=["Una variable es un espacio de memoria..."])


class ErrorResponse(BaseModel):
    """Forma estándar de un error controlado (RNF-06)."""

    error: str
    campo: str | None = None
    detalle: str | None = None
