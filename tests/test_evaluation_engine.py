"""Pruebas del motor de evaluación (RF-04, RF-05, RF-12, RNF-04).

Cliente de IA simulado (stub) para no llamar a la API real. Se verifica:
la orquestación, que la respuesta vacía se rechace ANTES de gastar en IA,
que los criterios lleguen al prompt, y que una salida malformada de la IA
se maneje con error controlado.
"""

from __future__ import annotations

import pytest

from app.ai_client import AICallResult
from app.evaluation_engine import EvaluationEngine, construir_prompt_evaluacion
from app.validation import InterviewConfig, ValidationError


def _config(nivel: str = "intermedio") -> InterviewConfig:
    return InterviewConfig(
        rol="Backend Developer",
        tecnologia="Python",
        nivel=nivel,
        idioma="es",
        cantidad_preguntas=3,
        tipo="tecnica",
    )


_EVAL_OK = {
    "puntaje": 80,
    "fortalezas": ["buena estructura", "usó ejemplos"],
    "errores": ["confundió lista con tupla"],
    "omisiones": ["no mencionó inmutabilidad"],
    "respuesta_mejorada": "Una tupla es inmutable, una lista es mutable...",
    "coherente_con_configuracion": True,
}


class _StubClient:
    """Cliente de IA falso: devuelve un JSON fijo y registra lo recibido.

    `llamado` permite verificar que la IA NO se invoca cuando la entrada es
    inválida (ahorro de costo, RNF-04).
    """

    def __init__(self, data: dict):
        self._data = data
        self.llamado = False
        self.ultimo_user_prompt = ""
        self.ultimos_criterios = None

    def generate_json(self, user_prompt, required_fields, system_prompt="", criterios=None):
        self.llamado = True
        self.ultimo_user_prompt = user_prompt
        self.ultimos_criterios = criterios
        return AICallResult(
            data=self._data,
            raw_response="{...}",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="claude-haiku-4-5",
            criterios=list(criterios or []),
        )


def test_evalua_respuesta_valida():
    stub = _StubClient(_EVAL_OK)
    engine = EvaluationEngine(client=stub)
    ev = engine.evaluar_respuesta(
        _config(),
        pregunta="¿Diferencia entre lista y tupla?",
        respuesta="Una lista se puede cambiar y una tupla no.",
        criterios=["precisión", "claridad"],
    )

    assert ev.puntaje == 80
    assert "buena estructura" in ev.fortalezas
    assert ev.coherente_con_configuracion is True
    assert ev.trace.model == "claude-haiku-4-5"  # trazabilidad presente


def test_respuesta_vacia_no_llama_a_la_ia_rnf04():
    stub = _StubClient(_EVAL_OK)
    engine = EvaluationEngine(client=stub)
    with pytest.raises(ValidationError):
        engine.evaluar_respuesta(_config(), "pregunta", "   ")
    assert stub.llamado is False  # no se gastó una llamada a la IA


def test_criterios_llegan_al_cliente_de_ia():
    stub = _StubClient(_EVAL_OK)
    engine = EvaluationEngine(client=stub)
    engine.evaluar_respuesta(
        _config(), "pregunta", "una respuesta válida", criterios=["profundidad"]
    )
    assert stub.ultimos_criterios == ["profundidad"]
    assert "profundidad" in stub.ultimo_user_prompt


def test_salida_puntaje_fuera_de_rango_falla_rf12():
    malo = dict(_EVAL_OK, puntaje=150)  # 150 está fuera de 0–100
    stub = _StubClient(malo)
    engine = EvaluationEngine(client=stub)
    with pytest.raises(ValidationError):
        engine.evaluar_respuesta(_config(), "pregunta", "respuesta válida")


def test_salida_coherente_no_booleano_falla():
    malo = dict(_EVAL_OK, coherente_con_configuracion="sí")
    stub = _StubClient(malo)
    engine = EvaluationEngine(client=stub)
    with pytest.raises(ValidationError):
        engine.evaluar_respuesta(_config(), "pregunta", "respuesta válida")


def test_prompt_incluye_pregunta_y_respuesta():
    prompt = construir_prompt_evaluacion(
        _config(), "¿Qué es REST?", "Es un estilo de arquitectura.", ["claridad"]
    )
    assert "¿Qué es REST?" in prompt
    assert "estilo de arquitectura" in prompt
    assert "claridad" in prompt
