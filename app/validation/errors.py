"""Error de validación con mensaje claro y específico (RNF-06).

Se separa de los errores de IA (`app.ai_client.errors`) porque son cosas
distintas: aquí falla la ENTRADA del usuario o la ESTRUCTURA de datos, no la IA.
La `api` puede mapear esta excepción a un HTTP 400 con el mensaje directo.
"""

from __future__ import annotations


class ValidationError(ValueError):
    """La entrada o los datos no cumplen las reglas del dominio.

    Attributes:
        campo: nombre del campo que falló (para señalarlo en la UI/API).
    """

    def __init__(self, mensaje: str, campo: str | None = None) -> None:
        super().__init__(mensaje)
        self.campo = campo

    def __str__(self) -> str:  # mensaje legible para el usuario final
        base = super().__str__()
        return f"[{self.campo}] {base}" if self.campo else base
