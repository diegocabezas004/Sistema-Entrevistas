"""Pruebas del motor de retroalimentación final (RF-06, RF-07, RNF-04).

Cliente de IA simulado (stub). Se verifica la orquestación, el cálculo local
del promedio, el rechazo de sesión vacía y que las evaluaciones lleguen al prompt.
"""

from __future__ import annotations

import pytest

from app.ai_client import AICallResult
from app.feedback import FeedbackEngine, construir_prompt_resumen
from app.validation import InterviewConfig, ValidationError


def _config() -> InterviewConfig:
    return InterviewConfig(
        rol="Backend Developer",
        tecnologia="Python",
        nivel="intermedio",
        idioma="es",
        cantidad_preguntas=2,
        tipo="mixta",
    )


_RESUMEN_OK = {
    "nivel_estimado": "intermedio",
    "puntaje_general": 72,
    "areas_fuertes": ["algoritmos"],
    "areas_mejora": ["bases de datos"],
    "plan_de_estudio": ["Repasar índices", "Practicar joins"],
}

_ITEMS = [
    {
        "pregunta": "¿Qué es una API REST?",
        "tema": "Web",
        "puntaje": 80,
        "fortalezas": ["clara"],
        "errores": [],
        "omisiones": ["no habló de verbos HTTP"],
    },
    {
        "pregunta": "¿Qué es un índice en SQL?",
        "tema": "Bases de datos",
        "puntaje": 60,
        "fortalezas": [],
        "errores": ["definición imprecisa"],
        "omisiones": [],
    },
]


class _StubClient:
    def __init__(self, data: dict):
        self._data = data
        self.ultimo_user_prompt = ""

    def generate_json(self, user_prompt, required_fields, system_prompt="", criterios=None):
        self.ultimo_user_prompt = user_prompt
        return AICallResult(
            data=self._data,
            raw_response="{...}",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="claude-haiku-4-5",
        )


def test_genera_resumen_valido():
    stub = _StubClient(_RESUMEN_OK)
    engine = FeedbackEngine(client=stub)
    resumen = engine.generar_resumen(_config(), _ITEMS)

    assert resumen.nivel_estimado == "intermedio"
    assert resumen.puntaje_general == 72
    assert "Repasar índices" in resumen.plan_de_estudio
    assert resumen.trace.model == "claude-haiku-4-5"


def test_calcula_promedio_local_como_referencia():
    stub = _StubClient(_RESUMEN_OK)
    engine = FeedbackEngine(client=stub)
    resumen = engine.generar_resumen(_config(), _ITEMS)
    # (80 + 60) / 2 = 70.0, independiente del puntaje_general que dé la IA (72).
    assert resumen.promedio_calculado == 70.0


def test_sesion_vacia_lanza_error_rnf04():
    stub = _StubClient(_RESUMEN_OK)
    engine = FeedbackEngine(client=stub)
    with pytest.raises(ValidationError) as e:
        engine.generar_resumen(_config(), [])
    assert e.value.campo == "items"


def test_salida_nivel_invalido_falla():
    malo = dict(_RESUMEN_OK, nivel_estimado="dios")
    stub = _StubClient(malo)
    engine = FeedbackEngine(client=stub)
    with pytest.raises(ValidationError):
        engine.generar_resumen(_config(), _ITEMS)


def test_prompt_incluye_evaluaciones():
    prompt = construir_prompt_resumen(_config(), _ITEMS)
    assert "API REST" in prompt
    assert "índice en SQL" in prompt
    assert "Puntaje: 80" in prompt
