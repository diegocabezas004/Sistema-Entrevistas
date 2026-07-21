"""Rutas de la interfaz web (Jinja2).

Flujo de tres pantallas, todo con formularios HTML y redirecciones
(patrón POST-Redirect-GET), sin depender de JavaScript:

    /ui                              configurar entrevista + historial
    /ui/entrevistas/{id}             responder preguntas
    /ui/entrevistas/{id}/resultado   resultado y plan de mejora

Las llamadas costosas a la IA se hacen de forma perezosa en el GET: al entrar a
la pantalla de preguntas se genera la siguiente pregunta si falta, y al entrar
al resultado se finaliza la entrevista si aún no tiene resumen. Así, si la IA
falla, basta con recargar la página para reintentar (RF-12/RNF-06) en lugar de
dejar la sesión en un estado roto.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.ai_client import AIClientError, AIConfigError
from app.config import DISCLAIMER
from app.interview import InterviewService, interview_service
from app.validation import ValidationError
from app.validation.constants import (
    IDIOMAS,
    MAX_PREGUNTAS,
    MIN_PREGUNTAS,
    NIVELES,
    TIPOS_ENTREVISTA,
)

_AQUI = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(_AQUI / "templates"))
templates.env.globals["disclaimer"] = DISCLAIMER

router = APIRouter(tags=["ui"])


def get_service() -> InterviewService:
    """Dependencia del servicio de entrevista (sustituible en pruebas)."""
    return interview_service


# --------------------------------------------------------------------------- #
# Ayudas de presentación
# --------------------------------------------------------------------------- #

# Etiquetas legibles para el usuario: el dominio guarda valores canónicos sin
# tildes ("tecnica"), la interfaz muestra español correcto.
ETIQUETA_TIPO: dict[str, str] = {
    "tecnica": "Técnica",
    "conceptual": "Conceptual",
    "practica": "Práctica",
    "situacional": "Situacional",
    "arquitectura": "Arquitectura",
    "mixta": "Mixta",
}
ETIQUETA_NIVEL: dict[str, str] = {
    "junior": "Junior",
    "intermedio": "Intermedio",
    "senior": "Senior",
}
ETIQUETA_IDIOMA: dict[str, str] = {"es": "Español", "en": "Inglés"}

# Escenarios de la sección 7 de CLAUDE.md, listos para la demostración en vivo.
ESCENARIOS: list[dict[str, Any]] = [
    {
        "clave": "junior",
        "titulo": "Entrevista junior",
        "resumen": "Fundamentos y preguntas conceptuales.",
        "rol": "Desarrollador Backend",
        "tecnologia": "Python",
        "nivel": "junior",
        "cantidad_preguntas": 3,
        "tipo": "conceptual",
    },
    {
        "clave": "intermedio",
        "titulo": "Entrevista intermedia",
        "resumen": "Mezcla de teoría y resolución práctica.",
        "rol": "Desarrollador Full Stack",
        "tecnologia": "JavaScript y Node.js",
        "nivel": "intermedio",
        "cantidad_preguntas": 4,
        "tipo": "mixta",
    },
    {
        "clave": "arquitectura",
        "titulo": "Arquitectura y diseño",
        "resumen": "Diseño de sistemas y decisiones técnicas.",
        "rol": "Ingeniero de Software Senior",
        "tecnologia": "Microservicios y PostgreSQL",
        "nivel": "senior",
        "cantidad_preguntas": 3,
        "tipo": "arquitectura",
    },
]


def _banda(puntaje: int | float | None) -> str:
    """Nombre de la banda de desempeño para un puntaje 0–100.

    Se usa como etiqueta de lectura rápida junto a la barra; el número exacto
    siempre se muestra al lado para no esconder el dato real.
    """
    if puntaje is None:
        return "Sin evaluar"
    if puntaje >= 80:
        return "Sólido"
    if puntaje >= 60:
        return "Aceptable"
    if puntaje >= 40:
        return "En desarrollo"
    return "Inicial"


def _recorrido(detalle: dict[str, Any], activa_id: int | None = None) -> list[dict]:
    """Construye el track de progreso: una fila por pregunta configurada.

    Las preguntas aún no generadas aparecen como espacios pendientes, para que
    el usuario vea desde el inicio cuántas le faltan.
    """
    filas: list[dict[str, Any]] = []
    for pregunta in detalle.get("preguntas", []):
        evaluacion = pregunta.get("evaluacion")
        if pregunta["id"] == activa_id:
            estado = "activa"
        elif evaluacion is not None:
            estado = "evaluada"
        elif pregunta.get("respuesta"):
            estado = "respondida"
        else:
            estado = "abierta"
        filas.append(
            {
                "orden": pregunta["orden"],
                "tema": pregunta.get("tema") or "—",
                "estado": estado,
                "puntaje": evaluacion["puntaje"] if evaluacion else None,
                "banda": _banda(evaluacion["puntaje"] if evaluacion else None),
            }
        )

    total = detalle.get("cantidad_preguntas", len(filas))
    for orden in range(len(filas) + 1, total + 1):
        filas.append(
            {
                "orden": orden,
                "tema": "Por generar",
                "estado": "pendiente",
                "puntaje": None,
                "banda": _banda(None),
            }
        )
    return filas


def _contexto(detalle: dict[str, Any]) -> dict[str, Any]:
    """Datos de configuración de la entrevista, ya con etiquetas legibles."""
    return {
        "id": detalle["id"],
        "rol": detalle["rol"],
        "tecnologia": detalle["tecnologia"],
        "nivel": ETIQUETA_NIVEL.get(detalle["nivel"], detalle["nivel"]),
        "idioma": ETIQUETA_IDIOMA.get(detalle["idioma"], detalle["idioma"]),
        "tipo": ETIQUETA_TIPO.get(detalle["tipo"], detalle["tipo"]),
        "total": detalle["cantidad_preguntas"],
        "estado": detalle["estado"],
    }


def _volver(destino: str, error: str | None = None) -> RedirectResponse:
    """Redirección tras un POST (303), arrastrando el error si lo hubo."""
    if error:
        destino = f"{destino}?e={quote(error)}"
    return RedirectResponse(destino, status_code=303)


def _mensaje_de_error(exc: Exception) -> str:
    """Traduce una excepción del dominio a un mensaje para la pantalla (RNF-06)."""
    if isinstance(exc, ValidationError):
        return str(exc)
    if isinstance(exc, AIConfigError):
        return (
            "El servicio de IA no está configurado. Revisa la variable "
            "ANTHROPIC_API_KEY en el archivo .env y vuelve a intentarlo."
        )
    if isinstance(exc, AIClientError):
        return f"La IA no devolvió una respuesta utilizable: {exc}. Recarga para reintentar."
    return "Ocurrió un error inesperado. Recarga la página para reintentar."


# --------------------------------------------------------------------------- #
# Pantalla 1: configurar entrevista (RF-01, RF-08, RF-09)
# --------------------------------------------------------------------------- #
@router.get("/ui", response_class=HTMLResponse)
async def configurar(
    request: Request,
    e: str | None = None,
    service: InterviewService = Depends(get_service),
) -> Any:
    historial = []
    for fila in service.listar_historial():
        historial.append(
            {
                **fila,
                "nivel_label": ETIQUETA_NIVEL.get(fila["nivel"], fila["nivel"]),
                "tipo_label": ETIQUETA_TIPO.get(fila["tipo"], fila["tipo"]),
                "fecha": (fila.get("creada_en") or "")[:10],
            }
        )

    return templates.TemplateResponse(
        request,
        "configurar.html",
        {
            "error": e,
            "historial": historial,
            "escenarios": ESCENARIOS,
            "niveles": [(n, ETIQUETA_NIVEL[n]) for n in NIVELES],
            "tipos": [(t, ETIQUETA_TIPO[t]) for t in TIPOS_ENTREVISTA],
            "idiomas": [(i, ETIQUETA_IDIOMA[i]) for i in IDIOMAS],
            "min_preguntas": MIN_PREGUNTAS,
            "max_preguntas": MAX_PREGUNTAS,
        },
    )


@router.post("/ui/entrevistas")
async def crear(
    rol: str = Form(...),
    tecnologia: str = Form(...),
    nivel: str = Form(...),
    idioma: str = Form("es"),
    cantidad_preguntas: int = Form(...),
    tipo: str = Form(...),
    service: InterviewService = Depends(get_service),
) -> Any:
    """Crea la entrevista y lleva a la pantalla de preguntas (RF-01)."""
    try:
        creada = service.iniciar_entrevista(
            {
                "rol": rol,
                "tecnologia": tecnologia,
                "nivel": nivel,
                "idioma": idioma,
                "cantidad_preguntas": cantidad_preguntas,
                "tipo": tipo,
            }
        )
    except (ValidationError, AIClientError) as exc:
        return _volver("/ui", _mensaje_de_error(exc))
    return _volver(f"/ui/entrevistas/{creada['entrevista_id']}")


# --------------------------------------------------------------------------- #
# Pantalla 2: responder preguntas (RF-02, RF-03, RF-04, RF-05)
# --------------------------------------------------------------------------- #
@router.get("/ui/entrevistas/{entrevista_id}", response_class=HTMLResponse)
async def entrevista(
    request: Request,
    entrevista_id: int,
    e: str | None = None,
    service: InterviewService = Depends(get_service),
) -> Any:
    detalle = service.obtener_entrevista(entrevista_id)
    if detalle is None:
        return _volver("/ui", "Esa entrevista no existe.")

    error = e
    pendiente = next(
        (p for p in detalle["preguntas"] if not p.get("respuesta")), None
    )

    # Si no hay pregunta abierta, se genera la siguiente (RF-02). Al agotar el
    # total configurado, la entrevista pasa al resultado.
    if pendiente is None:
        if len(detalle["preguntas"]) >= detalle["cantidad_preguntas"]:
            return RedirectResponse(
                f"/ui/entrevistas/{entrevista_id}/resultado", status_code=303
            )
        try:
            service.generar_siguiente_pregunta(entrevista_id)
            detalle = service.obtener_entrevista(entrevista_id) or detalle
            pendiente = next(
                (p for p in detalle["preguntas"] if not p.get("respuesta")), None
            )
        except (ValidationError, AIClientError) as exc:
            error = _mensaje_de_error(exc)

    # Última evaluación disponible: así el usuario ve la retroalimentación de la
    # pregunta que acaba de responder antes de seguir (RF-05).
    evaluadas = [p for p in detalle["preguntas"] if p.get("evaluacion")]
    ultima = evaluadas[-1] if evaluadas else None
    if ultima:
        ultima = {**ultima, "banda": _banda(ultima["evaluacion"]["puntaje"])}

    return templates.TemplateResponse(
        request,
        "entrevista.html",
        {
            "error": error,
            "ctx": _contexto(detalle),
            "recorrido": _recorrido(detalle, activa_id=pendiente["id"] if pendiente else None),
            "pregunta": pendiente,
            "respondidas": len(evaluadas),
            "ultima": ultima,
        },
    )


@router.post("/ui/entrevistas/{entrevista_id}/preguntas/{pregunta_id}/respuesta")
async def responder(
    entrevista_id: int,
    pregunta_id: int,
    respuesta: str = Form(""),
    service: InterviewService = Depends(get_service),
) -> Any:
    """Guarda la respuesta y la evalúa con IA (RF-03/RF-04)."""
    destino = f"/ui/entrevistas/{entrevista_id}"
    try:
        service.responder_pregunta(entrevista_id, pregunta_id, respuesta)
    except (ValidationError, AIClientError) as exc:
        return _volver(destino, _mensaje_de_error(exc))
    return _volver(destino)


# --------------------------------------------------------------------------- #
# Pantalla 3: resultado y plan de mejora (RF-06, RF-07)
# --------------------------------------------------------------------------- #
@router.get("/ui/entrevistas/{entrevista_id}/resultado", response_class=HTMLResponse)
async def resultado(
    request: Request,
    entrevista_id: int,
    e: str | None = None,
    service: InterviewService = Depends(get_service),
) -> Any:
    detalle = service.obtener_entrevista(entrevista_id)
    if detalle is None:
        return _volver("/ui", "Esa entrevista no existe.")

    error = e
    if detalle.get("resumen") is None:
        try:
            service.finalizar_entrevista(entrevista_id)
            detalle = service.obtener_entrevista(entrevista_id) or detalle
        except (ValidationError, AIClientError) as exc:
            error = _mensaje_de_error(exc)

    resumen = detalle.get("resumen")
    preguntas = []
    for pregunta in detalle["preguntas"]:
        evaluacion = pregunta.get("evaluacion")
        preguntas.append(
            {
                **pregunta,
                "banda": _banda(evaluacion["puntaje"] if evaluacion else None),
            }
        )

    return templates.TemplateResponse(
        request,
        "resultado.html",
        {
            "error": error,
            "ctx": _contexto(detalle),
            "recorrido": _recorrido(detalle),
            "resumen": resumen,
            "banda": _banda(resumen["puntaje_general"] if resumen else None),
            "preguntas": preguntas,
        },
    )
