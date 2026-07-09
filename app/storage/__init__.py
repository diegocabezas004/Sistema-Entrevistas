"""Persistencia SQLite con trazabilidad completa de IA (RF-08, RF-10, RNF-05).

Expone el repositorio y la clase Database para el resto del sistema.
"""

from app.storage.db import Database, database
from app.storage.repository import Repository, repository

__all__ = ["Database", "database", "Repository", "repository"]
