"""Punto de entrada del servidor.

Permite arrancar con `python -m app.main` además de
`uvicorn app.api.app:app --reload`. Lee host y puerto de la configuración (.env).
"""

from __future__ import annotations

import uvicorn

from app.api.app import app
from app.config import settings


def main() -> None:
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)


if __name__ == "__main__":
    main()
