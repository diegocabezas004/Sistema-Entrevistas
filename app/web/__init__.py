"""Interfaz web server-rendered con Jinja2 (RNF-07: usabilidad).

Capa de presentación delgada: no habla con la IA ni con la base de datos,
solo con `InterviewService`, igual que la API REST. Las plantillas viven en
`templates/` y los estilos en `static/`.
"""

from app.web.routes import get_service, router

__all__ = ["router", "get_service"]
