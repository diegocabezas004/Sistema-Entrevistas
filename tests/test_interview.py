"""Prueba de integración del flujo completo de entrevista (RF-01…RF-10).

Usa storage SQLite real (temporal) y motores de IA simulados (stubs) para
verificar la orquestación de punta a punta sin llamar a la API real:
iniciar → generar preguntas → responder/evaluar → finalizar → historial/trazas.
"""

from __future__ import annotations

import pytest

from app.ai_client import AICallResult
from app.evaluation_engine.engine import Evaluation
from app.feedback.engine import FeedbackSummary
from app.interview import InterviewService
from app.questions_engine.engine import GeneratedQuestion
from app.storage import Database, Repository
from app.validation import InterviewConfig, ValidationError


def _traza() -> AICallResult:
    return AICallResult(
        data={}, raw_response="{}", system_prompt="sys", user_prompt="usr",
        model="claude-haiku-4-5",
    )


class _StubQuestions:
    """Devuelve preguntas incrementales para simular la generación."""

    def __init__(self):
        self.contador = 0

    def generar_pregunta(self, config, preguntas_previas=None):
        self.contador += 1
        return GeneratedQuestion(
            pregunta=f"Pregunta {self.contador}",
            dificultad=config.nivel,
            criterios_evaluados=["claridad"],
            tema="Tema",
            trace=_traza(),
        )


class _StubEvaluations:
    def evaluar_respuesta(self, config, pregunta, respuesta, criterios=None):
        return Evaluation(
            puntaje=75,
            fortalezas=["clara"],
            errores=[],
            omisiones=["falta detalle"],
            respuesta_mejorada="mejor respuesta",
            coherente_con_configuracion=True,
            trace=_traza(),
        )


class _StubFeedback:
    def generar_resumen(self, config, items):
        assert items, "el resumen no debe recibir lista vacía"
        return FeedbackSummary(
            nivel_estimado="junior",
            puntaje_general=75,
            promedio_calculado=75.0,
            areas_fuertes=["fundamentos"],
            areas_mejora=["profundidad"],
            plan_de_estudio=["Practicar más"],
            trace=_traza(),
        )


@pytest.fixture
def service(tmp_path):
    repo = Repository(db=Database(path=str(tmp_path / "flujo.db")))
    return InterviewService(
        repo=repo,
        questions=_StubQuestions(),
        evaluations=_StubEvaluations(),
        feedback=_StubFeedback(),
    )


_CONFIG = {
    "rol": "Backend Developer",
    "tecnologia": "Python",
    "nivel": "junior",
    "idioma": "es",
    "cantidad_preguntas": 2,
    "tipo": "conceptual",
}


def test_flujo_completo_de_entrevista(service):
    # 1. Iniciar
    inicio = service.iniciar_entrevista(_CONFIG)
    eid = inicio["entrevista_id"]
    assert inicio["config"]["nivel"] == "junior"

    # 2. Responder las 2 preguntas
    for _ in range(2):
        pregunta = service.generar_siguiente_pregunta(eid)
        ev = service.responder_pregunta(
            eid, pregunta["pregunta_id"], "Mi respuesta a la pregunta."
        )
        assert ev["puntaje"] == 75

    # 3. Finalizar
    resumen = service.finalizar_entrevista(eid)
    assert resumen["nivel_estimado"] == "junior"
    assert resumen["plan_de_estudio"] == ["Practicar más"]

    # 4. Verificar persistencia y estado
    detalle = service.obtener_entrevista(eid)
    assert detalle["estado"] == "completada"
    assert len(detalle["preguntas"]) == 2
    assert all(p["evaluacion"] is not None for p in detalle["preguntas"])


def test_config_invalida_no_crea_entrevista(service):
    with pytest.raises(ValidationError):
        service.iniciar_entrevista({**_CONFIG, "nivel": "invalido"})


def test_no_se_exceden_las_preguntas_configuradas(service):
    eid = service.iniciar_entrevista(_CONFIG)["entrevista_id"]
    service.generar_siguiente_pregunta(eid)
    service.generar_siguiente_pregunta(eid)
    with pytest.raises(ValidationError):  # la 3ra excede el total (2)
        service.generar_siguiente_pregunta(eid)


def test_finalizar_sin_respuestas_falla_rnf04(service):
    eid = service.iniciar_entrevista(_CONFIG)["entrevista_id"]
    with pytest.raises(ValidationError):
        service.finalizar_entrevista(eid)


def test_responder_pregunta_ajena_falla(service):
    eid = service.iniciar_entrevista(_CONFIG)["entrevista_id"]
    with pytest.raises(ValidationError) as e:
        service.responder_pregunta(eid, 9999, "respuesta")
    assert e.value.campo == "pregunta_id"


def test_historial_y_trazas_se_registran(service):
    eid = service.iniciar_entrevista(_CONFIG)["entrevista_id"]
    p = service.generar_siguiente_pregunta(eid)
    service.responder_pregunta(eid, p["pregunta_id"], "respuesta válida")

    historial = service.listar_historial()
    assert any(h["id"] == eid for h in historial)

    trazas = service.obtener_trazas(eid)
    # Al menos una traza de pregunta y una de evaluación (RF-10).
    tipos = {t["tipo_llamada"] for t in trazas}
    assert "pregunta" in tipos and "evaluacion" in tipos
