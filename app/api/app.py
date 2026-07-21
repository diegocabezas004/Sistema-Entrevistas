"""Aplicación FastAPI: endpoints REST del simulador (RF-01…RF-10, RF-12).

Expone el flujo de entrevista y traduce los errores de negocio a códigos HTTP
claros (RNF-06): validación → 400, fallo de IA → 502, error inesperado → 500.
El módulo `interview` orquesta; aquí solo se adapta HTTP ↔ servicio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.ai_client import AIClientError, AIConfigError
from app.api.schemas import DISCLAIMER, ConfigRequest, RespuestaRequest
from app.interview import InterviewService, interview_service
from app.validation import ValidationError
from app.web import router as web_router

_ESTATICOS = Path(__file__).resolve().parent.parent / "web" / "static"


def get_service() -> InterviewService:
    """Dependencia que provee el servicio de entrevista.

    Se puede sobreescribir en pruebas con `app.dependency_overrides` para inyectar
    un servicio simulado sin llamar a la API real.
    """
    return interview_service


def create_app() -> FastAPI:
    """Construye y configura la aplicación FastAPI."""
    app = FastAPI(
        title="Simulador Generativo de Entrevistas Técnicas",
        description=DISCLAIMER,
        version="1.0.0",
    )

    # ---------------- Manejo de errores (RF-12 / RNF-06) ---------------- #
    @app.exception_handler(ValidationError)
    async def _validation_handler(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": str(exc), "campo": exc.campo},
        )

    @app.exception_handler(AIConfigError)
    async def _ai_config_handler(_: Request, exc: AIConfigError) -> JSONResponse:
        # Falta configuración (p. ej. API key): 503 servicio no disponible.
        return JSONResponse(
            status_code=503,
            content={"error": "Servicio de IA no configurado", "detalle": str(exc)},
        )

    @app.exception_handler(AIClientError)
    async def _ai_error_handler(_: Request, exc: AIClientError) -> JSONResponse:
        # Fallo de la IA (JSON inválido tras reintentos, red, etc.): 502.
        return JSONResponse(
            status_code=502,
            content={"error": "Fallo al generar la respuesta de IA", "detalle": str(exc)},
        )

    # ------------------- Interfaz web (Jinja2, RNF-07) ------------------- #
    # La UI vive en `app.web` y consume el mismo InterviewService que la API,
    # así que no duplica lógica de negocio: solo presenta.
    app.mount("/static", StaticFiles(directory=str(_ESTATICOS)), name="static")
    app.include_router(web_router)

    @app.get("/", include_in_schema=False)
    async def inicio() -> RedirectResponse:
        return RedirectResponse("/ui")

    # ---------------------------- Rutas ---------------------------- #
    @app.get("/health", tags=["sistema"])
    async def health() -> dict[str, Any]:
        return {"estado": "ok", "aviso": DISCLAIMER}

    @app.post("/entrevistas", tags=["entrevista"])
    async def iniciar(
        config: ConfigRequest, service: InterviewService = Depends(get_service)
    ) -> dict[str, Any]:
        """Inicia una entrevista con la configuración dada (RF-01)."""
        resultado = service.iniciar_entrevista(config.model_dump())
        return {**resultado, "aviso": DISCLAIMER}

    @app.post("/entrevistas/{entrevista_id}/preguntas", tags=["entrevista"])
    async def generar_pregunta(
        entrevista_id: int, service: InterviewService = Depends(get_service)
    ) -> dict[str, Any]:
        """Genera la siguiente pregunta de la entrevista (RF-02)."""
        return service.generar_siguiente_pregunta(entrevista_id)

    @app.post(
        "/entrevistas/{entrevista_id}/preguntas/{pregunta_id}/respuesta",
        tags=["entrevista"],
    )
    async def responder(
        entrevista_id: int,
        pregunta_id: int,
        body: RespuestaRequest,
        service: InterviewService = Depends(get_service),
    ) -> dict[str, Any]:
        """Registra la respuesta del usuario y la evalúa (RF-03/RF-04/RF-05)."""
        return service.responder_pregunta(entrevista_id, pregunta_id, body.respuesta)

    @app.post("/entrevistas/{entrevista_id}/finalizar", tags=["entrevista"])
    async def finalizar(
        entrevista_id: int, service: InterviewService = Depends(get_service)
    ) -> dict[str, Any]:
        """Genera el resultado general y el plan de mejora (RF-06/RF-07)."""
        resultado = service.finalizar_entrevista(entrevista_id)
        return {**resultado, "aviso": DISCLAIMER}

    @app.get("/entrevistas", tags=["historial"])
    async def historial(
        service: InterviewService = Depends(get_service),
    ) -> dict[str, Any]:
        """Lista el historial de entrevistas para ver avances (RF-08/RF-09)."""
        return {"entrevistas": service.listar_historial()}

    @app.get("/entrevistas/{entrevista_id}", tags=["historial"])
    async def detalle(
        entrevista_id: int, service: InterviewService = Depends(get_service)
    ) -> Any:
        """Detalle completo de una entrevista (RF-08)."""
        entrevista = service.obtener_entrevista(entrevista_id)
        if entrevista is None:
            return JSONResponse(
                status_code=404, content={"error": "Entrevista no encontrada"}
            )
        return entrevista

    @app.get("/entrevistas/{entrevista_id}/trazas", tags=["trazabilidad"])
    async def trazas(
        entrevista_id: int, service: InterviewService = Depends(get_service)
    ) -> dict[str, Any]:
        """Trazabilidad de IA de la entrevista: prompts y respuestas (RF-10)."""
        return {"trazas": service.obtener_trazas(entrevista_id)}

    return app


# Aplicación lista para uvicorn: `uvicorn app.api.app:app`
app = create_app()
