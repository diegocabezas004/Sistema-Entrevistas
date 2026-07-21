"""Configuración central del sistema.

Carga todas las variables de entorno en un único lugar (RNF-02: las
credenciales solo llegan por entorno, nunca hardcodeadas). Cualquier módulo
que necesite un parámetro de configuración lo pide aquí, no a os.environ
directamente, para mantener una sola fuente de verdad.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Carga el archivo .env de la raíz del proyecto si existe.
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")

# Aviso obligatorio (CLAUDE.md §12): la evaluación es práctica, no certificación.
# Vive aquí, en un módulo sin dependencias internas, para que tanto la API REST
# como la interfaz web lo usen sin importarse entre sí.
DISCLAIMER = (
    "Esta es una herramienta de práctica para entrevistas. No es una "
    "certificación oficial ni garantiza resultados en procesos reales."
)


@dataclass(frozen=True)
class Settings:
    """Valores de configuración inmutables leídos del entorno."""

    anthropic_api_key: str
    anthropic_model: str
    anthropic_max_tokens: int
    ai_max_retries: int
    database_url: str
    app_host: str
    app_port: int

    @property
    def sqlite_path(self) -> str:
        """Ruta física del archivo SQLite a partir de DATABASE_URL.

        Acepta el formato 'sqlite:///./entrevistas.db' y devuelve la ruta
        absoluta del archivo. Si no es una URL sqlite, la devuelve tal cual.
        """
        url = self.database_url
        prefix = "sqlite:///"
        if url.startswith(prefix):
            raw = url[len(prefix):]
            return str((_ROOT / raw).resolve()) if not os.path.isabs(raw) else raw
        return url


def _get_int(name: str, default: int) -> int:
    """Lee un entero del entorno con valor por defecto tolerante a errores."""
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def load_settings() -> Settings:
    """Construye el objeto Settings desde el entorno.

    Nota: no exige la API key aquí para permitir arrancar el resto del sistema
    (por ejemplo, correr pruebas de validación) sin credenciales. El ai_client
    sí la exige en el momento de hacer una llamada real (RNF-06).
    """
    return Settings(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5"),
        anthropic_max_tokens=_get_int("ANTHROPIC_MAX_TOKENS", 1500),
        ai_max_retries=_get_int("AI_MAX_RETRIES", 1),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./entrevistas.db"),
        app_host=os.getenv("APP_HOST", "127.0.0.1"),
        app_port=_get_int("APP_PORT", 8000),
    )


# Instancia compartida para todo el proyecto.
settings = load_settings()
