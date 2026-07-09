"""Capa de API REST (FastAPI).

Expone el flujo de entrevista por HTTP y mapea errores de negocio a códigos
claros. Punto de entrada: `app.api.app:app`.
"""

from app.api.app import app, create_app, get_service

__all__ = ["app", "create_app", "get_service"]
