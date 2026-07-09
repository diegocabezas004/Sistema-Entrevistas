"""Gestión de conexión a SQLite.

Encapsula la apertura de conexiones, la activación de claves foráneas y la
creación del esquema. Usar SQLite (librería estándar `sqlite3`) mantiene la
defensa 100% local y sin dependencias externas de base de datos.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.config import settings as default_settings
from app.storage.schema import SCHEMA_SQL


class Database:
    """Envuelve el acceso a un archivo SQLite (o ':memory:' para pruebas)."""

    def __init__(self, path: str | None = None) -> None:
        # Si no se pasa ruta, se toma de la configuración (DATABASE_URL).
        self.path = path or default_settings.sqlite_path
        # Crear la carpeta contenedora si la ruta es un archivo en disco.
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Abre una conexión con FK activadas y filas accesibles por nombre.

        Hace commit al salir sin error y rollback si hay excepción, para que un
        fallo a mitad de una operación no deje datos a medias (RF-12).
        """
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row           # filas tipo dict
        conn.execute("PRAGMA foreign_keys = ON")  # integridad referencial
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_schema(self) -> None:
        """Crea las tablas si no existen (idempotente)."""
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)


# Instancia compartida por defecto (usa la ruta de la configuración).
database = Database()
